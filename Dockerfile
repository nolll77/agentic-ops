# Base ultra-légère et sécurisée (Distroless-like ou Alpine durci)
FROM python:3.11-slim-bookworm

WORKDIR /app

# Invariants de sécurité système
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ENVIRONMENT=production

# Installation des dépendances minimales et de Tailscale
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && curl -fsSL https://pkgs.tailscale.com/stable/debian/bookworm.noarmor.gpg | tee /usr/share/keyrings/tailscale-archive-keyring.gpg >/dev/null \
    && curl -fsSL https://pkgs.tailscale.com/stable/debian/bookworm.tailscale-keyring.list | tee /etc/apt/sources.list.d/tailscale.list \
    && apt-get update && apt-get install -y --no-install-recommends tailscale \
    && rm -rf /var/lib/apt/lists/*

# Copie exclusive des fichiers de configuration et des sources
COPY pyproject.toml README.md start_sandbox.sh ./
COPY agentic_ops/ ./agentic_ops/
COPY state/ ./state/

# Installation via l'installateur sécurisé 'uv'
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    /root/.local/bin/uv pip install --system --no-cache -e .

# Règle du moindre privilège : on quitte le mode root pour un utilisateur sans droits
# Tailscale en mode Userspace peut tourner sans privilèges s'il a accès à son socket et à son state
RUN useradd -u 10001 agentic_user && \
    chmod +x start_sandbox.sh && \
    mkdir -p /var/run/tailscale && \
    chown -R agentic_user:agentic_user /app /var/run/tailscale

USER agentic_user

EXPOSE 8001

# Lancement automatisé via le script d'initialisation Tailscale
ENTRYPOINT ["/app/start_sandbox.sh"]
