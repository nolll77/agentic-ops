# 🛡️ Agentic-Ops Control Plane

![Status](https://img.shields.io/badge/Status-Production%20Hardened-success)
![Security](https://img.shields.io/badge/Security-Red%20Teamed-critical)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Architecture](https://img.shields.io/badge/Architecture-Hexagonal-purple)

**Agentic-Ops** est un *Control Plane MLOps* de classe entreprise conçu pour orchestrer des Agents IA (LLMs) dans la résolution d'incidents de production (Data Drift, Model Staleness, OOMKilled Pods). 

Contrairement aux frameworks d'agents classiques (LangChain, AutoGen) qui privilégient l'autonomie absolue, Agentic-Ops est bâti sur les piliers du **SRE (Site Reliability Engineering)** : Déterminisme, Observabilité, Sécurité Distribuée (Fail-Closed) et Human-in-the-Loop (HITL) asynchrone.

---

## 🏗️ Architecture Globale

Le système repose sur une **Architecture Hexagonale** (Ports & Adapters) couplée à une **Machine à États Finis (FSM)**.

1. **Orchestrator (FSM)** : Coordonne le cycle de vie strict d'un incident (`SIGNAL_RECEIVED` → `DIAGNOSIS` → `PLANNING` → `APPROVAL` → `EXECUTION` → `RESOLVED`).
2. **Policy Engine** : Le cerveau de la gouvernance. Évalue chaque proposition d'action de l'IA contre un manifeste YAML strict (`autonomy_policy.yaml`) pour décider si l'action est autorisée, refusée, ou nécessite une approbation humaine.
3. **Trust Ledger (Evidence Store)** : Le registre cryptographique immuable (WORM). Chaque transition d'état et décision est logguée, hachée, et signée.
4. **Agent Tools (Sandboxing)** : Outils mis à disposition des LLMs, confinés au niveau de l'OS.

---

## 🔥 Fonctionnalités Clés & Sécurité (Hardening)

Ce dépôt a subi un audit architectural offensif (*Red-Teaming*) exhaustif et a été corrigé pour résister aux failles des systèmes distribués critiques.

### 1. Sécurité Distribuée & Concurrence (Redis)
- **Rate Limiting Atomique** : Limite le nombre d'actions destructrices (ex: `restart_pod: 10/hour`). Utilise des pipelines atomiques Redis (`INCR` + `EXPIRE`) pour garantir qu'aucune *Race Condition* ne survient en environnement multi-réplicas.
- **Idempotence Sémantique** : L'Orchestrateur utilise des verrous distribués Redis (`SET NX EX`) basés sur l'empreinte sémantique de l'incident (`tenant:env:service:risk_id`). Élimine les risques de double exécution après un crash.
- **Fail-Closed Governance** : Le `PolicyEngine` parse les règles de sécurité via des schémas Pydantic stricts. La moindre faute de frappe dans le YAML ou l'indisponibilité du cache Redis fait crasher le système (Fail-Safe), empêchant une autorisation par défaut.

### 2. Isolation & Sandboxing des Outils
- **OS-Level Isolation** : L'exécution d'un "Tool" par l'IA ne se fait pas dans un thread, mais dans un sous-processus isolé (`multiprocessing.Process`). 
- **Timeouts Stricts** : En cas de dépassement, le processus enfant subit un `process.terminate()` implacable, empêchant l'accumulation de tâches bloquées et les fuites de ressources.
- **K8s RBAC Whitelisting** : L'adaptateur d'exécution Kubernetes bloque toute tentative d'élévation de privilèges (ex: modification du `serviceAccountName`) via une liste blanche stricte de requêtes JSON Patch.

### 3. Traçabilité Cryptographique WORM
- **Canonicalisation** : Tous les événements (Episodes) sont sérialisés de manière canonique (`sort_keys=True`).
- **Signature KMS Asymétrique** : Les historiques d'incidents sont signés cryptographiquement (`HMAC-SHA512`) avec une clé privée.
- **WORM Abstraction** : Conçu pour s'interfacer avec AWS S3 Object Lock ou GCP Retention Policy. Il est mathématiquement impossible de forger ou d'altérer l'historique des actions de l'IA sans invalider la chaîne.

### 4. Human-In-The-Loop (HITL) Asynchrone
- **Webhook Slack Sécurisé** : L'approbation humaine asynchrone repose sur un webhook FastAPI qui vérifie cryptographiquement l'origine via `X-Slack-Signature` et `HMAC-SHA256`.
- **Anti Replay-Attacks** : Blocage des requêtes âgées de plus de 5 minutes.
- **Allowlist Décisionnelle** : Seules les décisions pures (`APPROVE`, `DENY`) sont acceptées, avec vérification de l'atomicité de la consommation de l'approbation.

### 5. Résilience Financière & Organisationnelle
- **FinOps Circuit Breaker** : Suivi des appels LLM en temps réel. Coupe l'accès aux API OpenAI/Anthropic en cas de "Monitoring Storm" (ex: Datadog envoie 1000 alertes/min) pour protéger le budget, basculant sur une remédiation déterministe.
- **Shadow Mode (A/B Testing de Sécurité)** : Possibilité de tester une nouvelle politique de sécurité stricte "à blanc". L'Orchestrateur évalue le `shadow_policy.yaml` en parallèle du manifeste primaire et loggue les divergences sans jamais consommer les quotas de production.
- **Organizational Memory (RAG)** : L'IA ne devine pas. Elle effectue une recherche vectorielle dans la base des *Runbooks* et des *Post-Mortems* passés de l'entreprise avant de proposer un plan de remédiation.

---

## 📊 Télémétrie & Observabilité

L'application expose des métriques de niveau SRE via **Prometheus** :
- `agentic_ops_fsm_transitions_total` : Suivi de la Machine à États.
- `agentic_ops_policy_decisions_total` : Ratio des `ALLOW`, `DENY`, et `REQUIRE_APPROVAL`.
- `agentic_ops_circuit_breaker_status` : Déclenchement du coupe-circuit FinOps.
*(Note : Conception stricte évitant la Cardinality Explosion. Aucun UUID n'est passé en label).*

---

## 🚀 Installation & Utilisation

```bash
# 1. Cloner et préparer l'environnement
git clone https://github.com/nolll77/agentic-ops.git
cd agentic-ops-core
uv venv .venv
source .venv/bin/activate
uv pip install -e .

# 2. Exécuter la suite de régression de sécurité (Red-Team)
PYTHONPATH=. pytest tests/security/

# 3. Lancer la TUI d'Audit du Trust Ledger
python -m agentic_ops.cli.trust_ledger list
```

## 🛡️ Tests de Sécurité (Test-Driven Security)

La robustesse de ce Control Plane est vérifiée par une **Security Regression Suite** dédiée (`tests/security/`), issue d'un audit de Red-Teaming, incluant :
- Détection des falsifications d'Evidence Store (`test_episode_tampering_is_detectable`).
- Invariants de concurrence locale sur l'Exécuteur.
- Comportement Fail-Closed du moteur de gouvernance.
