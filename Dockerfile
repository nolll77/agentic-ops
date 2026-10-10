# Base ultra-légère et sécurisée (Distroless-like ou Alpine durci)
FROM python:3.11-slim-bookworm

WORKDIR /app

# Invariants de sécurité système
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ENVIRONMENT=production

# Installation des dépendances minimales requises
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copie exclusive des fichiers de configuration et des sources
COPY pyproject.toml README.md ./
COPY agentic_ops/ ./agentic_ops/
COPY state/ ./state/

# Installation via l'installateur sécurisé 'uv'
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    /root/.local/bin/uv pip install --system --no-cache -e .

# Règle du moindre privilège : on quitte le mode root pour un utilisateur sans droits
RUN useradd -u 10001 agentic_user && \
    chown -R agentic_user:agentic_user /app
USER agentic_user

EXPOSE 8001

# Lancement automatisé via le script CLI défini dans pyproject.toml
ENTRYPOINT ["agentic-start"]
