from __future__ import annotations

import argparse
import json
from pathlib import Path

from agentic_ops.core.sqlite_backup import (
    sha256_file,
    backup_runtime_state,
    restore_runtime_state,
    snapshot_sqlite_database,
    verify_backup_set,
    verify_sqlite_database,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Create, restore, or verify a consistent SQLite database snapshot."
    )
    subparsers = parser.add_subparsers(dest="operation", required=True)
    for operation in ("backup", "restore"):
        command = subparsers.add_parser(operation)
        command.add_argument("--source", required=True, type=Path)
        command.add_argument("--destination", required=True, type=Path)
    verify = subparsers.add_parser("verify")
    verify.add_argument("source", type=Path)
    backup_set = subparsers.add_parser(
        "backup-set",
        help="snapshot named SQLite databases and an evidence ledger together",
    )
    backup_set.add_argument(
        "--database",
        action="append",
        required=True,
        metavar="NAME=PATH",
        help="database name and source path; repeat for each runtime database",
    )
    backup_set.add_argument("--evidence-dir", required=True, type=Path)
    backup_set.add_argument("--destination", required=True, type=Path)
    verify_set = subparsers.add_parser("verify-set")
    verify_set.add_argument("source", type=Path)
    restore_set = subparsers.add_parser("restore-set")
    restore_set.add_argument("--source", required=True, type=Path)
    restore_set.add_argument("--destination", required=True, type=Path)
    args = parser.parse_args(argv)

    if args.operation == "verify":
        verify_sqlite_database(args.source)
        result = {
            "operation": "verify",
            "database": str(args.source),
            "integrity": "ok",
            "sha256": sha256_file(args.source),
        }
    elif args.operation == "backup-set":
        database_paths: dict[str, Path] = {}
        for definition in args.database:
            name, separator, raw_path = definition.partition("=")
            if not separator or not name or not raw_path or name in database_paths:
                parser.error("--database must be a unique NAME=PATH value")
            database_paths[name] = Path(raw_path)
        result = {
            "operation": "backup-set",
            "destination": str(args.destination),
            **backup_runtime_state(
                database_paths,
                args.evidence_dir,
                args.destination,
            ),
        }
    elif args.operation == "verify-set":
        manifest = verify_backup_set(args.source)
        result = {
            "operation": "verify-set",
            "source": str(args.source),
            "databases": sorted(manifest["databases"]),
            "files_verified": len(manifest["files"]),
            "integrity": "ok",
        }
    elif args.operation == "restore-set":
        result = {
            "operation": "restore-set",
            "source": str(args.source),
            "destination": str(args.destination),
            **restore_runtime_state(args.source, args.destination),
        }
    else:
        digest = snapshot_sqlite_database(args.source, args.destination)
        result = {
            "operation": args.operation,
            "source": str(args.source),
            "destination": str(args.destination),
            "integrity": "ok",
            "sha256": digest,
        }
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
