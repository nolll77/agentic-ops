from __future__ import annotations

import hashlib
import os
import json
import re
import sqlite3
import shutil
import tempfile
import time
from contextlib import closing
from pathlib import Path
from typing import Any


class SQLiteBackupError(RuntimeError):
    pass


_BACKUP_SET_SCHEMA = 1


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


def _evidence_files(root: Path) -> list[Path]:
    if not root.is_dir():
        raise SQLiteBackupError(f"evidence directory does not exist: {root}")
    files: list[Path] = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise SQLiteBackupError(f"symbolic links are not allowed in evidence backup: {path}")
        if path.is_file():
            files.append(path)
    required = {"ledger.jsonl", "_index.json"}
    if not required.issubset({path.name for path in files}):
        raise SQLiteBackupError(
            f"evidence directory must contain {', '.join(sorted(required))}"
        )
    return files


def _verify_evidence_chain(path: Path) -> None:
    from agentic_ops.core.evidence import EvidenceStore

    store = EvidenceStore(str(path))
    if not store.verify_chain():
        raise SQLiteBackupError(f"evidence ledger verification failed: {path}")


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def verify_backup_set(source: str | Path) -> dict[str, Any]:
    """Verify backup-set hashes, SQLite integrity, and the signed evidence chain."""
    root = Path(source)
    manifest_path = root / "manifest.json"
    if manifest_path.is_symlink() or not manifest_path.is_file():
        raise SQLiteBackupError(f"backup-set manifest does not exist: {manifest_path}")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SQLiteBackupError(f"cannot read backup-set manifest: {exc}") from exc
    if not isinstance(manifest, dict) or manifest.get("schema_version") != _BACKUP_SET_SCHEMA:
        raise SQLiteBackupError("unsupported backup-set schema version")

    files = manifest.get("files")
    if not isinstance(files, dict) or not files:
        raise SQLiteBackupError("backup-set manifest contains no file hashes")
    root_resolved = root.resolve()
    for relative, expected in files.items():
        if (
            not isinstance(relative, str)
            or not relative
            or Path(relative).is_absolute()
            or "\\" in relative
            or ".." in Path(relative).parts
            or not isinstance(expected, str)
            or not re.fullmatch(r"[a-f0-9]{64}", expected)
        ):
            raise SQLiteBackupError(f"invalid file entry in backup-set manifest: {relative!r}")
        candidate = root / relative
        cursor = root
        for part in Path(relative).parts:
            cursor = cursor / part
            if cursor.is_symlink():
                raise SQLiteBackupError(f"symbolic links are not allowed in backup set: {relative}")
        file_path = candidate.resolve()
        if not file_path.is_relative_to(root_resolved) or not file_path.is_file():
            raise SQLiteBackupError(f"backup-set file is missing or unsafe: {relative}")
        if sha256_file(file_path) != expected:
            raise SQLiteBackupError(f"backup-set SHA-256 mismatch: {relative}")

    databases = manifest.get("databases")
    if not isinstance(databases, dict) or not databases:
        raise SQLiteBackupError("backup-set manifest contains no databases")
    for name, relative in databases.items():
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]{0,63}", name):
            raise SQLiteBackupError(f"invalid database name in manifest: {name!r}")
        if (
            not isinstance(relative, str)
            or relative != f"databases/{name}.sqlite3"
            or files.get(relative) is None
        ):
            raise SQLiteBackupError(f"database is not protected by a manifest hash: {name}")
        verify_sqlite_database(root / relative)
    evidence_directory = manifest.get("evidence_directory")
    if not isinstance(evidence_directory, str) or not evidence_directory:
        raise SQLiteBackupError("backup-set manifest has no evidence directory")
    evidence_prefix = f"{evidence_directory}/"
    evidence_files = {
        path.removeprefix(evidence_prefix)
        for path in files
        if path.startswith(evidence_prefix)
    }
    if not {"ledger.jsonl", "_index.json"}.issubset(evidence_files):
        raise SQLiteBackupError("evidence directory is not protected by manifest hashes")
    if set(files) != set(databases.values()) | {
        f"{evidence_directory}/{relative}" for relative in evidence_files
    }:
        raise SQLiteBackupError("backup-set manifest contains unclassified files")

    actual_files = {
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file() or path.is_symlink()
    } - {"manifest.json"}
    if actual_files != set(files):
        raise SQLiteBackupError("backup set contains missing or unmanifested files")
    _verify_evidence_chain(root / evidence_directory)
    return manifest


def backup_runtime_state(
    database_paths: dict[str, str | Path],
    evidence_directory: str | Path,
    destination: str | Path,
) -> dict[str, Any]:
    """Snapshot runtime SQLite databases and evidence into one immutable backup set.

    Callers must stop or quiesce all writers first; SQLite snapshots are
    individually consistent, but this function cannot create a cross-database
    transaction boundary.
    """
    if not database_paths:
        raise SQLiteBackupError("at least one SQLite database is required")
    dest = Path(destination).absolute()
    if dest.exists():
        raise SQLiteBackupError(f"destination already exists; refusing to overwrite: {dest}")
    for name, source in database_paths.items():
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]{0,63}", name):
            raise SQLiteBackupError(f"invalid database name: {name!r}")
        if dest == Path(source).absolute() or dest in Path(source).absolute().parents:
            raise SQLiteBackupError("backup destination must not contain a source database")

    evidence = Path(evidence_directory).absolute()
    if dest == evidence or dest in evidence.parents or evidence in dest.parents:
        raise SQLiteBackupError("backup destination must be separate from the evidence source")
    evidence_sources = _evidence_files(evidence)
    for source in database_paths.values():
        if not Path(source).is_file():
            raise SQLiteBackupError(f"SQLite source database does not exist: {source}")

    started = time.perf_counter()
    dest.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f".{dest.name}.", dir=dest.parent))
    try:
        db_files: dict[str, str] = {}
        for name, source in sorted(database_paths.items()):
            relative = f"databases/{name}.sqlite3"
            snapshot_sqlite_database(source, staging / relative)
            db_files[name] = relative

        copied_evidence = staging / "evidence"
        shutil.copytree(evidence, copied_evidence)
        copied_evidence_files = _evidence_files(copied_evidence)
        files = {
            str(path.relative_to(staging)): sha256_file(path)
            for path in [*(staging / relative for relative in db_files.values()), *copied_evidence_files]
        }
        manifest: dict[str, Any] = {
            "schema_version": _BACKUP_SET_SCHEMA,
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "databases": db_files,
            "evidence_directory": "evidence",
            "files": files,
            "duration_seconds": round(time.perf_counter() - started, 6),
        }
        _write_json(staging / "manifest.json", manifest)
        verify_backup_set(staging)
        os.rename(staging, dest)
        return manifest
    except BaseException:
        shutil.rmtree(staging, ignore_errors=True)
        raise


def restore_runtime_state(
    source: str | Path, destination: str | Path
) -> dict[str, Any]:
    """Verify a backup set and restore it atomically into a previously absent path."""
    started = time.perf_counter()
    root = Path(source).absolute()
    dest = Path(destination).absolute()
    if root == dest or root in dest.parents:
        raise SQLiteBackupError("restore destination must be separate from the backup set")
    if dest.exists():
        raise SQLiteBackupError(f"destination already exists; refusing to overwrite: {dest}")
    manifest = verify_backup_set(root)
    dest.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f".{dest.name}.", dir=dest.parent))
    try:
        shutil.copytree(root, staging, dirs_exist_ok=True)
        verify_backup_set(staging)
        os.rename(staging, dest)
        return {
            "databases": sorted(manifest["databases"]),
            "evidence_files": len(manifest["files"]) - len(manifest["databases"]),
            "duration_seconds": round(time.perf_counter() - started, 6),
            "integrity": "ok",
        }
    except BaseException:
        shutil.rmtree(staging, ignore_errors=True)
        raise
