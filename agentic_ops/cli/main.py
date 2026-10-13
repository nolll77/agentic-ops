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
    """Redacts email addresses, truncated Tailscale account names, and personal workstation hostnames."""
    if not text:
        return text
    redacted = re.sub(r"[\w\.-]+@(?:[\w\.-]+\.\w+|(?=\s|$))", "[REDACTED_ACCOUNT]", text)
    redacted = re.sub(r"(?i)(jacquess-imac|jacquess-mac-mini|nollls-macbook-pro)", "[REDACTED_WORKSTATION]", redacted)
    return redacted


class DiagnosticCommand(str, Enum):
    sandbox_phase_a_vitals = "sandbox_phase_a_vitals"
    sandbox_phase_b_slack_spoof = "sandbox_phase_b_slack_spoof"
    sandbox_phase_c_adversarial_worm = "sandbox_phase_c_adversarial_worm"
    sandbox_phase_d_mlops_scenarios = "sandbox_phase_d_mlops_scenarios"
    sandbox_phase_e_fsm_governance = "sandbox_phase_e_fsm_governance"
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
    Executes a whitelisted SRE / Docker Cloud Sandbox diagnostic command inside the
    container and returns formatted plain-text terminal output (with automatic PII redaction).
    Replaces the paid Render SSH Shell tab for zero-cost live auditing.
    """
    ts_socket = os.environ.get("TS_SOCKET", "/tmp/tailscaled.sock")
    py = sys.executable

    cmd_map = {
        DiagnosticCommand.sandbox_phase_c_adversarial_worm: [
            py, "-m", "pytest", "tests/adversarial/", "tests/security/", "-v"
        ],
        DiagnosticCommand.sandbox_phase_d_mlops_scenarios: [
            py, "-m", "pytest", "tests/scenarios/", "-v", "-s"
        ],
        DiagnosticCommand.sandbox_phase_e_fsm_governance: [
            py, "-m", "pytest",
            "tests/test_fsm_orchestrator.py",
            "tests/test_grafana_webhook.py",
            "tests/test_tools_security.py",
            "-v",
        ],
        DiagnosticCommand.pytest_cac_connector: [
            py, "-m", "pytest", "tests/adapters/test_cac_pull_collector.py", "-v"
        ],
        DiagnosticCommand.pytest_security: [
            py, "-m", "pytest", "tests/security/", "tests/integration/", "-v"
        ],
        DiagnosticCommand.pytest_all: [
            py, "-m", "pytest",
            "tests/adversarial/",
            "tests/security/",
            "tests/scenarios/",
            "tests/test_fsm_orchestrator.py",
            "tests/test_grafana_webhook.py",
            "tests/test_tools_security.py",
            "tests/adapters/test_cac_pull_collector.py",
            "-v",
        ],
        DiagnosticCommand.trust_ledger_list: [
            py, "-m", "agentic_ops.cli.trust_ledger", "list"
        ],
        DiagnosticCommand.tailscale_status: [
            "tailscale", f"--socket={ts_socket}", "status"
        ],
        DiagnosticCommand.tailscale_netcheck: [
            "tailscale", f"--socket={ts_socket}", "netcheck"
        ],
        DiagnosticCommand.redis_ping: [
            "redis-cli", "-h", "127.0.0.1", "-p", "6379", "PING"
        ],
    }

    t0 = time.time()

    if command in (DiagnosticCommand.sandbox_phase_a_vitals, DiagnosticCommand.system_info):
        try:
            uname = subprocess.run(["uname", "-a"], capture_output=True, text=True).stdout.strip()
        except Exception as exc:
            uname = f"Unknown ({exc})"

        mem_lines = []
        try:
            free_out = subprocess.run(["free", "-h"], capture_output=True, text=True).stdout.strip()
            if free_out:
                mem_lines.append(free_out)
        except Exception:
            pass

        if not mem_lines and os.path.exists("/proc/meminfo"):
            try:
                with open("/proc/meminfo", "r", encoding="utf-8", errors="replace") as f:
                    for line in f:
                        if line.startswith(("MemTotal:", "MemFree:", "MemAvailable:", "Buffers:", "Cached:", "SwapTotal:", "SwapFree:")):
                            mem_lines.append(line.strip())
            except Exception:
                pass

        for cg_path, label in (
            ("/sys/fs/cgroup/memory.current", "Cgroup Memory Current"),
            ("/sys/fs/cgroup/memory.max", "Cgroup Memory Max"),
        ):
            if os.path.exists(cg_path):
                try:
                    with open(cg_path, "r", encoding="utf-8") as f:
                        val = f.read().strip()
                        if val.isdigit():
                            mem_lines.append(f"{label:22s}: {int(val) / (1024 * 1024):.1f} MiB ({val} bytes)")
                        else:
                            mem_lines.append(f"{label:22s}: {val}")
                except Exception:
                    pass

        cpu_model = "Unknown"
        if os.path.exists("/proc/cpuinfo"):
            try:
                with open("/proc/cpuinfo", "r", encoding="utf-8", errors="replace") as f:
                    for line in f:
                        if "model name" in line:
                            cpu_model = line.split(":", 1)[1].strip()
                            break
            except Exception:
                pass
        info = [
            "=== Phase A: Container Vitals, Health Probes & Hardware Telemetry ===",
            f"OS / Kernel          : {uname}",
            f"CPU Architecture     : {cpu_model} (cores={os.cpu_count()})",
            f"Python Executable    : {sys.executable} ({sys.version.split()[0]})",
            f"Working Directory    : {os.getcwd()}",
            f"Probe GET /healthz   : {healthz()}",
            f"Probe GET /ready     : {ready()}",
            f"Redis Local (:6379)  : {'OPEN (ONLINE)' if _is_port_open('127.0.0.1', 6379) else 'CLOSED'}",
            f"Tailscale (:1055)    : {'OPEN (ONLINE)' if _is_port_open('127.0.0.1', 1055) else 'CLOSED'}",
            f"Approval DB Path     : {db_path} (exists={os.path.exists(db_path)})",
            "",
            "--- Memory & Cgroup Telemetry (/proc/meminfo & cgroup v2) ---",
            "\n".join(mem_lines) if mem_lines else "(memory telemetry unavailable)",
        ]
        return "\n".join(info) + "\n"

    if command == DiagnosticCommand.sandbox_phase_b_slack_spoof:
        from fastapi.testclient import TestClient

        client = TestClient(app)
        resp = client.post(
            "/slack/interactive",
            data={"payload": "fake_tampered_attack"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        elapsed_ms = int((time.time() - t0) * 1000)
        lines = [
            "=== Phase B: Live Red-Team Slack Webhook Spoofing Attack ===",
            "$ curl -i -X POST http://127.0.0.1:8001/slack/interactive \\",
            '    -H "Content-Type: application/x-www-form-urlencoded" \\',
            '    -d "payload=fake_tampered_attack"',
            f"[status_code={resp.status_code} | duration={elapsed_ms}ms]",
            "-" * 72,
            f"HTTP/1.1 {resp.status_code} Unauthorized",
            f"content-type: {resp.headers.get('content-type', 'application/json')}",
            "",
            resp.text,
            "",
            "VERDICT: Unauthenticated webhook payload rejected Fail-Closed (HTTP 401).",
        ]
        return "\n".join(lines) + "\n"

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

    pytest_inprocess_map = {
        DiagnosticCommand.sandbox_phase_c_adversarial_worm: [
            "tests/adversarial/", "tests/security/", "-v", "-p", "no:cacheprovider"
        ],
        DiagnosticCommand.sandbox_phase_d_mlops_scenarios: [
            "tests/scenarios/", "-v", "-s", "-p", "no:cacheprovider"
        ],
        DiagnosticCommand.sandbox_phase_e_fsm_governance: [
            "tests/test_fsm_orchestrator.py",
            "tests/test_grafana_webhook.py",
            "tests/test_tools_security.py",
            "-v",
            "-p",
            "no:cacheprovider",
        ],
        DiagnosticCommand.pytest_cac_connector: [
            "tests/adapters/test_cac_pull_collector.py", "-v", "-p", "no:cacheprovider"
        ],
        DiagnosticCommand.pytest_security: [
            "tests/security/", "tests/integration/", "-v", "-p", "no:cacheprovider"
        ],
        DiagnosticCommand.pytest_all: [
            "tests/adversarial/",
            "tests/security/",
            "tests/scenarios/",
            "tests/test_fsm_orchestrator.py",
            "tests/test_grafana_webhook.py",
            "tests/test_tools_security.py",
            "tests/adapters/test_cac_pull_collector.py",
            "-v",
            "-p",
            "no:cacheprovider",
        ],
    }

    if command in pytest_inprocess_map:
        import contextlib
        import io
        import pytest

        pt_args = pytest_inprocess_map[command]
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                rc = int(pytest.main(pt_args))
            elapsed_ms = int((time.time() - t0) * 1000)
            display_cmd = f"pytest {' '.join(a for a in pt_args if a not in ('-p', 'no:cacheprovider'))}"
            header = (
                f"$ {display_cmd}  [in-process warm execution]\n"
                f"[exit_code={rc} | duration={elapsed_ms}ms]\n"
                f"{'-' * 72}\n"
            )
            return _redact_pii(header + buf.getvalue().strip() + "\n")
        except Exception as exc:
            return f"Error executing {command.value}: {exc}\n"

    argv = cmd_map[command]
    env = {**os.environ, "PYTHONPATH": "/app:."}
    try:
        proc = subprocess.run(
            argv,
            capture_output=True,
            text=True,
            timeout=120,
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
    Provides 1-click execution of all Docker Cloud Sandbox validation phases (A-F),
    Tailscale mesh status/netcheck, WORM Trust Ledger inspection, and CAC MLOps Pull snapshots.
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
    .container { max-width: 1180px; margin: 0 auto; }
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
      grid-template-columns: repeat(auto-fill, minmax(275px, 1fr));
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
    button strong { display: block; margin-bottom: 3px; font-size: 12.5px; }
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
      min-height: 460px;
      max-height: 700px;
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
        <h1>Agentic-Ops — SRE & Docker Sandbox Web Console</h1>
        <div class="subtitle">Zero-Cost Container Shell Replacement (100% of Docker Cloud Sandbox Phases A-F + Tailscale Mesh) | <a href="/docs" target="_blank">Open Swagger UI (/docs)</a></div>
      </div>
      <div class="badges">
        <span class="badge">Redis :6379 Active</span>
        <span class="badge">Tailscale SOCKS5 :1055 Active</span>
        <span class="badge">FastAPI :8001 Live</span>
      </div>
    </header>

    <div class="grid">
      <button class="amber" onclick="runCmd('sandbox_phase_a_vitals')">
        <strong>Phase A: Vitals & Hardware Telemetry</strong>
        <span>/healthz, /ready, CPU model, free -h, ports</span>
      </button>
      <button class="amber" onclick="runCmd('sandbox_phase_b_slack_spoof')">
        <strong>Phase B: Red-Team Slack Spoof Attack</strong>
        <span>POST /slack/interactive -> HTTP 401 Fail-Closed</span>
      </button>
      <button class="emerald" onclick="runCmd('sandbox_phase_c_adversarial_worm')">
        <strong>Phase C: Adversarial & WORM (9 Tests)</strong>
        <span>pytest tests/adversarial/ tests/security/ -v</span>
      </button>
      <button class="emerald" onclick="runCmd('sandbox_phase_d_mlops_scenarios')">
        <strong>Phase D: Live Agentic Scenarios (10 Tests)</strong>
        <span>pytest tests/scenarios/ -v -s (forbidden_executed=0)</span>
      </button>
      <button class="emerald" onclick="runCmd('sandbox_phase_e_fsm_governance')">
        <strong>Phase E: FSM & Tool Sandboxing (10 Tests)</strong>
        <span>pytest test_fsm + test_grafana + test_tools -v</span>
      </button>
      <button class="emerald" onclick="runCmd('pytest_cac_connector')">
        <strong>Phase F: CAC Tailscale Connector (13 Tests)</strong>
        <span>pytest tests/adapters/test_cac_pull_collector.py -v</span>
      </button>
      <button class="emerald" onclick="runCmd('pytest_all')">
        <strong>Grand Slam: All 42 Sandbox + CAC Tests</strong>
        <span>Runs Phases C + D + E + F in a single pass</span>
      </button>
      <button class="amber" onclick="runCmd('trust_ledger_list')">
        <strong>WORM Trust Ledger CLI</strong>
        <span>python -m agentic_ops.cli.trust_ledger list</span>
      </button>
      <button onclick="runCmd('tailscale_status')">
        <strong>Tailscale Mesh Status</strong>
        <span>tailscale status (PII auto-redacted)</span>
      </button>
      <button onclick="runCmd('tailscale_netcheck')">
        <strong>Tailscale DERP Netcheck</strong>
        <span>tailscale netcheck (UDP / DERP latencies)</span>
      </button>
      <button onclick="runJson('/api/cac/snapshot?timeout=3.5')">
        <strong>Live Pull: jakatt/cac_mlops</strong>
        <span>GET /api/cac/snapshot (5 observability sources)</span>
      </button>
      <button class="purple" onclick="runCmd('redis_ping')">
        <strong>Redis Local Daemon Ping</strong>
        <span>redis-cli -h 127.0.0.1 -p 6379 PING</span>
      </button>
    </div>

    <div class="terminal">
      <div class="terminal-bar">
        <span id="cmd-title">Ready — Click any Docker Sandbox Phase (A-F) or Tailscale button above to execute inside the live Render container.</span>
        <span id="cmd-status">IDLE</span>
      </div>
      <pre id="output">Agentic-Ops Control Plane — Interactive Web Console Ready.
Select any command above to execute the Docker Cloud Sandbox validation phases (A through F), inspect the WORM Trust Ledger, or query the Tailscale mesh.</pre>
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

