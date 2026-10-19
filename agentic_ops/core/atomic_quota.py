from __future__ import annotations

import hashlib
import os
import sqlite3
import time
import uuid


class AtomicQuotaManager:
    """Atomic sliding-window reservations shared by processes using the same SQLite file."""

    def __init__(self, path: str, clock=time.time):
        self.path = path
        self.clock = clock
        if path != ":memory:":
            os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        conn = self._connect()
        try:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=FULL")
            conn.execute(
                """CREATE TABLE IF NOT EXISTS quota_reservations (
                       scope TEXT NOT NULL,
                       reservation_key TEXT NOT NULL,
                       reserved_at REAL NOT NULL,
                       PRIMARY KEY(scope, reservation_key)
                   )"""
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS quota_reservations_time ON quota_reservations(scope, reserved_at)"
            )
        finally:
            conn.close()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path, timeout=10, isolation_level=None)
        conn.execute("PRAGMA busy_timeout=10000")
        return conn

    def reserve(
        self,
        action: str,
        target: str,
        limit: int,
        window_seconds: int,
        reservation_key: str | None = None,
    ) -> bool:
        if limit < 1 or window_seconds < 1:
            raise ValueError("quota limit and window must be positive")
        now = self.clock()
        key = hashlib.sha256((reservation_key or str(uuid.uuid4())).encode()).hexdigest()
        scope = hashlib.sha256(f"{action}\0{target}".encode()).hexdigest()
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            conn.execute(
                "DELETE FROM quota_reservations WHERE scope=? AND reserved_at <= ?",
                (scope, now - window_seconds),
            )
            existing = conn.execute(
                "SELECT 1 FROM quota_reservations WHERE scope=? AND reservation_key=?",
                (scope, key),
            ).fetchone()
            if existing:
                conn.execute("COMMIT")
                return False
            count = conn.execute(
                "SELECT COUNT(*) FROM quota_reservations WHERE scope=? AND reserved_at > ?",
                (scope, now - window_seconds),
            ).fetchone()[0]
            if count >= limit:
                conn.execute("COMMIT")
                return False
            conn.execute(
                "INSERT INTO quota_reservations(scope, reservation_key, reserved_at) VALUES(?,?,?)",
                (scope, key, now),
            )
            conn.execute("COMMIT")
            return True
        except BaseException:
            if conn.in_transaction:
                conn.execute("ROLLBACK")
            raise
        finally:
            conn.close()
