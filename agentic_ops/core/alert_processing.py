from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from agentic_ops.core.alert_outbox import AlertIngestionWorker, AlertOutbox, AlertRecord
from agentic_ops.core.contracts import ActionType


class AlertMappingError(ValueError):
    pass


class _UniqueKeySafeLoader(yaml.SafeLoader):
    pass


def _construct_unique_mapping(loader: yaml.SafeLoader, node: yaml.MappingNode, deep: bool = False):
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"duplicate key {key!r}",
                key_node.start_mark,
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


_UniqueKeySafeLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_unique_mapping,
)


class _MappingEntry(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    risk_id: str = Field(min_length=1)


class _MappingFile(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: int = Field(ge=1, le=1)
    mappings: dict[str, _MappingEntry]


@dataclass(frozen=True)
class AlertClassification:
    tracking_id: str
    triage_status: str
    alert_name: str | None
    risk_id: str | None
    mapping_version: str
    classified_at: float
    episode_id: str | None = None


class AlertClassifier:
    """Classifies only explicitly mapped Grafana alert names."""

    def __init__(
        self,
        mapping_path: str | Path,
        risk_register_path: str | Path | None = None,
    ):
        path = Path(mapping_path)
        try:
            raw = yaml.load(path.read_text(encoding="utf-8"), Loader=_UniqueKeySafeLoader)
            parsed = _MappingFile.model_validate(raw)
        except (OSError, yaml.YAMLError, ValidationError, TypeError) as exc:
            raise AlertMappingError(f"invalid alert classification map {path}: {exc}") from exc

        if risk_register_path is None:
            risk_register_path = Path(__file__).resolve().parents[1] / "governance" / "risk_register.yaml"
        risk_path = Path(risk_register_path)
        try:
            risk_register = yaml.safe_load(risk_path.read_text(encoding="utf-8"))
        except (OSError, yaml.YAMLError) as exc:
            raise AlertMappingError(f"cannot load risk register {risk_path}: {exc}") from exc
        if not isinstance(risk_register, dict):
            raise AlertMappingError(f"risk register {risk_path} must contain a mapping")

        normalized: dict[str, _MappingEntry] = {}
        for name, entry in parsed.mappings.items():
            key = name.strip()
            if not key or key != name or key in normalized:
                raise AlertMappingError(f"invalid or duplicate alert name in {path}: {name!r}")
            if entry.risk_id not in risk_register:
                raise AlertMappingError(
                    f"alert {name!r} references unknown risk {entry.risk_id!r} in {risk_path}"
                )
            normalized[key] = entry

        canonical = json.dumps(
            {
                "schema_version": parsed.schema_version,
                "mappings": {
                    name: entry.model_dump(mode="json")
                    for name, entry in sorted(normalized.items())
                },
                "risk_register_sha256": hashlib.sha256(
                    json.dumps(risk_register, sort_keys=True, separators=(",", ":")).encode("utf-8")
                ).hexdigest(),
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        self.mappings = normalized
        self.version = hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def classify(self, alert: dict[str, Any]) -> tuple[str, str | None, str | None]:
        labels = alert.get("labels")
        name = labels.get("alertname") if isinstance(labels, dict) else None
        if not isinstance(name, str) or not name.strip():
            return "REVIEW_REQUIRED", None, None
        entry = self.mappings.get(name)
        if entry is None:
            return "REVIEW_REQUIRED", name, None
        return "CLASSIFIED", name, entry.risk_id


class AlertClassificationStore:
    """Durable, idempotent triage results stored alongside the alert outbox."""

    def __init__(self, database_path: str):
        if database_path == ":memory:":
            raise ValueError("alert classification requires a persistent database path")
        self.database_path = database_path
        os.makedirs(os.path.dirname(os.path.abspath(database_path)), exist_ok=True)
        with sqlite3.connect(database_path, timeout=10) as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS alert_classifications(
                    tracking_id TEXT PRIMARY KEY,
                    triage_status TEXT NOT NULL,
                    alert_name TEXT,
                    risk_id TEXT,
                    mapping_version TEXT NOT NULL,
                    classified_at REAL NOT NULL,
                    episode_id TEXT
                )
                """
            )
            columns = {
                row[1] for row in conn.execute("PRAGMA table_info(alert_classifications)")
            }
            if "episode_id" not in columns:
                conn.execute("ALTER TABLE alert_classifications ADD COLUMN episode_id TEXT")

    def record(
        self,
        tracking_id: str,
        triage_status: str,
        alert_name: str | None,
        risk_id: str | None,
        mapping_version: str,
        classified_at: float,
    ) -> AlertClassification:
        with sqlite3.connect(self.database_path, timeout=10) as conn:
            conn.execute(
                """INSERT OR IGNORE INTO alert_classifications
                   (tracking_id, triage_status, alert_name, risk_id, mapping_version, classified_at)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    tracking_id,
                    triage_status,
                    alert_name,
                    risk_id,
                    mapping_version,
                    classified_at,
                ),
            )
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM alert_classifications WHERE tracking_id=?",
                (tracking_id,),
            ).fetchone()
        if row is None:
            raise RuntimeError(f"failed to persist alert classification {tracking_id}")
        return self._from_row(row)

    def get(self, tracking_id: str) -> AlertClassification | None:
        with sqlite3.connect(self.database_path, timeout=10) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM alert_classifications WHERE tracking_id=?",
                (tracking_id,),
            ).fetchone()
        return self._from_row(row) if row else None

    def set_episode_id(self, tracking_id: str, episode_id: str) -> None:
        with sqlite3.connect(self.database_path, timeout=10) as conn:
            updated = conn.execute(
                """UPDATE alert_classifications SET episode_id=?
                   WHERE tracking_id=? AND triage_status='CLASSIFIED'
                     AND (episode_id IS NULL OR episode_id=?)""",
                (episode_id, tracking_id, episode_id),
            )
            if updated.rowcount != 1:
                raise RuntimeError(
                    f"cannot associate episode {episode_id!r} with alert {tracking_id!r}"
                )

    @staticmethod
    def _from_row(row: sqlite3.Row) -> AlertClassification:
        return AlertClassification(
            tracking_id=row["tracking_id"],
            triage_status=row["triage_status"],
            alert_name=row["alert_name"],
            risk_id=row["risk_id"],
            mapping_version=row["mapping_version"],
            classified_at=row["classified_at"],
            episode_id=row["episode_id"],
        )


class AlertTriageWorker:
    """Consumes accepted alerts and persists deterministic triage only."""

    def __init__(
        self,
        outbox: AlertOutbox,
        classifier: AlertClassifier,
        result_store: AlertClassificationStore,
        worker_id: str,
        incident_handler: Any = None,
        *,
        max_attempts: int = 5,
        lease_seconds: int = 60,
    ):
        self.classifier = classifier
        self.result_store = result_store
        self.incident_handler = incident_handler
        self.worker = AlertIngestionWorker(
            outbox,
            worker_id,
            self._classify_and_persist,
            max_attempts=max_attempts,
            lease_seconds=lease_seconds,
        )

    def run_once(self) -> bool:
        return self.worker.run_once()

    def _classify_and_persist(self, record: AlertRecord) -> None:
        status, alert_name, risk_id = self.classifier.classify(record.payload)
        result = self.result_store.record(
            record.tracking_id,
            status,
            alert_name,
            risk_id,
            self.classifier.version,
            time.time(),
        )
        if result.triage_status != "CLASSIFIED" or self.incident_handler is None:
            return
        if result.episode_id:
            return
        episode_id = self.incident_handler(record, result.risk_id)
        if not isinstance(episode_id, str) or not episode_id:
            raise RuntimeError(
                f"incident handler returned no episode for alert {record.tracking_id}"
            )
        self.result_store.set_episode_id(record.tracking_id, episode_id)


class AlertIncidentProcessor:
    """Builds an investigation episode through the core orchestrator only."""

    def __init__(self, orchestrator: Any):
        self.orchestrator = orchestrator

    def __call__(self, record: AlertRecord, risk_id: str | None) -> str:
        if not risk_id:
            raise ValueError("a classified alert must have a risk_id")
        episode = self.orchestrator.run(
            risk_id,
            signal_id=record.tracking_id,
            forced_action=ActionType.INVESTIGATE,
            idempotency_key=record.tracking_id,
        )
        if episode is None:
            existing = self.orchestrator.evidence_store.find_episode_by_signal_id(
                record.tracking_id
            )
            if existing is None:
                raise RuntimeError(
                    f"orchestrator did not persist an episode for {record.tracking_id}"
                )
            return str(existing["episode_id"])
        return str(episode.episode_id)
