#!/bin/bash
set -e

echo "=========================================================="
echo " Agentic-Ops Auto-Wake Entrypoint (Redis + Tailscale + API)"
echo "=========================================================="

# 0. Prevent the SOCKS5 proxy loop (\x05\xff bug):
# Never export global HTTP_PROXY/HTTPS_PROXY before starting tailscaled.
unset HTTP_PROXY HTTPS_PROXY ALL_PROXY http_proxy https_proxy all_proxy

# 1. Start local Redis daemon if available (for distributed locks & rate limiting)
if command -v redis-server >/dev/null 2>&1; then
    echo "[1/4] Starting local Redis server on 127.0.0.1:6379..."
    redis-server --daemonize yes --bind 127.0.0.1 --port 6379 || true
else
    echo "[1/4] redis-server binary not found, skipping local daemon."
fi

# 2. Start Tailscale daemon in Userspace Networking mode (no root /dev/net/tun required)
TS_SOCKET="${TS_SOCKET:-/tmp/tailscaled.sock}"
TS_STATE="${TS_STATE:-/tmp/tailscaled.state}"

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

    # 3. Zero-Click Authentication via TS_AUTHKEY
    if [ -n "$TS_AUTHKEY" ]; then
        echo "[3/4] Authenticating Tailscale automatically via TS_AUTHKEY..."
        tailscale --socket="$TS_SOCKET" up \
            --authkey="${TS_AUTHKEY}" \
            --hostname="${TS_HOSTNAME:-agentic-ops-autowake}" \
            --accept-routes || echo "Warning: tailscale up returned non-zero status."
    else
        echo "[3/4] TS_AUTHKEY not set. tailscaled SOCKS5 is running in standby mode."
    fi
else
    echo "[2/4] tailscaled binary not found, skipping tunnel initialization."
fi

# Note: CacPullCollector routes its requests through socks5://127.0.0.1:1055
# internally via httpx.HTTPTransport, avoiding any global environment pollution.

echo "[4/4] Launching Agentic-Ops FastAPI Server on port ${PORT:-7860}..."
exec agentic-start
