from __future__ import annotations
import hashlib, json, os, sqlite3
import hmac
from contextlib import contextmanager
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Protocol

class Result(str, Enum):
    RECORDED = "RECORDED"        # approbation enregistrée, seuil pas atteint
    CLAIMED = "CLAIMED"          # quorum atteint et claim enregistré dans l'outbox durable
    DENIED = "DENIED"
    DUPLICATE = "DUPLICATE"      # même approbateur déjà compté
    EXPIRED = "EXPIRED"
    HASH_MISMATCH = "HASH_MISMATCH"
    DIVERGED = "DIVERGED"        # l'épisode courant ne correspond plus à la demande
    CLOSED = "CLOSED"            # déjà claim / refusé / expiré
    UNKNOWN = "UNKNOWN"
    SELF_APPROVAL = "SELF_APPROVAL"
    UNAUTHORIZED = "UNAUTHORIZED"
    INVALID_DECISION = "INVALID_DECISION"

@dataclass(frozen=True)
class FrozenProposal:
    episode_id: str
    action: str
    target: str
    risk_id: str
    policy_version: str
    required: int
    required_groups: tuple[str, ...] = ()
    requester_id: str = ""

    def digest(self) -> str:
        canon = json.dumps(self.__dict__, sort_keys=True, separators=(",", ":"), default=list)
        return hashlib.sha256(canon.encode()).hexdigest()


@dataclass(frozen=True)
class ExecutionClaim:
    proposal: FrozenProposal
    worker_id: str
    attempts: int


class ApprovedActionHandler(Protocol):
    def __call__(self, proposal: FrozenProposal) -> str | None: ...


_SCHEMA = """
CREATE TABLE IF NOT EXISTS requests(
  episode_id TEXT PRIMARY KEY, hash TEXT NOT NULL, proposal TEXT NOT NULL,
  status TEXT NOT NULL, required INTEGER NOT NULL, required_groups TEXT NOT NULL,
  created_at REAL NOT NULL, expires_at REAL NOT NULL);
CREATE TABLE IF NOT EXISTS approvals(
  episode_id TEXT NOT NULL, approver TEXT NOT NULL, grp TEXT NOT NULL, decided_at REAL NOT NULL,
  PRIMARY KEY(episode_id, approver));
CREATE TABLE IF NOT EXISTS seen_signatures(sig TEXT PRIMARY KEY, ts REAL NOT NULL);
CREATE TABLE IF NOT EXISTS execution_outbox(
  episode_id TEXT PRIMARY KEY, proposal TEXT NOT NULL, status TEXT NOT NULL,
  attempts INTEGER NOT NULL DEFAULT 0, created_at REAL NOT NULL, updated_at REAL NOT NULL,
  available_at REAL NOT NULL, lease_owner TEXT, lease_expires_at REAL, last_error TEXT);
CREATE INDEX IF NOT EXISTS execution_outbox_ready
  ON execution_outbox(status, available_at, lease_expires_at);
"""

class ApprovalRepo:
    def __init__(self, path: str, clock: Callable[[], float]):
        self.path, self.clock = path, clock
        if path != ":memory:":
            os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        c = self._conn()
        try:
            c.execute("PRAGMA journal_mode=WAL"); c.executescript(_SCHEMA)
        finally:
            c.close()

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
            if c.in_transaction:
                c.execute("ROLLBACK")
            raise
        finally:
            c.close()

    def open_request(self, p: FrozenProposal, ttl_s: int) -> str:
        if not p.requester_id.strip():
            raise ValueError("requester_id is required for an approval request")
        if ttl_s <= 0 or p.required < 1:
            raise ValueError("approval TTL and required quorum must be positive")
        if len(set(p.required_groups)) != len(p.required_groups):
            raise ValueError("required_groups must not contain duplicates")
        now = self.clock()
        with self._tx() as c:
            c.execute("INSERT OR IGNORE INTO requests VALUES(?,?,?,?,?,?,?,?)",
                      (p.episode_id, p.digest(), json.dumps(p.__dict__, default=list), "PENDING",
                       p.required, json.dumps(p.required_groups), now, now + ttl_s))
            row = c.execute(
                "SELECT hash FROM requests WHERE episode_id=?", (p.episode_id,)
            ).fetchone()
            if row["hash"] != p.digest():
                raise ValueError("an approval request with a different proposal already exists")
            return row["hash"]

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
               claimed_hash: str, current_hash: str,
               eligible_group_for: Callable[[str], str | None] | None = None
               ) -> tuple[Result, FrozenProposal | None]:
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
            if not hmac.compare_digest(claimed_hash, r["hash"]):
                return Result.HASH_MISMATCH, None
            if decision not in ("approve", "deny"):
                return Result.INVALID_DECISION, None
            if not approver.strip() or not group.strip():
                return Result.UNAUTHORIZED, None
            required_groups = set(json.loads(r["required_groups"]))
            if required_groups and group not in required_groups:
                return Result.UNAUTHORIZED, None
            proposal = json.loads(r["proposal"])
            if decision == "approve" and not proposal.get("requester_id"):
                return Result.UNAUTHORIZED, None
            if decision == "approve" and approver == proposal.get("requester_id"):
                return Result.SELF_APPROVAL, None
            if decision == "deny":
                c.execute("INSERT OR IGNORE INTO approvals VALUES(?,?,?,?)", (episode_id, approver, group, now))
                c.execute("UPDATE requests SET status='DENIED' WHERE episode_id=?", (episode_id,))
                return Result.DENIED, None
            if eligible_group_for is not None:
                for previous in c.execute(
                    "SELECT approver, grp FROM approvals WHERE episode_id=?", (episode_id,)
                ).fetchall():
                    if eligible_group_for(previous["approver"]) != previous["grp"]:
                        c.execute(
                            "DELETE FROM approvals WHERE episode_id=? AND approver=?",
                            (episode_id, previous["approver"]),
                        )
            cur = c.execute("INSERT OR IGNORE INTO approvals VALUES(?,?,?,?)", (episode_id, approver, group, now))
            if cur.rowcount == 0:
                return Result.DUPLICATE, None
            groups = {x["grp"] for x in c.execute("SELECT grp FROM approvals WHERE episode_id=?", (episode_id,))}
            n = c.execute("SELECT COUNT(*) n FROM approvals WHERE episode_id=?", (episode_id,)).fetchone()["n"]
            need_groups = required_groups
            if n >= r["required"] and need_groups <= groups:
                changed = c.execute(
                    "UPDATE requests SET status='CLAIMED' WHERE episode_id=? AND status='PENDING'",
                    (episode_id,),
                ).rowcount
                if changed != 1:
                    return Result.CLOSED, None
                c.execute(
                    """INSERT INTO execution_outbox
                       (episode_id, proposal, status, attempts, created_at, updated_at, available_at)
                       VALUES (?, ?, 'RECEIVED', 0, ?, ?, ?)""",
                    (episode_id, r["proposal"], now, now, now),
                )
                return Result.CLAIMED, FrozenProposal(
                    **{
                        **json.loads(r["proposal"]),
                        "required_groups": tuple(json.loads(r["required_groups"])),
                    }
                )
            return Result.RECORDED, None

    def claim_execution(self, worker_id: str, lease_s: int = 60) -> ExecutionClaim | None:
        if not worker_id.strip() or lease_s < 1:
            raise ValueError("worker_id and a positive lease duration are required")
        now = self.clock()
        with self._tx() as c:
            row = c.execute(
                """SELECT * FROM execution_outbox
                   WHERE (status IN ('RECEIVED', 'RETRY') AND available_at <= ?)
                      OR (status = 'PROCESSING' AND lease_expires_at <= ?)
                   ORDER BY created_at LIMIT 1""",
                (now, now),
            ).fetchone()
            if row is None:
                return None
            updated = c.execute(
                """UPDATE execution_outbox SET status='PROCESSING', attempts=attempts+1,
                       lease_owner=?, lease_expires_at=?, updated_at=?
                   WHERE episode_id=? AND
                     (status IN ('RECEIVED', 'RETRY') OR
                      (status='PROCESSING' AND lease_expires_at <= ?))""",
                (worker_id, now + lease_s, now, row["episode_id"], now),
            )
            if updated.rowcount != 1:
                return None
            claimed = c.execute(
                "SELECT * FROM execution_outbox WHERE episode_id=?", (row["episode_id"],)
            ).fetchone()
            data = json.loads(claimed["proposal"])
            data["required_groups"] = tuple(data.get("required_groups", ()))
            return ExecutionClaim(
                proposal=FrozenProposal(**data),
                worker_id=worker_id,
                attempts=claimed["attempts"],
            )

    def approvals_for(self, episode_id: str) -> list[tuple[str, str]]:
        conn = self._conn()
        try:
            rows = conn.execute(
                "SELECT approver, grp FROM approvals WHERE episode_id=? ORDER BY decided_at",
                (episode_id,),
            ).fetchall()
            return [(row["approver"], row["grp"]) for row in rows]
        finally:
            conn.close()

    def finish_execution(
        self,
        episode_id: str,
        worker_id: str,
        *,
        success: bool,
        error: str | None = None,
        result_status: str | None = None,
    ) -> None:
        now = self.clock()
        outbox_status = "COMPLETED" if success else "FAILED"
        request_status = (
            (result_status or "EXECUTED") if success else "EXECUTION_FAILED"
        )
        if request_status not in {"EXECUTED", "SIMULATED", "EXECUTION_FAILED"}:
            raise ValueError(f"invalid execution result status {request_status!r}")
        with self._tx() as c:
            row = c.execute(
                """SELECT 1 FROM execution_outbox WHERE episode_id=? AND status='PROCESSING'
                   AND lease_owner=?""",
                (episode_id, worker_id),
            ).fetchone()
            if row is None:
                raise RuntimeError(f"worker {worker_id!r} does not own execution claim {episode_id!r}")
            c.execute(
                """UPDATE execution_outbox SET status=?, last_error=?, updated_at=?,
                       lease_owner=NULL, lease_expires_at=NULL WHERE episode_id=?""",
                (outbox_status, error[:1000] if error else None, now, episode_id),
            )
            c.execute(
                "UPDATE requests SET status=? WHERE episode_id=? AND status='CLAIMED'",
                (request_status, episode_id),
            )

    def retry_execution(
        self, episode_id: str, worker_id: str, error: str, *, max_attempts: int = 5
    ) -> str:
        if max_attempts < 1:
            raise ValueError("max_attempts must be positive")
        now = self.clock()
        with self._tx() as c:
            row = c.execute(
                """SELECT attempts FROM execution_outbox WHERE episode_id=? AND status='PROCESSING'
                   AND lease_owner=?""",
                (episode_id, worker_id),
            ).fetchone()
            if row is None:
                raise RuntimeError(f"worker {worker_id!r} does not own execution claim {episode_id!r}")
            dead = row["attempts"] >= max_attempts
            status = "DEAD" if dead else "RETRY"
            delay = min(2 * 2 ** max(row["attempts"] - 1, 0), 300)
            c.execute(
                """UPDATE execution_outbox SET status=?, last_error=?, updated_at=?,
                       available_at=?, lease_owner=NULL, lease_expires_at=NULL WHERE episode_id=?""",
                (status, error[:1000], now, now + delay, episode_id),
            )
            if dead:
                c.execute(
                    "UPDATE requests SET status='EXECUTION_FAILED' WHERE episode_id=? AND status='CLAIMED'",
                    (episode_id,),
                )
            return status

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


class ApprovalExecutionWorker:
    """Lease-based worker; its handler must enforce target idempotency or reconcile."""

    def __init__(
        self,
        repo: ApprovalRepo,
        worker_id: str,
        handler: ApprovedActionHandler,
        *,
        lease_s: int = 60,
        max_attempts: int = 5,
    ):
        if not worker_id.strip() or lease_s < 1 or max_attempts < 1:
            raise ValueError("worker_id, lease_s and max_attempts must be valid")
        self.repo = repo
        self.worker_id = worker_id
        self.handler = handler
        self.lease_s = lease_s
        self.max_attempts = max_attempts

    def run_once(self) -> bool:
        claim = self.repo.claim_execution(self.worker_id, self.lease_s)
        if claim is None:
            return False
        try:
            result_status = self.handler(claim.proposal)
        except Exception as exc:
            self.repo.retry_execution(
                claim.proposal.episode_id,
                self.worker_id,
                type(exc).__name__,
                max_attempts=self.max_attempts,
            )
        else:
            self.repo.finish_execution(
                claim.proposal.episode_id,
                self.worker_id,
                success=True,
                result_status=result_status,
            )
        return True
