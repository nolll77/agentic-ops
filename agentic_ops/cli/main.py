import os
import re
import socket
import subprocess
import sys
import time
from enum import Enum
from types import SimpleNamespace
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, PlainTextResponse
from agentic_ops.entrypoints.slack_webhook import router as slack_router
from agentic_ops.core.approvals import ApprovalRepo
from agentic_ops.adapters.cac_pull_collector import CacPullCollector

app = FastAPI(
    title="Agentic-Ops Control Plane",
    description="Deterministic SRE & MLOps Governance Control Plane (Auto-Wake Ready + Web Diagnostic Console)",
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


def _redact_pii(text: str) -> str:
    """Redacts email addresses and personal workstation hostnames from diagnostic outputs."""
    if not text:
        return text
    redacted = re.sub(r"[\w\.-]+@[\w\.-]+\.\w+", "[REDACTED_ACCOUNT]", text)
    redacted = re.sub(r"(?i)(jacquess-imac|nollls-macbook-pro)", "[REDACTED_WORKSTATION]", redacted)
    return redacted


class DiagnosticCommand(str, Enum):
    pytest_cac_connector = "pytest_cac_connector"
    pytest_security = "pytest_security"
    pytest_all = "pytest_all"
    trust_ledger_list = "trust_ledger_list"
    tailscale_status = "tailscale_status"
    tailscale_netcheck = "tailscale_netcheck"
    tailscale_logs = "tailscale_logs"
    redis_ping = "redis_ping"
    system_info = "system_info"


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
            "web_console": "/console",
            "swagger_docs": "/docs",
            "healthz": "/healthz",
            "ready": "/ready",
            "tailscale_status": "/api/tailscale/status",
            "cac_snapshot": "/api/cac/snapshot",
            "diagnostics": "/api/diagnostics/{command}",
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


@app.get("/api/diagnostics/{command}", response_class=PlainTextResponse)
def run_diagnostic_command(command: DiagnosticCommand):
    """
    Executes a whitelisted SRE diagnostic command inside the container and returns
    formatted plain-text terminal output (with automatic PII redaction).
    Replaces the paid Render SSH Shell tab for zero-cost live auditing.
    """
    ts_socket = os.environ.get("TS_SOCKET", "/tmp/tailscaled.sock")
    py = sys.executable

    cmd_map = {
        DiagnosticCommand.pytest_cac_connector: [py, "-m", "pytest", "tests/adapters/test_cac_pull_collector.py", "-v"],
        DiagnosticCommand.pytest_security: [py, "-m", "pytest", "tests/security/", "tests/integration/", "-v"],
        DiagnosticCommand.pytest_all: [py, "-m", "pytest", "tests/", "-v"],
        DiagnosticCommand.trust_ledger_list: [py, "-m", "agentic_ops.cli.trust_ledger", "list"],
        DiagnosticCommand.tailscale_status: ["tailscale", f"--socket={ts_socket}", "status"],
        DiagnosticCommand.tailscale_netcheck: ["tailscale", f"--socket={ts_socket}", "netcheck"],
        DiagnosticCommand.redis_ping: ["redis-cli", "-h", "127.0.0.1", "-p", "6379", "PING"],
    }

    t0 = time.time()
    if command == DiagnosticCommand.tailscale_logs:
        logs = []
        for path in ("/tmp/tailscale_up.log", "/tmp/tailscaled.log"):
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8", errors="replace") as f:
                        content = f.read()[-4000:]
                    logs.append(f"=== {path} ===\n{content}")
                except Exception as exc:
                    logs.append(f"=== {path} (error: {exc}) ===")
            else:
                logs.append(f"=== {path} (not found) ===")
        out = "\n\n".join(logs)
        return _redact_pii(out)

    if command == DiagnosticCommand.system_info:
        uname = subprocess.run(["uname", "-a"], capture_output=True, text=True).stdout.strip()
        info = [
            "=== Agentic-Ops Container Runtime Info ===",
            f"OS / Kernel          : {uname}",
            f"Python Executable    : {sys.executable} ({sys.version.split()[0]})",
            f"Working Directory    : {os.getcwd()}",
            f"Redis Local (:6379)  : {'OPEN (ONLINE)' if _is_port_open('127.0.0.1', 6379) else 'CLOSED'}",
            f"Tailscale (:1055)    : {'OPEN (ONLINE)' if _is_port_open('127.0.0.1', 1055) else 'CLOSED'}",
            f"Approval DB Path     : {db_path} (exists={os.path.exists(db_path)})",
        ]
        return "\n".join(info)

    argv = cmd_map[command]
    env = {**os.environ, "PYTHONPATH": "/app:."}
    try:
        proc = subprocess.run(
            argv,
            capture_output=True,
            text=True,
            timeout=25,
            env=env,
        )
        elapsed_ms = int((time.time() - t0) * 1000)
        header = (
            f"$ {' '.join(argv)}\n"
            f"[exit_code={proc.returncode} | duration={elapsed_ms}ms]\n"
            f"{'-' * 72}\n"
        )
        body = (proc.stdout or "") + ("\n" + proc.stderr if proc.stderr else "")
        return _redact_pii(header + body.strip() + "\n")
    except Exception as exc:
        return f"Error executing {command.value}: {exc}\n"


@app.get("/console", response_class=HTMLResponse)
def web_console():
    """
    Interactive Dark-Mode SRE Web Terminal & Diagnostic Cockpit.
    Provides 1-click execution of pytest suites, Tailscale mesh status/netcheck,
    WORM Trust Ledger inspection, and CAC MLOps Pull snapshots directly in the browser.
    """
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Agentic-Ops SRE Web Terminal</title>
  <style>
    :root {
      --bg: #090d16;
      --panel: #111827;
      --border: #1e293b;
      --accent: #38bdf8;
      --purple: #c084fc;
      --amber: #f59e0b;
      --emerald: #34d399;
      --text: #f8fafc;
      --muted: #94a3b8;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      padding: 24px;
      background: var(--bg);
      color: var(--text);
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    }
    .container { max-width: 1120px; margin: 0 auto; }
    header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 12px;
      padding: 16px 20px;
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 8px;
      margin-bottom: 16px;
    }
    h1 { font-size: 18px; margin: 0; color: var(--accent); }
    .subtitle { font-size: 12px; color: var(--muted); margin-top: 4px; }
    .badges { display: flex; gap: 8px; flex-wrap: wrap; }
    .badge {
      font-size: 11px;
      padding: 4px 10px;
      border-radius: 999px;
      background: #064e3b;
      border: 1px solid var(--emerald);
      color: #d1fae5;
    }
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
      gap: 10px;
      margin-bottom: 16px;
    }
    button {
      background: var(--panel);
      color: var(--text);
      border: 1px solid var(--border);
      border-left: 3px solid var(--accent);
      padding: 10px 12px;
      border-radius: 6px;
      font-family: inherit;
      font-size: 12px;
      text-align: left;
      cursor: pointer;
      transition: all 0.15s ease;
    }
    button:hover {
      background: #1e293b;
      border-color: var(--accent);
    }
    button.purple { border-left-color: var(--purple); }
    button.amber { border-left-color: var(--amber); }
    button.emerald { border-left-color: var(--emerald); }
    button strong { display: block; margin-bottom: 3px; font-size: 13px; }
    button span { color: var(--muted); font-size: 11px; }
    .terminal {
      background: #05080f;
      border: 1px solid var(--border);
      border-radius: 8px;
      overflow: hidden;
    }
    .terminal-bar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 8px 14px;
      background: #0f172a;
      border-bottom: 1px solid var(--border);
      font-size: 12px;
      color: var(--muted);
    }
    pre {
      margin: 0;
      padding: 16px;
      min-height: 440px;
      max-height: 680px;
      overflow: auto;
      font-size: 12.5px;
      line-height: 1.5;
      color: #e2e8f0;
      white-space: pre-wrap;
      word-break: break-word;
    }
    a { color: var(--accent); text-decoration: none; }
    a:hover { text-decoration: underline; }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <div>
        <h1>Agentic-Ops — SRE Diagnostic Web Console</h1>
        <div class="subtitle">Zero-Cost Container Shell Replacement (Whitelisted Read-Only & Audit Commands) | <a href="/docs" target="_blank">Open Swagger UI (/docs)</a></div>
      </div>
      <div class="badges">
        <span class="badge">Redis :6379 Active</span>
        <span class="badge">Tailscale SOCKS5 :1055 Active</span>
        <span class="badge">FastAPI :8001 Live</span>
      </div>
    </header>

    <div class="grid">
      <button class="emerald" onclick="runCmd('pytest_cac_connector')">
        <strong>1. Pytest: CAC Tailscale Connector</strong>
        <span>pytest tests/adapters/test_cac_pull_collector.py -v</span>
      </button>
      <button class="emerald" onclick="runCmd('pytest_security')">
        <strong>2. Pytest: Red-Team & WORM Security</strong>
        <span>pytest tests/security/ tests/integration/ -v</span>
      </button>
      <button class="emerald" onclick="runCmd('pytest_all')">
        <strong>3. Pytest: Full Test Suite (All)</strong>
        <span>pytest tests/ -v (All unit + security tests)</span>
      </button>
      <button class="amber" onclick="runCmd('trust_ledger_list')">
        <strong>4. WORM Trust Ledger CLI</strong>
        <span>python -m agentic_ops.cli.trust_ledger list</span>
      </button>
      <button onclick="runCmd('tailscale_status')">
        <strong>5. Tailscale Mesh Status</strong>
        <span>tailscale status (PII auto-redacted)</span>
      </button>
      <button onclick="runCmd('tailscale_netcheck')">
        <strong>6. Tailscale DERP Netcheck</strong>
        <span>tailscale netcheck (UDP / DERP latencies)</span>
      </button>
      <button onclick="runJson('/api/cac/snapshot?timeout=3.5')">
        <strong>7. Live Pull: jakatt/cac_mlops</strong>
        <span>GET /api/cac/snapshot (5 observability sources)</span>
      </button>
      <button class="purple" onclick="runCmd('redis_ping')">
        <strong>8. Redis Local Daemon Ping</strong>
        <span>redis-cli -h 127.0.0.1 -p 6379 PING</span>
      </button>
      <button class="purple" onclick="runCmd('tailscale_logs')">
        <strong>9. Tailscale Daemon Logs</strong>
        <span>cat /tmp/tailscale_up.log & tailscaled.log</span>
      </button>
      <button class="amber" onclick="runCmd('system_info')">
        <strong>10. Container Runtime Info</strong>
        <span>uname -a, Python, open ports, SQLite WAL</span>
      </button>
    </div>

    <div class="terminal">
      <div class="terminal-bar">
        <span id="cmd-title">Ready — Click any diagnostic command button above to execute inside the live Render container.</span>
        <span id="cmd-status">IDLE</span>
      </div>
      <pre id="output">Agentic-Ops Control Plane — Interactive Web Console Ready.
Select a command above to inspect the container, run the Pytest security/connector suites, or query the Tailscale mesh.</pre>
    </div>
  </div>

  <script>
    async function runCmd(cmd) {
      const out = document.getElementById('output');
      const title = document.getElementById('cmd-title');
      const status = document.getElementById('cmd-status');
      title.textContent = 'Running: /api/diagnostics/' + cmd + ' ...';
      status.textContent = 'RUNNING...';
      out.textContent = 'Executing command inside container, please wait...';
      try {
        const res = await fetch('/api/diagnostics/' + cmd);
        const text = await res.text();
        title.textContent = 'Completed: /api/diagnostics/' + cmd;
        status.textContent = 'HTTP ' + res.status;
        out.textContent = text;
      } catch (err) {
        status.textContent = 'ERROR';
        out.textContent = 'Request failed: ' + err;
      }
    }

    async function runJson(url) {
      const out = document.getElementById('output');
      const title = document.getElementById('cmd-title');
      const status = document.getElementById('cmd-status');
      title.textContent = 'Fetching: ' + url + ' ...';
      status.textContent = 'RUNNING...';
      out.textContent = 'Polling remote jakatt/cac_mlops endpoints via Tailscale SOCKS5 (127.0.0.1:1055)...';
      try {
        const res = await fetch(url);
        const data = await res.json();
        title.textContent = 'Completed: ' + url;
        status.textContent = 'HTTP ' + res.status;
        out.textContent = JSON.stringify(data, null, 2);
      } catch (err) {
        status.textContent = 'ERROR';
        out.textContent = 'Request failed: ' + err;
      }
    }
  </script>
</body>
</html>"""


app.include_router(slack_router)


def start_server():
    import uvicorn
    port = int(os.environ.get("PORT", "8001"))
    uvicorn.run("agentic_ops.cli.main:app", host="0.0.0.0", port=port)

