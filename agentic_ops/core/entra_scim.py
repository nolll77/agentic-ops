from __future__ import annotations

import json
import os
import re
import sqlite3
import time
import uuid
from collections.abc import Iterable
from datetime import datetime, timezone
from typing import Any


SCIM_ROLES = frozenset({"SRE", "SRE_LEAD", "DATA_STEWARD", "SECOPS"})
_USER_SCHEMA = "urn:ietf:params:scim:schemas:core:2.0:User"
_GROUP_SCHEMA = "urn:ietf:params:scim:schemas:core:2.0:Group"
_LIST_RESPONSE_SCHEMA = "urn:ietf:params:scim:api:messages:2.0:ListResponse"
_FILTER_RE = re.compile(r'^\s*(externalId|displayName)\s+eq\s+"([^"]+)"\s*$', re.I)


def scim_enabled() -> bool:
    return os.environ.get("SCIM_ENABLED", "false").lower() == "true"


def scim_database_path() -> str:
    return os.environ.get(
        "SCIM_DB_PATH", os.environ.get("APPROVAL_DB_PATH", "state/approvals.db")
    )


def _text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > 255:
        raise ValueError(f"{field} must be a non-empty string of at most 255 characters")
    return value.strip()


def _members(value: Any) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError("members must be an array")
    result: list[str] = []
    for item in value:
        if not isinstance(item, dict):
            raise ValueError("each member must be an object")
        result.append(_text(item.get("value"), "member.value"))
    if len(set(result)) != len(result):
        raise ValueError("members must not contain duplicates")
    return result


def _timestamp(value: float) -> str:
    return datetime.fromtimestamp(value, timezone.utc).isoformat().replace("+00:00", "Z")


class SCIMDirectory:
    """Durable SCIM role directory; SCIM externalId is the Slack member ID."""

    def __init__(self, path: str, clock=time.time):
        self.path = path
        self.clock = clock
        if path != ":memory:":
            os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        conn = self._conn()
        try:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS scim_users(
                    id TEXT PRIMARY KEY,
                    external_id TEXT NOT NULL UNIQUE,
                    user_name TEXT NOT NULL,
                    active INTEGER NOT NULL,
                    created_at REAL NOT NULL,
                    modified_at REAL NOT NULL
                );
                CREATE TABLE IF NOT EXISTS scim_groups(
                    id TEXT PRIMARY KEY,
                    display_name TEXT NOT NULL UNIQUE,
                    created_at REAL NOT NULL,
                    modified_at REAL NOT NULL
                );
                CREATE TABLE IF NOT EXISTS scim_group_members(
                    group_id TEXT NOT NULL REFERENCES scim_groups(id) ON DELETE CASCADE,
                    user_id TEXT NOT NULL REFERENCES scim_users(id) ON DELETE CASCADE,
                    PRIMARY KEY(group_id, user_id)
                );
                CREATE INDEX IF NOT EXISTS scim_users_external_id
                    ON scim_users(external_id);
                """
            )
        finally:
            conn.close()

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path, timeout=5, isolation_level=None)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA busy_timeout=5000")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    def _transaction(self):
        conn = self._conn()
        try:
            conn.execute("BEGIN IMMEDIATE")
        except BaseException:
            conn.close()
            raise
        return conn

    @staticmethod
    def _role(display_name: Any) -> str:
        name = _text(display_name, "displayName")
        if name not in SCIM_ROLES:
            raise ValueError("displayName must be one of the configured approver roles")
        return name

    def _user_resource(self, conn: sqlite3.Connection, user: sqlite3.Row) -> dict[str, Any]:
        groups = conn.execute(
            """SELECT g.id, g.display_name FROM scim_groups g
               JOIN scim_group_members m ON m.group_id=g.id
               WHERE m.user_id=? ORDER BY g.display_name""",
            (user["id"],),
        ).fetchall()
        return {
            "schemas": [_USER_SCHEMA],
            "id": user["id"],
            "externalId": user["external_id"],
            "userName": user["user_name"],
            "active": bool(user["active"]),
            "groups": [
                {"value": group["id"], "display": group["display_name"], "type": "direct"}
                for group in groups
            ],
            "meta": {
                "resourceType": "User",
                "created": _timestamp(user["created_at"]),
                "lastModified": _timestamp(user["modified_at"]),
            },
        }

    def _group_resource(self, conn: sqlite3.Connection, group: sqlite3.Row) -> dict[str, Any]:
        members = conn.execute(
            """SELECT u.id, u.user_name FROM scim_users u
               JOIN scim_group_members m ON m.user_id=u.id
               WHERE m.group_id=? ORDER BY u.id""",
            (group["id"],),
        ).fetchall()
        return {
            "schemas": [_GROUP_SCHEMA],
            "id": group["id"],
            "displayName": group["display_name"],
            "members": [
                {"value": user["id"], "display": user["user_name"], "type": "User"}
                for user in members
            ],
            "meta": {
                "resourceType": "Group",
                "created": _timestamp(group["created_at"]),
                "lastModified": _timestamp(group["modified_at"]),
            },
        }

    def get_user(self, user_id: str) -> dict[str, Any] | None:
        conn = self._conn()
        try:
            user = conn.execute("SELECT * FROM scim_users WHERE id=?", (user_id,)).fetchone()
            return self._user_resource(conn, user) if user else None
        finally:
            conn.close()

    def get_user_by_external_id(self, external_id: str) -> dict[str, Any] | None:
        conn = self._conn()
        try:
            user = conn.execute(
                "SELECT * FROM scim_users WHERE external_id=?", (external_id,)
            ).fetchone()
            return self._user_resource(conn, user) if user else None
        finally:
            conn.close()

    def save_user(
        self, data: dict[str, Any], user_id: str | None = None
    ) -> dict[str, Any]:
        external_id = _text(data.get("externalId"), "externalId")
        user_name = _text(data.get("userName"), "userName")
        active = data.get("active", True)
        if not isinstance(active, bool):
            raise ValueError("active must be a boolean")
        now = self.clock()
        conn = self._transaction()
        try:
            if user_id is None:
                user_id = str(uuid.uuid4())
                conn.execute(
                    "INSERT INTO scim_users VALUES(?,?,?,?,?,?)",
                    (user_id, external_id, user_name, int(active), now, now),
                )
            else:
                existing = conn.execute(
                    "SELECT 1 FROM scim_users WHERE id=?", (user_id,)
                ).fetchone()
                if existing is None:
                    raise KeyError(user_id)
                conn.execute(
                    """UPDATE scim_users SET external_id=?, user_name=?, active=?, modified_at=?
                       WHERE id=?""",
                    (external_id, user_name, int(active), now, user_id),
                )
            conn.execute("COMMIT")
        except BaseException:
            if conn.in_transaction:
                conn.execute("ROLLBACK")
            raise
        finally:
            conn.close()
        resource = self.get_user(user_id)
        if resource is None:
            raise RuntimeError("SCIM user disappeared after write")
        return resource

    def delete_user(self, user_id: str) -> bool:
        conn = self._conn()
        try:
            conn.execute("BEGIN IMMEDIATE")
            deleted = conn.execute("DELETE FROM scim_users WHERE id=?", (user_id,)).rowcount
            conn.execute("COMMIT")
            return deleted == 1
        except BaseException:
            if conn.in_transaction:
                conn.execute("ROLLBACK")
            raise
        finally:
            conn.close()

    def get_group(self, group_id: str) -> dict[str, Any] | None:
        conn = self._conn()
        try:
            group = conn.execute(
                "SELECT * FROM scim_groups WHERE id=?", (group_id,)
            ).fetchone()
            return self._group_resource(conn, group) if group else None
        finally:
            conn.close()

    def save_group(
        self, data: dict[str, Any], group_id: str | None = None
    ) -> dict[str, Any]:
        display_name = self._role(data.get("displayName"))
        member_ids = _members(data.get("members", []))
        now = self.clock()
        conn = self._transaction()
        try:
            missing = [
                member_id
                for member_id in member_ids
                if conn.execute("SELECT 1 FROM scim_users WHERE id=?", (member_id,)).fetchone()
                is None
            ]
            if missing:
                raise ValueError("group references an unknown SCIM user")
            if group_id is None:
                group_id = str(uuid.uuid4())
                conn.execute(
                    "INSERT INTO scim_groups VALUES(?,?,?,?)",
                    (group_id, display_name, now, now),
                )
            else:
                if conn.execute(
                    "SELECT 1 FROM scim_groups WHERE id=?", (group_id,)
                ).fetchone() is None:
                    raise KeyError(group_id)
                conn.execute(
                    "UPDATE scim_groups SET display_name=?, modified_at=? WHERE id=?",
                    (display_name, now, group_id),
                )
                conn.execute("DELETE FROM scim_group_members WHERE group_id=?", (group_id,))
            conn.executemany(
                "INSERT INTO scim_group_members VALUES(?,?)",
                [(group_id, member_id) for member_id in member_ids],
            )
            conn.execute("COMMIT")
        except BaseException:
            if conn.in_transaction:
                conn.execute("ROLLBACK")
            raise
        finally:
            conn.close()
        resource = self.get_group(group_id)
        if resource is None:
            raise RuntimeError("SCIM group disappeared after write")
        return resource

    def patch_group(self, group_id: str, operations: Iterable[dict[str, Any]]) -> dict[str, Any]:
        current = self.get_group(group_id)
        if current is None:
            raise KeyError(group_id)
        members = {member["value"] for member in current["members"]}
        for operation in operations:
            if not isinstance(operation, dict):
                raise ValueError("each SCIM operation must be an object")
            op = str(operation.get("op", "")).lower()
            path = str(operation.get("path", "members"))
            value = operation.get("value")
            member_filter = re.fullmatch(
                r'members\[value\s+eq\s+"([^"]+)"\](?:\.value)?', path, re.I
            )
            if path.lower() not in {"members", "members.value"} and not member_filter:
                raise ValueError("only group members may be patched")
            if member_filter:
                member_id = member_filter.group(1)
                if op == "remove":
                    members.discard(member_id)
                elif op == "add":
                    members.add(member_id)
                elif op == "replace":
                    values = _members(value if isinstance(value, list) else [value])
                    members.discard(member_id)
                    members.update(values)
                else:
                    raise ValueError(f"unsupported SCIM operation {op!r}")
            elif op == "replace":
                members = set(_members(value))
            elif op == "add":
                members.update(_members(value if isinstance(value, list) else [value]))
            elif op == "remove":
                if value is not None:
                    members.difference_update(_members(value if isinstance(value, list) else [value]))
                else:
                    members.clear()
            else:
                raise ValueError(f"unsupported SCIM operation {op!r}")
        return self.save_group(
            {"displayName": current["displayName"], "members": [{"value": item} for item in sorted(members)]},
            group_id,
        )

    def delete_group(self, group_id: str) -> bool:
        conn = self._conn()
        try:
            conn.execute("BEGIN IMMEDIATE")
            deleted = conn.execute("DELETE FROM scim_groups WHERE id=?", (group_id,)).rowcount
            conn.execute("COMMIT")
            return deleted == 1
        except BaseException:
            if conn.in_transaction:
                conn.execute("ROLLBACK")
            raise
        finally:
            conn.close()

    def list_resources(
        self,
        resource_type: str,
        *,
        filter_expression: str | None = None,
        start_index: int = 1,
        count: int = 100,
    ) -> dict[str, Any]:
        if start_index < 1 or count < 0 or count > 1000:
            raise ValueError("invalid SCIM pagination")
        conn = self._conn()
        try:
            if resource_type == "Users":
                select = "SELECT * FROM scim_users"
                allowed_filters = {"externalid": "external_id", "username": "user_name"}
                resource_fn = self._user_resource
            elif resource_type == "Groups":
                select = "SELECT * FROM scim_groups"
                allowed_filters = {"displayname": "display_name"}
                resource_fn = self._group_resource
            else:
                raise ValueError("unsupported SCIM resource type")
            params: tuple[Any, ...] = ()
            where = ""
            if filter_expression:
                match = _FILTER_RE.fullmatch(filter_expression)
                column = allowed_filters.get(match.group(1).lower()) if match else None
                if match is None or column is None:
                    raise ValueError("unsupported SCIM filter")
                where = f" WHERE {column}=?"
                params = (match.group(2),)
            total = conn.execute(f"SELECT COUNT(*) FROM ({select}{where})", params).fetchone()[0]
            rows = conn.execute(
                f"{select}{where} ORDER BY id LIMIT ? OFFSET ?",
                (*params, count, start_index - 1),
            ).fetchall()
            resources = [resource_fn(conn, row) for row in rows]
            return {
                "schemas": [_LIST_RESPONSE_SCHEMA],
                "totalResults": total,
                "startIndex": start_index,
                "itemsPerPage": len(resources),
                "Resources": resources,
            }
        finally:
            conn.close()

    def roles_for_external_id(self, external_id: str) -> set[str]:
        conn = self._conn()
        try:
            rows = conn.execute(
                """SELECT g.display_name FROM scim_users u
                   JOIN scim_group_members m ON m.user_id=u.id
                   JOIN scim_groups g ON g.id=m.group_id
                   WHERE u.external_id=? AND u.active=1""",
                (external_id,),
            ).fetchall()
            return {row["display_name"] for row in rows}
        finally:
            conn.close()

    def group_for_external_id(self, external_id: str, level: str) -> str | None:
        eligible = {
            "L2": ("SRE", "SRE_LEAD"),
            "L3": ("SRE", "DATA_STEWARD", "SECOPS"),
        }.get(level, ())
        roles = self.roles_for_external_id(external_id)
        return next((role for role in eligible if role in roles), None)
