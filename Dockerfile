# Base ultra-légère et sécurisée (Distroless-like ou Debian slim durci)
FROM python:3.11-slim-bookworm

WORKDIR /app

# Invariants de sécurité système
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ENVIRONMENT=production \
    PORT=8001 \
    APPROVAL_DB_PATH=/tmp/state/approvals.db \
    TS_SOCKET=/tmp/tailscaled.sock \
    TS_STATE=/tmp/tailscaled.state

# Installation de Redis, curl et Tailscale
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    redis-server \
    && curl -fsSL https://pkgs.tailscale.com/stable/debian/bookworm.noarmor.gpg | tee /usr/share/keyrings/tailscale-archive-keyring.gpg >/dev/null \
    && curl -fsSL https://pkgs.tailscale.com/stable/debian/bookworm.tailscale-keyring.list | tee /etc/apt/sources.list.d/tailscale.list \
    && apt-get update && apt-get install -y --no-install-recommends tailscale \
    && rm -rf /var/lib/apt/lists/*

# Copie des fichiers de configuration et des sources
COPY pyproject.toml README.md start_sandbox.sh ./
COPY scripts/ ./scripts/
COPY agentic_ops/ ./agentic_ops/
COPY tests/ ./tests/
COPY docs/ ./docs/
COPY reports/ ./reports/
COPY state/ ./state/

# Installation via l'installateur sécurisé 'uv' (incluant httpx[socks], pytest, hypothesis, fakeredis)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    /root/.local/bin/uv pip install --system --no-cache -e . && \
    /root/.local/bin/uv pip install --system --no-cache 'httpx[socks]' pytest pytest-mock hypothesis fakeredis && \
    mkdir -p /app/reports /tmp/state && \
    chmod -R 777 /app/reports /app/state /tmp/state

# Règle du moindre privilège : utilisateur sans privilèges root
RUN useradd -m -u 10001 agentic_user && \
    chmod +x /app/scripts/entrypoint.sh /app/start_sandbox.sh && \
    mkdir -p /tmp/state && \
    chown -R agentic_user:agentic_user /app /tmp/state

USER agentic_user

EXPOSE 8001

# Lancement automatisé via le script d'initialisation Auto-Wake (Redis + Tailscale + FastAPI)
ENTRYPOINT ["/app/scripts/entrypoint.sh"]
