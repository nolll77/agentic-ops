from __future__ import annotations

import hashlib
import json
import logging
import os
import sqlite3
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, Callable, Protocol

log = logging.getLogger(__name__)


class LostLeaseError(RuntimeError):
    pass


@dataclass(frozen=True)
class AlertRecord:
    tracking_id: str
    fingerprint: str
    payload: dict[str, Any]
    status: str
    attempts: int
    created_at: float
    last_error: str | None = None


class AlertHandler(Protocol):
    def __call__(self, alert: AlertRecord) -> None: ...


def semantic_fingerprint(alert: dict[str, Any]) -> str:
    labels = alert.get("labels")
    stable = {
        "status": alert.get("status", ""),
        "labels": labels if isinstance(labels, dict) else {},
        "startsAt": alert.get("startsAt", ""),
        "endsAt": alert.get("endsAt", ""),
        "fingerprint": alert.get("fingerprint", ""),
    }
    if not any(stable.values()):
        stable["payload"] = alert
    canonical = json.dumps(stable, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class AlertOutbox:
    """Transactional single-node outbox; use a qualified shared database for HA."""

    def __init__(
        self,
        path: str,
        clock: Callable[[], float] = time.time,
        dedup_window_seconds: int = 300,
    ):
        if dedup_window_seconds < 1:
            raise ValueError("deduplication window must be positive")
        self.path = path
        self.clock = clock
        self.dedup_window_seconds = dedup_window_seconds
        if path != ":memory:":
            os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        conn = self._connection()
        try:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=FULL")
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS alerts (
                    tracking_id TEXT PRIMARY KEY,
                    fingerprint TEXT NOT NULL UNIQUE,
                    payload TEXT NOT NULL,
                    status TEXT NOT NULL,
                    attempts INTEGER NOT NULL DEFAULT 0,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL,
                    available_at REAL NOT NULL,
                    lease_owner TEXT,
                    lease_expires_at REAL,
                    last_error TEXT
                );
                CREATE INDEX IF NOT EXISTS alerts_ready
                    ON alerts(status, available_at, lease_expires_at);
                CREATE TABLE IF NOT EXISTS alert_dedup (
                    semantic_fingerprint TEXT PRIMARY KEY,
                    tracking_id TEXT NOT NULL,
                    expires_at REAL NOT NULL
                );
                """
            )
        finally:
            conn.close()

    def _connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path, timeout=10, isolation_level=None)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA busy_timeout=10000")
        return conn

    @contextmanager
    def _transaction(self):
        conn = self._connection()
        try:
            conn.execute("BEGIN IMMEDIATE")
            yield conn
            conn.execute("COMMIT")
        except BaseException:
            if conn.in_transaction:
                conn.execute("ROLLBACK")
            raise
        finally:
            conn.close()

    def enqueue(self, alerts: list[dict[str, Any]]) -> tuple[list[AlertRecord], int]:
        now = self.clock()
        accepted: list[AlertRecord] = []
        duplicates = 0
        with self._transaction() as conn:
            for alert in alerts:
                fingerprint = semantic_fingerprint(alert)
                payload = json.dumps(alert, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
                prior = conn.execute(
                    """SELECT tracking_id FROM alert_dedup
                       WHERE semantic_fingerprint=? AND expires_at > ?""",
                    (fingerprint, now),
                ).fetchone()
                if prior is not None:
                    row = conn.execute(
                        "SELECT * FROM alerts WHERE tracking_id=?", (prior["tracking_id"],)
                    ).fetchone()
                    if row is not None:
                        duplicates += 1
                        conn.execute(
                            "UPDATE alert_dedup SET expires_at=? WHERE semantic_fingerprint=?",
                            (now + self.dedup_window_seconds, fingerprint),
                        )
                        accepted.append(self._record(row))
                        continue

                tracking_id = str(uuid.uuid4())
                storage_fingerprint = fingerprint
                if conn.execute(
                    "SELECT 1 FROM alerts WHERE fingerprint=?", (storage_fingerprint,)
                ).fetchone():
                    storage_fingerprint = f"{fingerprint}:{tracking_id}"
                conn.execute(
                    """INSERT OR IGNORE INTO alerts
                       (tracking_id, fingerprint, payload, status, attempts, created_at,
                        updated_at, available_at)
                       VALUES (?, ?, ?, 'RECEIVED', 0, ?, ?, ?)""",
                    (tracking_id, storage_fingerprint, payload, now, now, now),
                )
                conn.execute(
                    """INSERT INTO alert_dedup(semantic_fingerprint, tracking_id, expires_at)
                       VALUES (?, ?, ?) ON CONFLICT(semantic_fingerprint) DO UPDATE SET
                       tracking_id=excluded.tracking_id, expires_at=excluded.expires_at""",
                    (fingerprint, tracking_id, now + self.dedup_window_seconds),
                )
                row = conn.execute(
                    "SELECT * FROM alerts WHERE tracking_id=?", (tracking_id,)
                ).fetchone()
                accepted.append(self._record(row))
        return accepted, duplicates

    def get(self, tracking_id: str) -> AlertRecord | None:
        conn = self._connection()
        try:
            row = conn.execute(
                "SELECT * FROM alerts WHERE tracking_id = ?", (tracking_id,)
            ).fetchone()
        finally:
            conn.close()
        return self._record(row) if row else None

    def claim(self, worker_id: str, lease_seconds: int = 60) -> AlertRecord | None:
        if not worker_id or lease_seconds < 1:
            raise ValueError("worker_id and a positive lease duration are required")
        now = self.clock()
        with self._transaction() as conn:
            row = conn.execute(
                """SELECT * FROM alerts
                   WHERE (status IN ('RECEIVED', 'RETRY') AND available_at <= ?)
                      OR (status = 'PROCESSING' AND lease_expires_at <= ?)
                   ORDER BY created_at LIMIT 1""",
                (now, now),
            ).fetchone()
            if row is None:
                return None
            updated = conn.execute(
                """UPDATE alerts SET status='PROCESSING', attempts=attempts+1,
                       lease_owner=?, lease_expires_at=?, updated_at=?
                   WHERE tracking_id=? AND
                     (status IN ('RECEIVED', 'RETRY') OR
                      (status='PROCESSING' AND lease_expires_at <= ?))""",
                (worker_id, now + lease_seconds, now, row["tracking_id"], now),
            )
            if updated.rowcount != 1:
                return None
            claimed = conn.execute(
                "SELECT * FROM alerts WHERE tracking_id=?", (row["tracking_id"],)
            ).fetchone()
            return self._record(claimed)

    def complete(self, tracking_id: str, worker_id: str) -> None:
        self._finish_lease(tracking_id, worker_id, "COMPLETED", None, None)

    def retry(
        self,
        tracking_id: str,
        worker_id: str,
        error: str,
        *,
        max_attempts: int = 5,
        base_delay_seconds: int = 2,
    ) -> str:
        if max_attempts < 1 or base_delay_seconds < 0:
            raise ValueError("max_attempts must be positive and retry delay non-negative")
        now = self.clock()
        with self._transaction() as conn:
            row = self._owned_lease(conn, tracking_id, worker_id)
            terminal = row["attempts"] >= max_attempts
            status = "DEAD" if terminal else "RETRY"
            delay = min(base_delay_seconds * 2 ** max(row["attempts"] - 1, 0), 300)
            conn.execute(
                """UPDATE alerts SET status=?, last_error=?, updated_at=?,
                       available_at=?, lease_owner=NULL, lease_expires_at=NULL
                   WHERE tracking_id=?""",
                (status, error[:1000], now, now + delay, tracking_id),
            )
            return status

    def _finish_lease(
        self, tracking_id: str, worker_id: str, status: str, error: str | None, available_at: float | None
    ) -> None:
        now = self.clock()
        with self._transaction() as conn:
            self._owned_lease(conn, tracking_id, worker_id)
            conn.execute(
                """UPDATE alerts SET status=?, last_error=?, updated_at=?,
                       available_at=COALESCE(?, available_at), lease_owner=NULL,
                       lease_expires_at=NULL WHERE tracking_id=?""",
                (status, error, now, available_at, tracking_id),
            )

    @staticmethod
    def _owned_lease(conn: sqlite3.Connection, tracking_id: str, worker_id: str) -> sqlite3.Row:
        row = conn.execute(
            "SELECT * FROM alerts WHERE tracking_id=? AND status='PROCESSING' AND lease_owner=?",
            (tracking_id, worker_id),
        ).fetchone()
        if row is None:
            raise LostLeaseError(f"worker {worker_id!r} does not own alert lease {tracking_id!r}")
        return row

    @staticmethod
    def _record(row: sqlite3.Row) -> AlertRecord:
        return AlertRecord(
            tracking_id=row["tracking_id"],
            fingerprint=row["fingerprint"],
            payload=json.loads(row["payload"]),
            status=row["status"],
            attempts=row["attempts"],
            created_at=row["created_at"],
            last_error=row["last_error"],
        )


class AlertIngestionWorker:
    def __init__(
        self,
        outbox: AlertOutbox,
        worker_id: str,
        handler: AlertHandler,
        *,
        max_attempts: int = 5,
        lease_seconds: int = 60,
    ):
        self.outbox = outbox
        self.worker_id = worker_id
        self.handler = handler
        self.max_attempts = max_attempts
        self.lease_seconds = lease_seconds
        if max_attempts < 1 or lease_seconds < 1:
            raise ValueError("max_attempts and lease_seconds must be positive")

    def run_once(self) -> bool:
        record = self.outbox.claim(self.worker_id, self.lease_seconds)
        if record is None:
            return False
        try:
            self.handler(record)
        except Exception as exc:
            status = self.outbox.retry(
                record.tracking_id,
                self.worker_id,
                type(exc).__name__,
                max_attempts=self.max_attempts,
            )
            log.exception(
                "alert processing failed tracking_id=%s state=%s",
                record.tracking_id,
                status,
            )
            return True
        self.outbox.complete(record.tracking_id, self.worker_id)
        return True
