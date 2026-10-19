#!/bin/bash
set -e

echo "=========================================================="
echo " Agentic-Ops Auto-Wake Entrypoint (Redis + Tailscale + API)"
echo "=========================================================="

# 0. Prevent the SOCKS5 proxy loop (\x05\xff bug):
# Never export global HTTP_PROXY/HTTPS_PROXY before starting tailscaled.
unset HTTP_PROXY HTTPS_PROXY ALL_PROXY http_proxy https_proxy all_proxy

# Ensure runtime state directory exists (on Render/HF Spaces, /tmp is mounted fresh at runtime)
mkdir -p /tmp/state

# Initialize Ledger signing key if not injected via external KMS/secrets
if [ -z "$LEDGER_SECRET_KEY" ] && [ -z "$EVIDENCE_STORE_HMAC_KEY" ]; then
    echo "[SECURITY WARNING] Neither LEDGER_SECRET_KEY nor EVIDENCE_STORE_HMAC_KEY configured."
    echo "Generating cryptographically random 256-bit ephemeral session key for sandbox container..."
    export LEDGER_SECRET_KEY="$(python3 -c 'import secrets; print(secrets.token_hex(32))')"
fi

# 1. Start local Redis daemon if available (for distributed locks & rate limiting)
if command -v redis-server >/dev/null 2>&1; then
    echo "[1/4] Starting local Redis server on 127.0.0.1:6379 (maxmemory 16mb, LRU eviction)..."
    redis-server --daemonize yes --bind 127.0.0.1 --port 6379 --maxmemory 16mb --maxmemory-policy allkeys-lru || true
else
    echo "[1/4] redis-server binary not found, skipping local daemon."
fi

# 2. Start Tailscale daemon in Userspace Networking mode (no root /dev/net/tun required)
TS_SOCKET="${TS_SOCKET:-/tmp/tailscaled.sock}"
TS_STATE="${TS_STATE:-/tmp/tailscaled.state}"

# If TS_STATE_B64 is set in Render Environment Variables, restore the authenticated state file
# so the container reconnects to Tailscale on wake-up without needing an Admin TS_AUTHKEY.
if [ -n "$TS_STATE_B64" ]; then
    echo "[2/4] Restoring authenticated Tailscale state from TS_STATE_B64..."
    echo "$TS_STATE_B64" | base64 -d > "$TS_STATE" 2>/dev/null || true
    chmod 600 "$TS_STATE" 2>/dev/null || true
fi

if command -v tailscaled >/dev/null 2>&1; then
    echo "[2/4] Starting tailscaled (--tun=userspace-networking, SOCKS5 on 127.0.0.1:1055)..."
    env -i PATH="$PATH" HOME="$HOME" nohup tailscaled \
        --tun=userspace-networking \
        --socks5-server=127.0.0.1:1055 \
        --state="$TS_STATE" \
        --socket="$TS_SOCKET" > /tmp/tailscaled.log 2>&1 &

    # Wait for Unix socket creation
    for i in $(seq 1 15); do
        if [ -S "$TS_SOCKET" ]; then
            chmod 666 "$TS_SOCKET" 2>/dev/null || true
            break
        fi
        sleep 0.5
    done

    # 3. Authentication: Zero-Click via TS_AUTHKEY or non-blocking background OAuth URL
    if [ -n "$TS_AUTHKEY" ]; then
        echo "[3/4] Authenticating Tailscale automatically via TS_AUTHKEY..."
        nohup tailscale --socket="$TS_SOCKET" up \
            --authkey="${TS_AUTHKEY}" \
            --hostname="${TS_HOSTNAME:-agentic-ops-render}" \
            --accept-routes > /tmp/tailscale_up.log 2>&1 &
    else
        echo "[3/4] TS_AUTHKEY not set. Launching non-blocking tailscale up in background (check Render logs for login URL if needed)..."
        nohup tailscale --socket="$TS_SOCKET" up \
            --hostname="${TS_HOSTNAME:-agentic-ops-render}" \
            --accept-routes > /tmp/tailscale_up.log 2>&1 &
        sleep 2
        cat /tmp/tailscale_up.log 2>/dev/null || true
    fi
else
    echo "[2/4] tailscaled binary not found, skipping tunnel initialization."
fi

echo "[4/4] Launching Agentic-Ops FastAPI Server on port ${PORT:-8001}..."
exec agentic-start
