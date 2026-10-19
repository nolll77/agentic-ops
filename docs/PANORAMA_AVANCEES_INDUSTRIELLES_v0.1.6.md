# Panorama des Avancées Industrielles (Version v0.1.6)

> **Document de Référence & Synthèse d'Ingénierie MLOps / SRE**  
> **Auteur** : Équipe MLOps / SRE  
> **Statut** : Document de Synthèse Officiel  
> **Périmètre** : Bilan exhaustif des avancées industrielles, nouvelles briques logicielles, conteneurisation et corpus documentaire v0.1.6.

---

## 1. Vue d'Ensemble des 6 Grands Piliers Développés

```text
+----------------------------------------------------------------------------------------------------+
| AGENTIC-OPS — PANORAMA DES AVANCÉES INDUSTRIELLES (VERSION v0.1.6)                                 |
+----------------------------------------------------------------------------------------------------+
|                                                                                                    |
| 1. SÉCURITÉ ZERO-TRUST & PERMUTATION DE CLÉS                                                       |
|    - AdminAPIKeyMiddleware sur /mcp, /api/diagnostics/*, /api/alerts/*, /api/llm/probe              |
|    - Comparaison en temps constant hmac.compare_digest contre clé active et clé précédente         |
|    - Secret dédié X-Grafana-Token sur le webhook et rejet des faux proxys amont                   |
|    - Gestion de clé API côté navigateur sur /console et /chat avec erreurs Render explicites       |
|                                                                                                    |
| 2. INGESTION TRANSACTIONNELLE OUTBOX & TRIAGE D'ALERTES                                            |
|    - Pattern Outbox SQLite WAL BEGIN IMMEDIATE garantissant la persistance avant l'ACK 202         |
|    - Déduplication déterministe SHA-256(tenant, service, risk_id, alertname)                       |
|    - AlertTriageWorker & AlertClassifier (alert_classification.yaml : CacDriftAlert -> DATA-042)   |
|    - Baux expirables (leases), retries exponentiels et statut Dead-Letter Queue (DLQ)              |
|                                                                                                    |
| 3. QUOTAS ATOMIQUES CONCURRENTS (RÉSOLUTION GAP P0-6)                                              |
|    - AtomicQuotaManager avec réservation glissante thread-safe sous transaction SQLite             |
|    - test_known_gaps.py passe officiellement à l'état PASSED (zéro condition de course TOCTOU)     |
|                                                                                                    |
| 4. IDENTITÉ D'ENTREPRISE MICROSOFT ENTRA ID (OIDC / SCIM) & QUORUM HITL                            |
|    - Serveur SCIM v2.0 (/scim/v2/Users, /scim/v2/Groups) pour cycle de vie des approbateurs        |
|    - Validation de tokens OIDC avec signature asymétrique JWKS et validation d'audience            |
|    - FrozenProposal liée par hash SHA-256, demandeur FSM certifié et anti-auto-approbation         |
|    - Quorum multi-groupes M-of-N avec mise en file d'exécution asynchrone durable                  |
|                                                                                                    |
| 5. INVENTAIRE LOCAL STRICT & GARDE D'EXÉCUTION                                                     |
|    - LocalInventory avec chargement YAML strict et expiration temporelle (expires_at)              |
|    - Règle INV-001 Fail-Closed : refus inconditionnel si inventaire absent, expiré ou cible inconnue|
|    - ExecutorGateway forçant SIMULATION_MODE = True, contrôle Kill-Switch et allowlist vide         |
|                                                                                                    |
| 6. OUTILLAGE SRE : SAUVEGARDE, RESTAURATION & BENCHMARKS DE RÉSILIENCE                             |
|    - CLI agentic-ops-db (backup-set, verify-set, restore-set) multi-bases SQLite + Merkle          |
|    - CLI agentic-ops-benchmark-alerts : micro-benchmarks 100/500/1000 alertes avec SIGKILL worker  |
|                                                                                                    |
+----------------------------------------------------------------------------------------------------+
```

---

## 2. Détail Technique des Nouvelles Briques Logicielles

### A. Ingestion Robuste & Triage des Alertes
- [`agentic_ops/core/alert_outbox.py`](../agentic_ops/core/alert_outbox.py) : L'alerte Grafana reçue sur `/webhook/alerts` est commitée dans la table `alerts_outbox` en mode SQLite WAL via une transaction `BEGIN IMMEDIATE` avant que le serveur ne délivre le code HTTP `202 Accepted`. L'émetteur reçoit un `tracking_id` et une URL de suivi d'état.
- [`agentic_ops/core/alert_processing.py`](../agentic_ops/core/alert_processing.py) & [`agentic_ops/entrypoints/alert_worker.py`](../agentic_ops/entrypoints/alert_worker.py) : Le worker consomme les alertes non traitées avec des baux expirables (*leases*). Le module `AlertClassifier` charge le catalogue déterministe [`agentic_ops/governance/alert_classification.yaml`](../agentic_ops/governance/alert_classification.yaml) pour mapper l'alerte vers son code de risque (`DATA-042`). Les alertes inconnues basculent en statut `REVIEW_REQUIRED` sans faux positif.

### B. Concurrence & Quotas Atomiques (Levée du gap P0-6)
- [`agentic_ops/core/atomic_quota.py`](../agentic_ops/core/atomic_quota.py) : `AtomicQuotaManager` implémente la réservation glissante sous verrou exclusif de base de données. Il élimine la condition de course TOCTOU (*Time-of-Check to Time-of-Use*). Le test de concurrence de charge [`tests/policy/test_known_gaps.py`](../tests/policy/test_known_gaps.py), qui était historiquement en `xfail`, passe désormais à 100% au vert.

### C. Identité Entreprise Microsoft Entra ID (OIDC / SCIM) & Quorum Humain
- [`agentic_ops/core/entra_oidc.py`](../agentic_ops/core/entra_oidc.py) & [`agentic_ops/core/entra_scim.py`](../agentic_ops/core/entra_scim.py) : Intégration d'un serveur SCIM v2.0 complet permettant à un annuaire d'entreprise (Microsoft Entra ID / Okta) de provisionner et déprovisionner les approbateurs, et validation cryptographique asymétrique des jetons OIDC via les clés publiques JWKS de Microsoft.
- [`agentic_ops/core/approvals.py`](../agentic_ops/core/approvals.py) & [`agentic_ops/entrypoints/approval_worker.py`](../agentic_ops/entrypoints/approval_worker.py) : Toute proposition soumise à approbation humaine est scellée par son digest SHA-256 (`proposal_hash`). Le demandeur `requester_id` est certifié par la machine à états FSM. L'auto-approbation est rejetée immédiatement (`SELF_APPROVAL_FORBIDDEN`). Dès l'obtention du quorum multi-groupes, la demande est enregistrée atomiquement dans une file `execution-outbox`.

### D. Inventaire Déterministe & Garde d'Exécution
- [`agentic_ops/core/local_inventory.py`](../agentic_ops/core/local_inventory.py) : Remplace les mocks permissifs par un chargeur d'inventaire YAML strict. L'inventaire possède un TTL d'expiration (`expires_at`). Tout inventaire absent, malformé ou expiré déclenche la règle Fail-Closed `INV-001: Target not recognized in inventory`.
- [`agentic_ops/core/executor_gateway.py`](../agentic_ops/core/executor_gateway.py) : Point de passage unique pour toute action vers l'extérieur. Le mode simulation (`SIMULATION_MODE = True`) est forcé par défaut. La passerelle vérifie la présence du fichier sentinelle de Kill-Switch (`/var/run/agentic-ops/kill-switch`).

### E. Outillage d'Exploitation SRE (Disaster Recovery & Benchmarking)
- [`agentic_ops/core/sqlite_backup.py`](../agentic_ops/core/sqlite_backup.py) & [`agentic_ops/entrypoints/sqlite_backup.py`](../agentic_ops/entrypoints/sqlite_backup.py) : La commande CLI `agentic-ops-db` permet de créer un jeu de sauvegarde cohérent (`backup-set`), de vérifier les sommes de contrôle SHA-256 et l'intégrité SQLite (`verify-set`), et de restaurer le jeu dans un répertoire isolé (`restore-set`), couvrant l'ensemble des bases (`alerts.db`, `approvals.db`, `quotas.db`, `scim.db`) et le Trust Ledger Merkle.
- [`agentic_ops/entrypoints/alert_benchmark.py`](../agentic_ops/entrypoints/alert_benchmark.py) : La commande CLI `agentic-ops-benchmark-alerts` mesure le débit et la latence P95 sur des séries de 100, 500 et 1000 alertes en simulant des pannes brutales de worker (`SIGKILL`) pour tester la ré-acquisition automatique des baux expirés.

---

## 3. Packaging, Conteneurisation & Publication

- **GitHub Container Registry (GHCR)** : Image officielle publiée : `ghcr.io/nolll77/agentic-ops:v0.1.6`
- **Multi-architecture** : `linux/amd64` et `linux/arm64`.
- **Utilisateur non-root** : `agentic_user` (UID 10001).
- **Couche conteneur assainie** sans aucun secret ni fichier de données résiduel.
- **Workflow CI/CD Coordonné** ([`.github/workflows/publish.yml`](../.github/workflows/publish.yml)) : Vérification stricte de synchronisation entre `pyproject.toml` et `Chart.yaml`, publication sur PyPI, puis construction et signature de l'image GHCR uniquement si PyPI a réussi.
- **Helm Chart Production** ([`helm/agentic-ops/`](../helm/agentic-ops/)) : Chart Kubernetes durci avec PersistentVolumeClaim (`PVC`) pour SQLite/preuves, ConfigMap d'inventaire monté en lecture seule et injection de secrets externes.

---

## 4. Corpus Documentaire Stratégique Ajouté

Le dossier `docs/` s'est enrichi de guides opérationnels chirurgicaux :

| Document | Emplacement | Rôle et Portée |
| :--- | :--- | :--- |
| Industrial Implementation Status | [`docs/INDUSTRIAL_IMPLEMENTATION_STATUS.md`](./INDUSTRIAL_IMPLEMENTATION_STATUS.md) | Matrice d'Honnêteté Radicale dissociant ce qui est testé en CI locale de ce qui requiert une qualification externe. |
| Industrial Production Blueprint | [`docs/INDUSTRIAL_PRODUCTION_BLUEPRINT.md`](./INDUSTRIAL_PRODUCTION_BLUEPRINT.md) | Spécification architecturale complète de la cible de production entreprise. |
| Profil Personnel Auto-Hébergé | [`docs/SELF_HOSTED_PRODUCTION_PATH.md`](./SELF_HOSTED_PRODUCTION_PATH.md) | Guide pratique pour qualifier une instance solo sans dépendance à un tenant Entra payant. |
| Plan d'Exécution Novembre 2026 | [`docs/SELF_HOSTED_SCOPE_EXECUTION_PLAN_NOV_2026.md`](./SELF_HOSTED_SCOPE_EXECUTION_PLAN_NOV_2026.md) | Feuille de route en 4 étapes hebdomadaires pour novembre (réconciliation des refus, pannes, répétition de backup et benchmarks). |
| Qualification Préproduction Entra | [`docs/ENTRA_PREPRODUCTION_QUALIFICATION.md`](./ENTRA_PREPRODUCTION_QUALIFICATION.md) | Procédure pas à pas d'interconnexion avec un annuaire Azure / Entra ID réel. |
| Publication d'Images GHCR | [`docs/CONTAINER_IMAGE_PUBLICATION.md`](./CONTAINER_IMAGE_PUBLICATION.md) | Traçabilité des digests et manifestes multi-arch publiés. |
| Diagnostic Console / Chat Render | [`docs/RENDER_CONSOLE_CHAT_TROUBLESHOOTING.md`](./RENDER_CONSOLE_CHAT_TROUBLESHOOTING.md) | Résolution des erreurs d'authentification sur l'instance live de démonstration. |
