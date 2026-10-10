#!/bin/bash
set -e

echo "=========================================="
echo " Initialisation Docker Sandbox & Tailscale"
echo "=========================================="

# Démarrage de Tailscale en arrière-plan avec le mode Userspace
# Cela évite d'avoir besoin des droits root (NET_ADMIN) sur la Sandbox Docker
echo "[1/3] Démarrage du démon Tailscale (Mode Userspace)..."
tailscaled --tun=userspace-networking --socks5-server=localhost:1055 --outbound-http-proxy-listen=localhost:1056 --state=/app/state/tailscaled.state &

# On attend que le socket soit prêt
sleep 3

# Authentification si une clé est fournie
if [ -n "$TS_AUTHKEY" ]; then
    echo "[2/3] Connexion au réseau Tailscale avec la clé fournie..."
    tailscale up --authkey=${TS_AUTHKEY} --hostname=agentic-ops-sandbox --accept-routes
else
    echo "[2/3] ATTENTION : Variable TS_AUTHKEY manquante. Tailscale ne sera pas connecté."
fi

# Pour que le code Python n'ait pas à changer et puisse contacter 100.117.99.62,
# on force toutes les requêtes réseau à passer par le proxy SOCKS5 local de Tailscale.
export HTTP_PROXY=socks5://localhost:1055
export HTTPS_PROXY=socks5://localhost:1055
export ALL_PROXY=socks5://localhost:1055

echo "[3/3] Lancement du Control Plane Agentic-Ops..."
exec agentic-start
