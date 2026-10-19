from __future__ import annotations

import hashlib
import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from agentic_ops.core.policy_engine import TargetInfo


class InventoryLoadError(ValueError):
    pass


class _UniqueKeySafeLoader(yaml.SafeLoader):
    pass


def _construct_unique_mapping(
    loader: yaml.SafeLoader, node: yaml.MappingNode, deep: bool = False
) -> dict[Any, Any]:
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


class _InventoryTarget(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    replicas: int = Field(ge=1)
    criticality: str

    @model_validator(mode="after")
    def validate_criticality(self) -> _InventoryTarget:
        if self.criticality not in {"low", "high"}:
            raise ValueError("criticality must be 'low' or 'high'")
        return self


class _InventoryFile(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: int = Field(ge=1, le=1)
    generated_at: datetime
    max_age_seconds: int = Field(ge=1, le=2_592_000)
    targets: dict[str, _InventoryTarget] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_generated_at(self) -> _InventoryFile:
        if self.generated_at.tzinfo is None or self.generated_at.utcoffset() is None:
            raise ValueError("generated_at must include a timezone")
        return self


class UnavailableInventory:
    """Fail-closed inventory used when no authoritative source is configured."""

    failure_reason = "no authoritative local inventory is configured"

    def describe(self, target: str) -> None:
        return None


class LocalInventory:
    """Exact-name local allowlist with an enforced freshness window."""

    def __init__(
        self,
        targets: dict[str, _InventoryTarget],
        generated_at: datetime,
        max_age_seconds: int,
        version: str,
        clock: Callable[[], float] = time.time,
    ):
        self._targets = targets
        self.generated_at = generated_at.astimezone(timezone.utc)
        self.max_age_seconds = max_age_seconds
        self.version = version
        self._clock = clock

    @property
    def failure_reason(self) -> str | None:
        generated = self.generated_at.timestamp()
        now = self._clock()
        if generated > now + 60:
            return "local inventory timestamp is in the future"
        if now - generated > self.max_age_seconds:
            return "local inventory is stale"
        return None

    def describe(self, target: str) -> TargetInfo | None:
        if self.failure_reason is not None:
            return None
        entry = self._targets.get(target)
        if entry is None:
            return None
        return TargetInfo(replicas=entry.replicas, criticality=entry.criticality)

    @classmethod
    def load(
        cls,
        path: str | Path,
        *,
        clock: Callable[[], float] = time.time,
    ) -> LocalInventory:
        inventory_path = Path(path)
        try:
            raw = yaml.load(
                inventory_path.read_text(encoding="utf-8"),
                Loader=_UniqueKeySafeLoader,
            )
            parsed = _InventoryFile.model_validate(raw)
        except (OSError, yaml.YAMLError, ValidationError, TypeError) as exc:
            raise InventoryLoadError(
                f"cannot load authoritative inventory {inventory_path}: {exc}"
            ) from exc

        for target in parsed.targets:
            if not target or target.strip() != target or not re.fullmatch(
                r"[A-Za-z0-9][A-Za-z0-9._:/-]{0,254}", target
            ):
                raise InventoryLoadError(
                    f"inventory target must be a non-empty exact identifier: {target!r}"
                )

        inventory = cls(
            parsed.targets,
            parsed.generated_at,
            parsed.max_age_seconds,
            hashlib.sha256(
                json.dumps(raw, sort_keys=True, default=str, separators=(",", ":")).encode()
            ).hexdigest(),
            clock,
        )
        if inventory.failure_reason:
            raise InventoryLoadError(
                f"cannot load authoritative inventory {inventory_path}: "
                f"{inventory.failure_reason}"
            )
        return inventory


def inventory_from_environment(
    environ: dict[str, str] | None = None,
) -> LocalInventory | UnavailableInventory:
    env = os.environ if environ is None else environ
    path = env.get("AGENTIC_OPS_INVENTORY_PATH")
    if not path:
        return UnavailableInventory()
    return LocalInventory.load(path)
