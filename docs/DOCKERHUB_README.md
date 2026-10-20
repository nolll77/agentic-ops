# Agentic-Ops: Deterministic Multi-Agent Control Plane for MLOps & SRE Governance

[![PyPI - Version](https://img.shields.io/pypi/v/agentic-ops?color=blue&logo=pypi&logoColor=white)](https://pypi.org/project/agentic-ops/)
[![Docker Hub](https://img.shields.io/badge/Docker%20Hub-nolll78%2Fagentic--ops-blue?logo=docker&logoColor=white)](https://hub.docker.com/r/nolll78/agentic-ops)
[![GHCR](https://img.shields.io/badge/GHCR-ghcr.io%2Fnolll77-blue?logo=github)](https://github.com/nolll77/agentic-ops/pkgs/container/agentic-ops)
[![GitHub](https://img.shields.io/badge/GitHub-nolll77%2Fagentic--ops-black?logo=github)](https://github.com/nolll77/agentic-ops)
[![Tests](https://img.shields.io/badge/Tests-231%20Passed-brightgreen)](https://github.com/nolll77/agentic-ops/actions)

**Agentic-Ops** is an autonomous, deterministic Multi-Agent System (MAS) designed to investigate, diagnose, and remediate operational MLOps signals (Data Drift, Concept Drift, Model Staleness, OOMKilled Pods, Latency Spikes) under strict Site Reliability Engineering (SRE) governance.

Unlike open-ended agentic frameworks, **Agentic-Ops** enforces a **Zero-Trust, Fail-Closed Security Model**:
- **Deterministic Policy Engine**: Pre-execution vetoes (`DENY`), rate-limiting, and human-in-the-loop (`HITL`) approval gateways.
- **WORM Trust Ledger**: Append-only cryptographic audit trail with RFC 6962 binary Merkle trees.
- **Hexagonal Architecture**: Complete domain decoupling driven by declarative YAML policies.
- **Multi-Role MAS Routing**: Specialized agents (`DataSpecialist`, `ModelSpecialist`, `InfraSpecialist`, `RemediationAgent`, `WebChatAssistant`).

---

## Quickstart: Run with Docker

The official container image is multi-architecture (`linux/amd64` and `linux/arm64`):

```bash
# 1. Pull the official image
docker pull nolll78/agentic-ops:latest

# 2. Run the complete Control Plane
docker run -d -p 8000:8000 --name agentic-ops nolll78/agentic-ops:latest
```

### Available Endpoints & Interfaces

Once started, access the built-in services in your browser:
- 🤖 **Web Chat Assistant**: [http://localhost:8000/chat](http://localhost:8000/chat)
- 🖥️ **Live SRE Console & MAS Topology**: [http://localhost:8000/console](http://localhost:8000/console)
- 📚 **Interactive Swagger API**: [http://localhost:8000/docs](http://localhost:8000/docs)
- 🔌 **Model Context Protocol (MCP)**: [http://localhost:8000/mcp](http://localhost:8000/mcp)
- 📊 **Prometheus Metrics**: [http://localhost:8000/metrics](http://localhost:8000/metrics)

---

## Configuration & Environment Variables

You can pass environment variables to configure external LLMs or admin credentials:

```bash
docker run -d -p 8000:8000 \
  -e ADMIN_API_KEY="your-secret-key" \
  -e OPENROUTER_API_KEY="sk-or-v1-..." \
  -e DEFAULT_LLM_MODEL="google/gemini-2.0-flash-exp:free" \
  --name agentic-ops \
  nolll78/agentic-ops:latest
```

---

## Links & Documentation

- **GitHub Repository**: [https://github.com/nolll77/agentic-ops](https://github.com/nolll77/agentic-ops)
- **PyPI Package**: [https://pypi.org/project/agentic-ops/](https://pypi.org/project/agentic-ops/)
- **GitHub Container Registry**: [ghcr.io/nolll77/agentic-ops](https://github.com/nolll77/agentic-ops/pkgs/container/agentic-ops)
- **Live Demo & Sandbox**: [https://agentic-ops-5ebv.onrender.com/chat](https://agentic-ops-5ebv.onrender.com/chat)
- **Community Guide & Issues**: [CONTRIBUTING.md](https://github.com/nolll77/agentic-ops/blob/main/CONTRIBUTING.md)
