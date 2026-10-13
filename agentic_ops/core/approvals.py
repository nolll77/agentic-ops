from __future__ import annotations
import hashlib, json, os, sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from enum import Enum
from typing import Callable

class Result(str, Enum):
    RECORDED = "RECORDED"        # approbation enregistrée, seuil pas atteint
    CLAIMED = "CLAIMED"          # CET appel a gagné : il exécute
    DENIED = "DENIED"
    DUPLICATE = "DUPLICATE"      # même approbateur déjà compté
    EXPIRED = "EXPIRED"
    HASH_MISMATCH = "HASH_MISMATCH"
    DIVERGED = "DIVERGED"        # l'épisode courant ne correspond plus à la demande
    CLOSED = "CLOSED"            # déjà claim / refusé / expiré
    UNKNOWN = "UNKNOWN"

@dataclass(frozen=True)
class FrozenProposal:
    episode_id: str
    action: str
    target: str
    risk_id: str
    policy_version: str
    required: int
    required_groups: tuple[str, ...] = ()

    def digest(self) -> str:
        canon = json.dumps(self.__dict__, sort_keys=True, separators=(",", ":"), default=list)
        return hashlib.sha256(canon.encode()).hexdigest()[:24]

_SCHEMA = """
CREATE TABLE IF NOT EXISTS requests(
  episode_id TEXT PRIMARY KEY, hash TEXT NOT NULL, proposal TEXT NOT NULL,
  status TEXT NOT NULL, required INTEGER NOT NULL, required_groups TEXT NOT NULL,
  created_at REAL NOT NULL, expires_at REAL NOT NULL);
CREATE TABLE IF NOT EXISTS approvals(
  episode_id TEXT NOT NULL, approver TEXT NOT NULL, grp TEXT NOT NULL, decided_at REAL NOT NULL,
  PRIMARY KEY(episode_id, approver));
CREATE TABLE IF NOT EXISTS seen_signatures(sig TEXT PRIMARY KEY, ts REAL NOT NULL);
"""

class ApprovalRepo:
    def __init__(self, path: str, clock: Callable[[], float]):
        self.path, self.clock = path, clock
        if path != ":memory:":
            os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with self._conn() as c:
            c.execute("PRAGMA journal_mode=WAL"); c.executescript(_SCHEMA)

    def _conn(self):
        c = sqlite3.connect(self.path, timeout=5, isolation_level=None)
        c.row_factory = sqlite3.Row
        c.execute("PRAGMA busy_timeout=5000")
        return c

    @contextmanager
    def _tx(self):
        c = self._conn()
        try:
            c.execute("BEGIN IMMEDIATE")
            yield c
            c.execute("COMMIT")
        except BaseException:
            c.execute("ROLLBACK"); raise
        finally:
            c.close()

    def open_request(self, p: FrozenProposal, ttl_s: int) -> str:
        now = self.clock()
        with self._tx() as c:
            c.execute("INSERT OR IGNORE INTO requests VALUES(?,?,?,?,?,?,?,?)",
                      (p.episode_id, p.digest(), json.dumps(p.__dict__, default=list), "PENDING",
                       p.required, json.dumps(p.required_groups), now, now + ttl_s))
            return c.execute("SELECT hash FROM requests WHERE episode_id=?", (p.episode_id,)).fetchone()["hash"]

    def register_signature(self, sig: str) -> bool:
        now = self.clock()
        with self._tx() as c:
            c.execute("DELETE FROM seen_signatures WHERE ts < ?", (now - 900,))
            try:
                c.execute("INSERT INTO seen_signatures VALUES(?,?)", (hashlib.sha256(sig.encode()).hexdigest(), now))
                return True
            except sqlite3.IntegrityError:
                return False

    def decide(self, episode_id: str, approver: str, group: str, decision: str,
               claimed_hash: str, current_hash: str) -> tuple[Result, FrozenProposal | None]:
        now = self.clock()
        with self._tx() as c:
            r = c.execute("SELECT * FROM requests WHERE episode_id=?", (episode_id,)).fetchone()
            if r is None:
                return Result.UNKNOWN, None
            if r["status"] != "PENDING":
                return Result.CLOSED, None
            if now >= r["expires_at"]:
                c.execute("UPDATE requests SET status='EXPIRED' WHERE episode_id=?", (episode_id,))
                return Result.EXPIRED, None
            if current_hash != r["hash"]:
                c.execute("UPDATE requests SET status='INVALIDATED' WHERE episode_id=?", (episode_id,))
                return Result.DIVERGED, None
            if claimed_hash != r["hash"]:
                return Result.HASH_MISMATCH, None
            if decision == "deny":
                c.execute("INSERT OR IGNORE INTO approvals VALUES(?,?,?,?)", (episode_id, approver, group, now))
                c.execute("UPDATE requests SET status='DENIED' WHERE episode_id=?", (episode_id,))
                return Result.DENIED, None
            cur = c.execute("INSERT OR IGNORE INTO approvals VALUES(?,?,?,?)", (episode_id, approver, group, now))
            if cur.rowcount == 0:
                return Result.DUPLICATE, None
            groups = {x["grp"] for x in c.execute("SELECT grp FROM approvals WHERE episode_id=?", (episode_id,))}
            n = c.execute("SELECT COUNT(*) n FROM approvals WHERE episode_id=?", (episode_id,)).fetchone()["n"]
            need_groups = set(json.loads(r["required_groups"]))
            if n >= r["required"] and need_groups <= groups:
                c.execute("UPDATE requests SET status='CLAIMED' WHERE episode_id=? AND status='PENDING'", (episode_id,))
                return Result.CLAIMED, FrozenProposal(**{**json.loads(r["proposal"]),
                                                          "required_groups": tuple(need_groups)})
            return Result.RECORDED, None

    def finish(self, episode_id: str, status: str) -> None:
        with self._tx() as c:
            c.execute("UPDATE requests SET status=? WHERE episode_id=? AND status='CLAIMED'", (status, episode_id))

    def sweep_expired(self) -> list[str]:
        with self._tx() as c:
            ids = [x["episode_id"] for x in c.execute(
                "SELECT episode_id FROM requests WHERE status='PENDING' AND expires_at <= ?", (self.clock(),))]
            for i in ids:
                c.execute("UPDATE requests SET status='EXPIRED' WHERE episode_id=?", (i,))
            return ids

    def stuck_claims(self, older_than_s: int) -> list[str]:
        with self._tx() as c:
            return [x["episode_id"] for x in c.execute(
                "SELECT episode_id FROM requests WHERE status='CLAIMED' AND created_at <= ?",
                (self.clock() - older_than_s,))]
