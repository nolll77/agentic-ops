from __future__ import annotations

import argparse
import json
from pathlib import Path

from agentic_ops.core.sqlite_backup import (
    sha256_file,
    snapshot_sqlite_database,
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
    args = parser.parse_args(argv)

    if args.operation == "verify":
        verify_sqlite_database(args.source)
        result = {
            "operation": "verify",
            "database": str(args.source),
            "integrity": "ok",
            "sha256": sha256_file(args.source),
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
