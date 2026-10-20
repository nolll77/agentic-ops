# Guide de Contribution & Collaboration — Agentic-Ops

Bienvenue sur le projet **Agentic-Ops** ! Ce guide formalise les principes d'architecture, les normes de développement, les protocoles de test et les règles de gouvernance pour tous les ingénieurs et chercheurs souhaitant contribuer au projet.

---

## 1. Principes Fondateurs & Règles Constitutionnelles

Toute contribution au projet doit obligatoirement respecter ces trois invariants architecturaux :

1. **Honnêteté Radicale & Transparence Scientifique :**
   - Différencier systématiquement ce qui est qualifié en environnement de test local de ce qui exige un déploiement externe ou multi-nœuds.
   - Ne jamais revendiquer un SLO, un RPO/RTO ou une conformité de production sans métrique instrumentée et reproductible.
2. **L'IA Propose, le Code Déterministe Décide :**
   - Les Grands Modèles de Langage (LLM) sont cantonnés aux rôles d'analyse sémiotique, d'investigation et de formulation d'hypothèses (`ActionProposal`).
   - L'arbitrage de sécurité, le filtrage de cibles, le calcul de blast radius et les vetos sont exécutés à **100% par du code Python déterministe (0 token)** sans hallucination possible.
3. **Auditabilité Cryptographique Immuable :**
   - Toute décision et trace d'exécution est scellée dans un registre WORM (*Write Once, Read Many*) lié par chaîne de hash linéaire SHA-256 et vérifiable par arbre de Merkle conforme à la norme **RFC 6962**.

---

## 2. Environnement de Développement Local

Le projet exploite le gestionnaire de paquets ultra-rapide `uv` sous Python 3.11+.

### Installation

```bash
# Cloner le dépôt
git clone https://github.com/nolll77/agentic-ops.git
cd agentic-ops

# Installer les dépendances avec le groupe de développement
uv sync --all-extras

# Exécuter la suite de tests complète (231 tests)
uv run pytest tests/ -q -p no:randomly
```

### Lancement du Serveur de Développement Local

```bash
# Démarrer le plan de contrôle (Console Web sur :8001/console, Chat sur :8001/chat)
uv run agentic-start --port 8001
```

---

## 3. Chantiers Prioritaires & Roadmap Ouverte (Issues GitHub)

Les travaux de R&D et d'industrialisation sont structurés autour de 6 issues majeures :

| Issue GitHub | Sujet & Périmètre Technique | Complexité | Documentation Associée |
| :--- | :--- | :--- | :--- |
| **[#1](https://github.com/nolll77/agentic-ops/issues/1)** | **Réconciliation du Refus d'Approbation** dans l'épisode d'origine et scellage WORM. | Moyenne | `docs/SELF_HOSTED_SCOPE_EXECUTION_PLAN_NOV_2026.md` |
| **[#2](https://github.com/nolll77/agentic-ops/issues/2)** | **Exercices de Panne du Worker** et garantie *At-Least-Once Delivery* avec déduplication. | Haute | `docs/SELF_HOSTED_SCOPE_EXECUTION_PLAN_NOV_2026.md` |
| **[#3](https://github.com/nolll77/agentic-ops/issues/3)** | **Cycle de Vie de l'Inventaire Local** (`LocalInventory`), détection de drift et rechargement atomique. | Moyenne | `docs/SELF_HOSTED_SCOPE_EXECUTION_PLAN_NOV_2026.md` |
| **[#4](https://github.com/nolll77/agentic-ops/issues/4)** | **Répétition Locale Backup / Restore**, manifestes d'intégrité et rejet de corruption SQLite/WORM. | Moyenne | `agentic_ops/core/sqlite_backup.py` |
| **[#5](https://github.com/nolll77/agentic-ops/issues/5)** | **Benchmark d'Ingestion d'Alertes** et passage à l'échelle sous rafales d'alertes Loki/Prometheus. | Moyenne | `agentic_ops/entrypoints/alert_benchmark.py` |
| **[#6](https://github.com/nolll77/agentic-ops/issues/6)** | **Benchmark Empirique des LLMs Gratuits OpenRouter** selon les 5 rôles cognitifs du MAS. | Haute | `docs/OPENROUTER_FREE_MODELS_GUIDE.md` |

---

## 4. Zoom sur l'Issue #6 : Participer au Benchmark des LLMs Gratuits

Nous cherchons des contributeurs pour évaluer les modèles gratuits d'OpenRouter (`:free`) sur nos cas d'usage SRE :

1. **Rôles Cognitifs à Évaluer :**
   - `DataSpecialist` (Parsing de matrices de covariance, analyse de dérive Evidently).
   - `ModelSpecialist` (Détection d'instabilités de calibration, dérive de scores F1).
   - `InfraSpecialist` (Dépouillement de logs Grafana Loki volumineux).
   - `RemediationAgent` (Raisonnement CoT, règle du veto amont, blast radius).
   - `WebChatAssistant` (Dialogue conversationnel fluide, latence TTFT).
2. **Métriques d'Évaluation :**
   - Respect strict des schémas JSON Pydantic v2 (taux d'erreur de parsing).
   - Résistance aux attaques contradictoires par injection de prompt (`SC-101`, `SC-102`).
   - Latence roundtrip et tolérance aux rate-limits HTTP 429.

---

## 5. Workflow de Contribution (Pull Requests)

1. **Créer une branche descriptive** :
   ```bash
   git checkout -b feat/reconcile-denial-issue-1
   # ou
   git checkout -b bench/openrouter-gemma-nemotron
   ```
2. **Respecter la typographie technique** :
   Tous les noms de fonctions, classes, commandes, fichiers et variables doivent être encapsulés dans des backticks (ex: `PolicyEngine`, `ActionProposal`, `uv sync`).
3. **Valider les tests avant toute soumission** :
   ```bash
   uv run pytest tests/ -q -p no:randomly
   ```
4. **Ouvrir une Pull Request** :
   - Référencer explicitement l'issue liée (ex: `Closes #1` ou `Relates to #6`).
   - Joindre les résultats bruts des tests et les métriques de mesure.
   - Ne jamais inclure de tokens d'API, d'identifiants privés ou de données sensibles.

Merci pour votre engagement à bâtir un écosystème de supervision MLOps souverain, auditable et résilient !
