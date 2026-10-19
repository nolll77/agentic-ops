from __future__ import annotations

from datetime import datetime, timezone

import pytest

from agentic_ops.core.local_inventory import (
    InventoryLoadError,
    LocalInventory,
    UnavailableInventory,
    inventory_from_environment,
)


def _inventory_text(generated_at: str) -> str:
    return f"""schema_version: 1
generated_at: {generated_at}
max_age_seconds: 3600
targets:
  service/prediction-api:
    replicas: 3
    criticality: high
"""


def test_local_inventory_is_an_exact_allowlist_and_exposes_real_attributes(tmp_path):
    now = datetime.now(timezone.utc)
    path = tmp_path / "inventory.yaml"
    path.write_text(_inventory_text(now.isoformat()), encoding="utf-8")

    inventory = LocalInventory.load(path)

    assert inventory.describe("service/prediction-api").model_dump() == {
        "replicas": 3,
        "criticality": "high",
    }
    assert inventory.describe("service/prediction-api/extra") is None
    assert inventory.describe("service/other") is None
    assert len(inventory.version) == 64


@pytest.mark.parametrize(
    "content",
    [
        "schema_version: 1\ngenerated_at: [not, a, timestamp]\n",
        "schema_version: 1\ngenerated_at: 2026-10-19T12:00:00Z\nmax_age_seconds: 3600\ntargets: {}\n",
        """schema_version: 1
generated_at: 2026-10-19T12:00:00Z
max_age_seconds: 3600
targets:
  service/x:
    replicas: 0
    criticality: low
""",
        """schema_version: 1
generated_at: 2026-10-19T12:00:00Z
max_age_seconds: 3600
targets:
  service/x:
    replicas: 1
    criticality: medium
""",
        """schema_version: 1
generated_at: 2026-10-19T12:00:00Z
max_age_seconds: 3600
targets:
  service/x:
    replicas: 1
    criticality: low
  service/x:
    replicas: 2
    criticality: high
""",
        """schema_version: 1
generated_at: 2026-10-19T12:00:00Z
max_age_seconds: 3600
targets:
  " service/x":
    replicas: 1
    criticality: low
""",
    ],
)
def test_invalid_inventory_fails_to_load(tmp_path, content):
    path = tmp_path / "inventory.yaml"
    path.write_text(content, encoding="utf-8")

    with pytest.raises(InventoryLoadError):
        LocalInventory.load(path)


def test_stale_inventory_is_rejected_at_load_and_expires_at_runtime(tmp_path):
    now = [datetime(2026, 10, 19, 12, 0, tzinfo=timezone.utc).timestamp()]
    path = tmp_path / "inventory.yaml"
    path.write_text(_inventory_text("2026-10-19T10:00:00Z"), encoding="utf-8")

    with pytest.raises(InventoryLoadError, match="stale"):
        LocalInventory.load(path, clock=lambda: now[0])

    path.write_text(
        """schema_version: 1
generated_at: 2026-10-19T11:59:00Z
max_age_seconds: 3600
targets:
  service/prediction-api:
    replicas: 3
    criticality: high
""",
        encoding="utf-8",
    )
    inventory = LocalInventory.load(path, clock=lambda: now[0])
    assert inventory.describe("service/prediction-api") is not None
    now[0] += 3601
    assert inventory.describe("service/prediction-api") is None
    assert inventory.failure_reason == "local inventory is stale"


def test_inventory_requires_timezone_and_rejects_future_timestamp(tmp_path):
    path = tmp_path / "inventory.yaml"
    path.write_text(
        _inventory_text("2026-10-19T12:00:00"),
        encoding="utf-8",
    )
    with pytest.raises(InventoryLoadError):
        LocalInventory.load(path)

    path.write_text(
        _inventory_text("2999-10-19T12:00:00Z"),
        encoding="utf-8",
    )
    with pytest.raises(InventoryLoadError, match="future"):
        LocalInventory.load(path, clock=lambda: 1_798_800_000)


def test_missing_environment_configuration_fails_closed():
    inventory = inventory_from_environment({})

    assert isinstance(inventory, UnavailableInventory)
    assert inventory.describe("anything") is None
    assert inventory.failure_reason == "no authoritative local inventory is configured"


def test_configured_missing_inventory_is_an_explicit_error(tmp_path):
    with pytest.raises(InventoryLoadError, match="cannot load"):
        inventory_from_environment(
            {"AGENTIC_OPS_INVENTORY_PATH": str(tmp_path / "missing.yaml")}
        )


def test_inventory_reloading_after_file_change_replaces_allowlist_and_version(tmp_path):
    path = tmp_path / "inventory.yaml"
    first_time = datetime.now(timezone.utc)
    path.write_text(
        f"""schema_version: 1
generated_at: {first_time.isoformat()}
max_age_seconds: 3600
targets:
  service/old:
    replicas: 1
    criticality: low
""",
        encoding="utf-8",
    )
    first = LocalInventory.load(path)
    assert first.describe("service/old") is not None

    second_time = datetime.now(timezone.utc)
    path.write_text(
        f"""schema_version: 1
generated_at: {second_time.isoformat()}
max_age_seconds: 3600
targets:
  service/new:
    replicas: 2
    criticality: high
""",
        encoding="utf-8",
    )
    second = LocalInventory.load(path)

    assert second.version != first.version
    assert first.describe("service/old") is None
    assert first.failure_reason == "local inventory changed since it was loaded"
    assert second.describe("service/old") is None
    assert second.describe("service/new").replicas == 2
