import os
import time
from types import SimpleNamespace
from fastapi import FastAPI
from agentic_ops.entrypoints.slack_webhook import router as slack_router
from agentic_ops.core.approvals import ApprovalRepo

app = FastAPI(title="Agentic-Ops Control Plane")

# Initialisation de l'état HITL (Human-In-The-Loop) pour sécuriser /slack/interactive
os.makedirs("state", exist_ok=True)
db_path = os.environ.get("APPROVAL_DB_PATH", "state/approvals.db")
clock = time.time
repo = ApprovalRepo(db_path, clock)

app.state.hitl = SimpleNamespace(
    secrets=[os.environ.get("SLACK_SIGNING_SECRET", "dummy_secret_defense_presentation")],
    clock=clock,
    repo=repo,
    orchestrator=SimpleNamespace(
        load_episode=lambda ep_id: None,
        current_proposal_hash=lambda ep: "",
        resume_from_claim=lambda claim: None,
        close_episode=lambda ep_id, val: None,
    ),
    policy=SimpleNamespace(level_of=lambda ep: "L1"),
    approvers=SimpleNamespace(group_of=lambda user, level: "admin"),
)

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.get("/ready")
def ready():
    # En production, on pourrait vérifier Redis ici
    return {"status": "ready"}

app.include_router(slack_router)

def start_server():
    import uvicorn
    uvicorn.run("agentic_ops.cli.main:app", host="0.0.0.0", port=8001)
