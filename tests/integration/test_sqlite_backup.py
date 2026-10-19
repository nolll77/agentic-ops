from __future__ import annotations

import sqlite3

import pytest

from agentic_ops.core.sqlite_backup import (
    SQLiteBackupError,
    backup_runtime_state,
    restore_runtime_state,
    snapshot_sqlite_database,
    verify_backup_set,
    verify_sqlite_database,
)


def test_backup_snapshot_includes_committed_wal_state_and_restores(tmp_path):
    source = tmp_path / "live.db"
    backup = tmp_path / "backups" / "snapshot.db"
    restored = tmp_path / "restore" / "restored.db"
    writer = sqlite3.connect(source)
    writer.execute("PRAGMA journal_mode=WAL")
    writer.execute("CREATE TABLE events(id INTEGER PRIMARY KEY, value TEXT NOT NULL)")
    writer.execute("INSERT INTO events(value) VALUES ('committed-in-wal')")
    writer.commit()

    digest = snapshot_sqlite_database(source, backup)
    assert len(digest) == 64
    verify_sqlite_database(backup)
    with sqlite3.connect(backup) as snapshot:
        assert snapshot.execute("SELECT value FROM events").fetchone() == (
            "committed-in-wal",
        )

    snapshot_sqlite_database(backup, restored)
    with sqlite3.connect(restored) as recovered:
        assert recovered.execute("PRAGMA integrity_check").fetchone() == ("ok",)
        assert recovered.execute("SELECT count(*) FROM events").fetchone() == (1,)
    writer.close()


def test_snapshot_refuses_to_overwrite_existing_destination(tmp_path):
    source = tmp_path / "live.db"
    destination = tmp_path / "backup.db"
    with sqlite3.connect(source) as conn:
        conn.execute("CREATE TABLE data(value TEXT)")
    destination.write_text("keep existing data", encoding="utf-8")

    with pytest.raises(SQLiteBackupError, match="refusing to overwrite"):
        snapshot_sqlite_database(source, destination)
    assert destination.read_text(encoding="utf-8") == "keep existing data"


def test_snapshot_rejects_missing_same_and_corrupt_sources(tmp_path):
    source = tmp_path / "source.db"
    with sqlite3.connect(source) as conn:
        conn.execute("CREATE TABLE data(value TEXT)")

    with pytest.raises(SQLiteBackupError, match="must differ"):
        snapshot_sqlite_database(source, source)
    with pytest.raises(SQLiteBackupError, match="does not exist"):
        snapshot_sqlite_database(tmp_path / "missing.db", tmp_path / "backup.db")

    corrupt = tmp_path / "corrupt.db"
    corrupt.write_bytes(b"not a SQLite database")
    with pytest.raises(SQLiteBackupError, match="cannot verify|integrity"):
        verify_sqlite_database(corrupt)


def test_runtime_backup_set_restores_all_databases_and_signed_evidence(tmp_path):
    from agentic_ops.core.evidence import EvidenceStore

    state = tmp_path / "state"
    state.mkdir()
    databases = {
        "alerts": state / "alerts.db",
        "approvals": state / "approvals.db",
        "quotas": state / "quotas.db",
    }
    for name, path in databases.items():
        with sqlite3.connect(path) as conn:
            conn.execute("CREATE TABLE state(value TEXT NOT NULL)")
            conn.execute("INSERT INTO state(value) VALUES (?)", (f"{name}-committed",))

    evidence = state / "episodes"
    EvidenceStore(str(evidence)).save(
        {
            "episode_id": "EP-RESTORE-DRILL",
            "state_trace": ["DETECTED", "AWAITING_APPROVAL"],
            "payload": "preserved",
        }
    )
    backup = tmp_path / "off-host-backup-copy"
    restored = tmp_path / "isolated-restore"

    manifest = backup_runtime_state(databases, evidence, backup)
    verification = verify_backup_set(backup)
    restore_result = restore_runtime_state(backup, restored)

    assert set(manifest["databases"]) == {"alerts", "approvals", "quotas"}
    assert len(manifest["files"]) == 6
    assert verification["schema_version"] == 1
    assert restore_result["integrity"] == "ok"
    assert restore_result["databases"] == ["alerts", "approvals", "quotas"]
    assert restore_result["evidence_files"] == 3
    for name in databases:
        restored_db = restored / "databases" / f"{name}.sqlite3"
        verify_sqlite_database(restored_db)
        with sqlite3.connect(restored_db) as conn:
            assert conn.execute("SELECT value FROM state").fetchone() == (
                f"{name}-committed",
            )
    restored_evidence = EvidenceStore(str(restored / "evidence"))
    assert restored_evidence.verify_chain()
    assert restored_evidence.load_all_episodes()[0]["payload"] == "preserved"


def test_runtime_backup_set_rejects_destination_reuse_and_tampering(tmp_path):
    from agentic_ops.core.evidence import EvidenceStore

    source = tmp_path / "source.db"
    with sqlite3.connect(source) as conn:
        conn.execute("CREATE TABLE data(value TEXT)")
    evidence = tmp_path / "evidence"
    EvidenceStore(str(evidence)).save({"episode_id": "EP-1", "state_trace": ["DETECTED"]})
    backup = tmp_path / "backup"
    backup_runtime_state({"alerts": source}, evidence, backup)

    with pytest.raises(SQLiteBackupError, match="refusing to overwrite"):
        backup_runtime_state({"alerts": source}, evidence, backup)

    (backup / "evidence" / "EP-1.json").write_text("tampered", encoding="utf-8")
    with pytest.raises(SQLiteBackupError, match="SHA-256 mismatch"):
        verify_backup_set(backup)


def test_runtime_backup_set_rejects_unmanifested_files_and_unsafe_paths(tmp_path):
    from agentic_ops.core.evidence import EvidenceStore

    source = tmp_path / "source.db"
    with sqlite3.connect(source) as conn:
        conn.execute("CREATE TABLE data(value TEXT)")
    evidence = tmp_path / "evidence"
    EvidenceStore(str(evidence)).save({"episode_id": "EP-1", "state_trace": ["DETECTED"]})
    backup = tmp_path / "backup"
    backup_runtime_state({"alerts": source}, evidence, backup)

    (backup / "unexpected.txt").write_text("not in manifest", encoding="utf-8")
    with pytest.raises(SQLiteBackupError, match="unmanifested"):
        verify_backup_set(backup)

    (backup / "unexpected.txt").unlink()
    manifest_path = backup / "manifest.json"
    manifest = manifest_path.read_text(encoding="utf-8")
    manifest_path.write_text(
        manifest.replace('"databases/alerts.sqlite3"', '"../source.db"'),
        encoding="utf-8",
    )
    with pytest.raises(SQLiteBackupError, match="invalid file entry"):
        verify_backup_set(backup)


def test_runtime_backup_set_rejects_symlinked_evidence(tmp_path):
    source = tmp_path / "source.db"
    with sqlite3.connect(source) as conn:
        conn.execute("CREATE TABLE data(value TEXT)")
    evidence = tmp_path / "evidence"
    evidence.mkdir()
    (evidence / "ledger.jsonl").write_text("", encoding="utf-8")
    (evidence / "_index.json").write_text("{}", encoding="utf-8")
    (evidence / "linked.json").symlink_to(source)

    with pytest.raises(SQLiteBackupError, match="symbolic links"):
        backup_runtime_state(
            {"alerts": source}, evidence, tmp_path / "backup"
        )


def test_runtime_backup_set_rejects_destination_nested_in_evidence(tmp_path):
    from agentic_ops.core.evidence import EvidenceStore

    source = tmp_path / "source.db"
    with sqlite3.connect(source) as conn:
        conn.execute("CREATE TABLE data(value TEXT)")
    evidence = tmp_path / "evidence"
    EvidenceStore(str(evidence))

    with pytest.raises(SQLiteBackupError, match="separate from the evidence"):
        backup_runtime_state({"alerts": source}, evidence, evidence / "backup")
