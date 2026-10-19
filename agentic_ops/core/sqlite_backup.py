from __future__ import annotations

import hashlib
import os
import sqlite3
import tempfile
from contextlib import closing
from pathlib import Path


class SQLiteBackupError(RuntimeError):
    pass


def verify_sqlite_database(path: str | Path) -> None:
    database = Path(path)
    if not database.is_file():
        raise SQLiteBackupError(f"SQLite database does not exist: {database}")
    try:
        with closing(
            sqlite3.connect(f"{database.as_uri()}?mode=ro", uri=True, timeout=10)
        ) as conn:
            rows = [row[0] for row in conn.execute("PRAGMA integrity_check")]
    except sqlite3.Error as exc:
        raise SQLiteBackupError(f"cannot verify SQLite database {database}: {exc}") from exc
    if rows != ["ok"]:
        raise SQLiteBackupError(
            f"SQLite integrity check failed for {database}: {'; '.join(rows)}"
        )


def snapshot_sqlite_database(source: str | Path, destination: str | Path) -> str:
    """Create a consistent SQLite snapshot through SQLite's online backup API."""
    source_path = Path(source)
    destination_path = Path(destination)
    if not source_path.is_file():
        raise SQLiteBackupError(f"SQLite source database does not exist: {source_path}")
    if source_path.absolute() == destination_path.absolute():
        raise SQLiteBackupError("source and destination database paths must differ")
    if destination_path.exists():
        raise SQLiteBackupError(f"destination already exists; refusing to overwrite: {destination_path}")

    destination_path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(
        prefix=f".{destination_path.name}.",
        suffix=".tmp",
        dir=destination_path.parent,
    )
    os.close(fd)
    temporary_path = Path(temporary_name)
    try:
        source_uri = f"{source_path.absolute().as_uri()}?mode=ro"
        with closing(sqlite3.connect(source_uri, uri=True, timeout=10)) as source_conn:
            source_integrity = [row[0] for row in source_conn.execute("PRAGMA integrity_check")]
            if source_integrity != ["ok"]:
                raise SQLiteBackupError(
                    f"SQLite source integrity check failed: {'; '.join(source_integrity)}"
                )
            with closing(sqlite3.connect(temporary_path, timeout=10)) as destination_conn:
                source_conn.backup(destination_conn)
                copied_integrity = [
                    row[0] for row in destination_conn.execute("PRAGMA integrity_check")
                ]
                if copied_integrity != ["ok"]:
                    raise SQLiteBackupError(
                        f"SQLite snapshot integrity check failed: {'; '.join(copied_integrity)}"
                    )

        with temporary_path.open("rb") as snapshot:
            os.fsync(snapshot.fileno())
        try:
            os.link(temporary_path, destination_path)
        except FileExistsError as exc:
            raise SQLiteBackupError(
                f"destination already exists; refusing to overwrite: {destination_path}"
            ) from exc
        temporary_path.unlink()
        return sha256_file(destination_path)
    except sqlite3.Error as exc:
        raise SQLiteBackupError(f"SQLite snapshot failed: {exc}") from exc
    finally:
        if temporary_path.exists():
            temporary_path.unlink()


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as content:
        for chunk in iter(lambda: content.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
