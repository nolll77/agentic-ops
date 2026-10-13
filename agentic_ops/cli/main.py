import os
import socket
import time
from types import SimpleNamespace
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from agentic_ops.entrypoints.slack_webhook import router as slack_router
from agentic_ops.core.approvals import ApprovalRepo
from agentic_ops.adapters.cac_pull_collector import CacPullCollector

app = FastAPI(
    title="Agentic-Ops Control Plane",
    description="Deterministic SRE & MLOps Governance Control Plane (Auto-Wake Ready)",
    version="0.1.0",
)

# CORS enabled so a Vercel frontend or external dashboard can wake the container via fetch()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# HITL (Human-In-The-Loop) state initialization for /slack/interactive
db_path = os.environ.get("APPROVAL_DB_PATH", "state/approvals.db")
if db_path != ":memory:":
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
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


def _is_port_open(host: str, port: int, timeout: float = 0.5) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


@app.get("/")
def root():
    """
    Auto-wake landing route. Visiting the container URL or calling it from a
    frontend wakes the container and returns the live Control Plane status.
    """
    return {
        "service": "agentic-ops-control-plane",
        "status": "awake",
        "redis_local_6379": _is_port_open("127.0.0.1", 6379),
        "tailscale_socks5_1055": _is_port_open("127.0.0.1", 1055),
        "endpoints": {
            "healthz": "/healthz",
            "ready": "/ready",
            "tailscale_status": "/api/tailscale/status",
            "cac_snapshot": "/api/cac/snapshot",
            "slack_webhook": "/slack/interactive",
        },
    }


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/ready")
def ready():
    return {
        "status": "ready",
        "redis_local_6379": _is_port_open("127.0.0.1", 6379),
        "tailscale_socks5_1055": _is_port_open("127.0.0.1", 1055),
    }


@app.get("/api/tailscale/status")
def tailscale_status():
    """
    Returns the live Tailscale daemon status, the fresh interactive AuthURL
    (if NeedsLogin), and the base64-encoded state (TS_STATE_B64) once authenticated
    so non-admin members can persist their session in Render Environment Variables.
    """
    import base64
    import json
    import subprocess

    ts_socket = os.environ.get("TS_SOCKET", "/tmp/tailscaled.sock")
    ts_state_path = os.environ.get("TS_STATE", "/tmp/tailscaled.state")
    hostname = os.environ.get("TS_HOSTNAME", "agentic-ops-render")

    status_data = {}
    try:
        res = subprocess.run(
            ["tailscale", f"--socket={ts_socket}", "status", "--json"],
            capture_output=True,
            text=True,
            timeout=3,
        )
        if res.returncode == 0 and res.stdout:
            status_data = json.loads(res.stdout)
    except Exception as exc:
        return {"error": str(exc)}

    backend_state = status_data.get("BackendState", "Unknown")
    auth_url = status_data.get("AuthURL", "")

    # If NeedsLogin but AuthURL is not populated yet, trigger non-blocking tailscale up
    if backend_state in ("NeedsLogin", "NoState", "Stopped") and not auth_url:
        try:
            subprocess.Popen(
                [
                    "tailscale",
                    f"--socket={ts_socket}",
                    "up",
                    f"--hostname={hostname}",
                    "--accept-routes",
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            time.sleep(1.5)
            res2 = subprocess.run(
                ["tailscale", f"--socket={ts_socket}", "status", "--json"],
                capture_output=True,
                text=True,
                timeout=3,
            )
            if res2.returncode == 0 and res2.stdout:
                status_data = json.loads(res2.stdout)
                backend_state = status_data.get("BackendState", backend_state)
                auth_url = status_data.get("AuthURL", "")
        except Exception:
            pass

    ts_state_b64 = None
    if backend_state == "Running" and os.path.exists(ts_state_path):
        try:
            with open(ts_state_path, "rb") as f:
                ts_state_b64 = base64.b64encode(f.read()).decode("ascii")
        except Exception:
            ts_state_b64 = None

    self_node = status_data.get("Self") or {}
    return {
        "backend_state": backend_state,
        "auth_url": auth_url or None,
        "tailscale_ips": self_node.get("TailscaleIPs", []),
        "hostname": self_node.get("HostName"),
        "ts_state_b64": ts_state_b64,
        "instructions": (
            "1. Open auth_url in your browser to authorize this container. "
            "2. Refresh this page once connected to copy ts_state_b64 into Render Environment Variables as TS_STATE_B64."
            if backend_state != "Running"
            else "Connected to Tailscale! Copy ts_state_b64 into Render Environment Variables (Key: TS_STATE_B64) to persist across container sleep cycles."
        ),
    }


@app.get("/api/cac/snapshot")
def get_cac_snapshot(use_proxy: bool = Query(default=True), timeout: float = Query(default=3.5)):
    """
    Triggers an immediate Read-Only Pull collection against the remote
    jakatt/cac_mlops platform (via Tailscale SOCKS5 proxy if available).
    """
    proxy_available = _is_port_open("127.0.0.1", 1055)
    collector = CacPullCollector(
        use_proxy_for_vps=(use_proxy and proxy_available),
        timeout=timeout,
    )
    snapshot = collector.collect_all()
    return snapshot.model_dump(mode="json")


app.include_router(slack_router)


def start_server():
    import uvicorn
    port = int(os.environ.get("PORT", "8001"))
    uvicorn.run("agentic_ops.cli.main:app", host="0.0.0.0", port=port)
