from __future__ import annotations

import sqlite3

import pytest

from agentic_ops.core.sqlite_backup import (
    SQLiteBackupError,
    snapshot_sqlite_database,
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
