# Agentic-Ops — Feuille de Route d'Ingénierie du Model Context Protocol (`MCP`)

> **Statut du Document** : Feuille de Route Stratégique Active & Spécification Architecturale  
> **Fenêtre de Release Cible** : Versions `v0.2.0` à `v0.4.0`  
> **Entrée Officielle au Registre Anthropic** : [`io.github.nolll77/agentic-ops`](https://registry.modelcontextprotocol.io/v0.1/servers/io.github.nolll77%2Fagentic-ops/versions)  
> **Normes RFC & Réglementations** : Anthropic Model Context Protocol (`2024-11-05`), RFC 6962 (`Certificate Transparency / Merkle Tree`), RFC 8888, EU AI Act (`Règlement (UE) 2024/1689`, Articles 12 & 14)

---

## Résumé Exécutif & Invariant de Conception

La **Passerelle Model Context Protocol d'`Agentic-Ops`** (`agentic_ops/entrypoints/mcp_server.py`) opère comme un plan de contrôle gouverné reliant les agents cognitifs externes (`Claude Desktop`, `Cursor`, `Windsurf`, `Google Antigravity`, `OpenRouter`) aux infrastructures de production.

Contrairement aux passerelles d'outils CRUD conventionnelles ou non structurées, `Agentic-Ops` applique l'**Invariant du Pare-Feu Déterministe** :
> *Les modèles cognitifs proposent des hypothèses ; des noyaux Python déterministes à 0 token appliquent les frontières de règles, calculent les rayons d'impact et scellent des preuves cryptographiques immuables.*

Cette feuille de route formalise les trois prochaines phases d'ingénierie conçues pour faire évoluer la passerelle d'un point d'exécution synchrone vers un système nerveux MLOps autonome, distribué et mathématiquement vérifiable.

```text
+-------------------------------------------------------------------------------------------------+
|                       CHRONOLOGIE DE LA FEUILLE DE ROUTE D'ÉVOLUTION MCP                        |
+-------------------------------------------------------------------------------------------------+
|                                                                                                 |
|   PHASE 1 : Sondes Sensorielles Temps Réel & Télémétrie en Streaming                           |
|   ------------------------------------------------------------                                  |
|   * Transport Server-Sent Events (`SSE`) en direct aux côtés du flux HTTP JSON-RPC 2.0.          |
|   * Télémétrie découpée & streaming de dérive Evidently AI via les ressources MCP.             |
|   * Échantillonnage dynamique de prompts (`sampling/createMessage`) pour validation opérateur.  |
|                                                                                                 |
|   PHASE 2 : Auditabilité Cryptographique & Conformité EU AI Act                                 |
|   ------------------------------------------------------------                                  |
|   * Outil natif `verify_ledger_inclusion` exposant des preuves Merkle RFC 6962 en O(log N).     |
|   * Audit en direct de la chaîne linéaire WORM (`SHA-256` + `HMAC-SHA512`) via JSON-RPC.       |
|   * Attestation directe de conformité pour systèmes IA à haut risque (Articles 12 & 14).        |
|                                                                                                 |
|   PHASE 3 : Quorum Multi-Agents Judiciaire & Maillage Souverain                                 |
|   ------------------------------------------------------------                                  |
|   * Séparation des Pouvoirs : Agent Proposeur vs Quorum d'Agents Inspecteurs / Auditeurs.       |
|   * Repli souverain hors-cloud : routage d'outils via le maillage chiffré Tailscale.            |
|   * Isolation multi-clusters & exécution zero-trust en environnement étanche (air-gapped).     |
|                                                                                                 |
+-------------------------------------------------------------------------------------------------+
```

---

## Phase 1 : Sondes Sensorielles Temps Réel & Streaming de Télémétrie (`Livré en v0.2.0`)

### 1.1 Objectif & Contexte
`Agentic-Ops` expose désormais **11 outils gouvernés** et **8 ressources** via HTTP synchrone `POST /mcp` (JSON-RPC 2.0), `GET /mcp/events` (`Server-Sent Events`) et `stdio` local, permettant une observation sensorielle continue non bloquante sans boucles de scrutation (*polling*) côté client.

### 1.2 Livrables Architecturaux

1. **Prise en Charge Double Transport (`SSE` + `HTTP Streamable`)** :
   - Point de terminaison natif Server-Sent Events (`SSE`) sur `GET /mcp/events` parallèlement au `POST /mcp` existant (`agentic_ops/entrypoints/mcp_sse.py`).
   - Rétrocompatibilité intégrale avec la spécification Anthropic MCP `2024-11-05`.
   - Battement de cœur (`: ping`), en-tête `Mcp-Session-Id` et rejeu à la reconnexion via `Last-Event-ID` sur l'historique en mémoire.

2. **Diffusion Continue de Télémétrie via Ressources Dynamiques** :
   - Schémas d'URI dynamiques (`agentic_ops/core/telemetry_stream.py`) :
     - `mlops://telemetry/live/drift` : Relaie `drift_share` et `n_drifted_columns` du rapport `Evidently AI` via `CacPullCollector` lorsque `MCP_TELEMETRY_SOURCE=cac_pull`, ou émet par défaut une ligne de base explicitement étiquetée `source="simulated"` (aucune fausse dérive fabriquée).
     - `mlops://telemetry/live/latency` : Quantiles (`p50`/`p95`/`p99`) interpolés depuis l'histogramme Prometheus local `agentic_ops_llm_latency_seconds` (mesurant les appels LLM propres à `Agentic-Ops`, étiqueté `source="agentic_ops_local"`).
   - Les LLMs externes s'abonnent aux notifications (`resources/subscribe` $\rightarrow$ `notifications/resources/updated`) sur session `SSE` active.

3. **Échantillonnage Dynamique de Prompts (`sampling/createMessage`)** :
   - Outil gouverné `request_client_sampling` (`agentic_ops/entrypoints/mcp_transport.py`) déléguant une analyse heuristique locale au modèle client connecté (`STDIO` ou `HTTP+SSE`) ayant déclaré `capabilities.sampling`.
   - Encapsule systématiquement la réponse du modèle client dans `prompt_guard.wrap_untrusted(..., source="client_sampling")` avec `includeContext="none"`.

### 1.3 Critères de Vérification Technique
- [x] Test de charge SSE : soutenir 50 connexions de streaming concurrentes avec une latence de distribution d'événements $< 15\,\text{ms}$ *(vérifié dans `tests/entrypoints/test_mcp_sse.py` : latence fan-out in-process $p_{50} = 2.40\,\text{ms}$, $p_{95} = 4.78\,\text{ms}$, $\max = 5.34\,\text{ms}$ sur 50 flux concurrents)*.
- [x] Boucle d'événements non bloquante : s'assurer que la télémétrie sensorielle en direct ne bloque pas les appels d'outils synchrones dans `mcp_server.py` *(vérifié via collecteurs `asyncio.to_thread`, files bornées drop-oldest et `run_in_threadpool` dans `test_mcp_sse.py` & `test_mcp_sampling.py`)*.
- [x] Validation de schéma sans dérive : s'assurer que tous les flux d'événements respectent les schémas stricts Pydantic v2 (`TelemetrySnapshot` avec `ConfigDict(extra="forbid")`).

---

## Phase 2 : Auditabilité Cryptographique & Conformité EU AI Act (`Livré en v0.2.0`)

### 2.1 Objectif & Contexte
Les cadres réglementaires encadrant les systèmes autonomes — au premier rang desquels le **Règlement sur l'Intelligence Artificielle de l'Union Européenne (`Règlement (UE) 2024/1689`)** — imposent une journalisation rigoureuse (Article 12 : *Tenue de registres*) et une surveillance humaine effective (Article 14 : *Contrôle humain*) pour les systèmes d'IA à haut risque opérant sur des infrastructures critiques.

La Phase 2 intègre la génération de preuves mathématiques formelles et l'export d'éléments probants techniques en lecture seule directement au niveau du protocole MCP *(outil de preuve technique, ne constituant pas à lui seul une évaluation juridique de conformité)*.

### 2.2 Livrables Architecturaux

1. **Outil Gouverné Natif `verify_ledger_inclusion`** :
   - Exposer un nouvel outil de gouvernance :
     ```python
     def verify_ledger_inclusion(
         episode_id: str,
         leaf_index: int,
         expected_merkle_root: str
     ) -> Dict[str, Any]:
         """Vérifie le chemin d'audit RFC 6962 en complexité O(log N)."""
     ```
   - Connecté directement à `agentic_ops/core/merkle.py` (`MerkleTree`).
   - Restitue un certificat d'audit de preuve structuré :
     - Hashes des nœuds frères du chemin d'audit : `[{"position": "left"|"right", "hash": "..."}]`.
     - Verdict d'égalité entre racine calculée et racine attendue (`VALID_AUTHENTICATED_INCLUSION_PROOF` / `ROOT_MISMATCH` / `TAMPERING_OR_INVALID_PROOF`).
     - Complexité de vérification computationnelle : $\mathcal{O}(\log_2 N)$ opérations de hachage.

2. **Dossier de Conformité Automatisé EU AI Act Article 12** :
   - Ressource MCP `mlops://compliance/eu-ai-act/article-12/audit-pack` (`agentic_ops/core/compliance_pack.py`) fournissant un export consolidé en lecture seule scellé par `HMAC-SHA512` comprenant :
     - État d'intégrité du journal WORM (`ledger.jsonl`), racine `Merkle` et compteurs de décisions/états FSM.
     - Continuité de la chaîne linéaire `SHA-256` et validité des signatures `HMAC-SHA512`.
     - Règles actives du `PolicyBundle`, empreinte de version et résumé du catalogue d'actions.
     - Statistiques d'approbation humaine en lecture seule (`ApprovalRepo.stats()`) avec traçabilité explicite `signing_key_provenance` (`CONFIGURED` vs `INSECURE_DEFAULT_DUMMY_KEY`) et `third_party_verifiable: false`.

3. **Preuve de Rejet d'Altération en CI/CD** :
   - Tests contradictoires automatisés validant que toute altération d'un seul bit dans l'historique des épisodes ou du pack d'audit provoque l'échec immédiat de la vérification (`tests/adversarial/test_merkle_tree.py`, `tests/core/test_compliance_pack.py`).

### 2.3 Critères de Vérification Technique
- [x] La génération de preuve en $\mathcal{O}(\log N)$ s'exécute en $< 2\,\text{ms}$ pour des registres dépassant $10^5$ épisodes *(vérifié dans `tests/adversarial/test_merkle_tree.py` : `0.040 ms` pour la génération et `0.047 ms` pour la vérification sur un `MerkleTree` pré-indexé de $100\,005$ feuilles ; un appel à froid de `EvidenceStore.get_merkle_proof` effectue toujours une lecture initiale $\mathcal{O}(N)$ de `ledger.jsonl`)*.
- [x] Suite cryptographique intégralement validée par les tests automatisés dans `tests/entrypoints/test_mcp_server.py` et `tests/core/test_compliance_pack.py`.
- [x] Conformité stricte à 100% avec la norme RFC 6962 pour le préfixe de hachage des feuilles (`0x00`) et des nœuds intérieurs (`0x01`).

---

## Phase 3 : Quorum Multi-Agents Judiciaire & Maillage Souverain (`3.1 Livré en v0.2.0` · `3.2–3.3 Planifié v0.3.0+`)

### 3.1 Objectif & Contexte
Autoriser un agent d'IA unique ou un fournisseur LLM exclusif à la fois à élaborer un plan de remédiation et à valider sa propre sécurité crée un point de défaillance unique et un biais cognitif systémique inacceptable. La Phase 3 implémente une **Gouvernance par Quorum Judiciaire** (`Livré en v0.2.0`) et des **Replis par Maillage Réseau Souverain** (`Planifié`).

### 3.2 Livrables Architecturaux

```text
                               +----------------------------------+
                               |      INCIDENT DÉTETECTÉ VIA      |
                               |    STREAMING TÉLÉMÉTRIE (P1)     |
                               +-----------------+----------------+
                                                 |
                                                 v
                               +----------------------------------+
                               |   AGENT PROPOSEUR (ex: Claude)   |
                               | Formule une ActionProposal :     |
                               | "Scale réplicas + flush buffer"  |
                               +-----------------+----------------+
                                                 |
                                                 v
           +-------------------------------------+-------------------------------------+
           |                                                                           |
           v                                                                           v
+-----------------------+                                                   +-----------------------+
|    NOYAU DÉTERMINISTE |                                                   |    AGENT INSPECTEUR   |
| (Moteur de Règles)    |                                                   |   (Quorum Judiciaire) |
| Python pur 0 Token    |                                                   | Modèle Indépendant    |
| * Rayon impact < 0.2  |                                                   | (ex: Gemma 4 vs       |
| * Quota de fréquence  |                                                   |  NVIDIA Nemotron)     |
| * Masquage amont      |                                                   | * Évalue hypothèses   |
+-----------+-----------+                                                   +-----------+-----------+
            |                                                                           |
            +-------------------------------------+-------------------------------------+
                                                  |
                                                  v
                               +----------------------------------+
                               |    PORTE D'ACCORD & EXÉCUTION    |
                               | Les DEUX avis doivent être PASS  |
                               | Si accord  -> Exécution & WORM   |
                               | Si veto    -> Annulation & Log   |
                               +----------------------------------+
```

1. **Séparation Judiciaire des Pouvoirs (Proposeur vs Inspecteur)** *(Livré en `v0.2.0` — `agentic_ops/core/inspector_agent.py`, opt-in via `AGENTIC_OPS_INSPECTOR_ENABLED=true`)* :
   - Découplage des rôles cognitifs durant la remédiation d'incidents :
     - **Agent Proposeur (`RemediationAgent`)** : Formule l'`ActionIntent` / `ActionProposal` (`nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free` par défaut).
     - **Agent Inspecteur (`InspectorAgent`, rôle `"inspector"`)** : Opère sous une famille de LLM distincte (`google/gemma-4-31b-it:free` par défaut) avec isolation `prompt_guard.wrap_untrusted`.
   - **Durcissement Monotone & Fail-Closed** : `apply_inspector_verdict` ne peut QUE durcir un `ALLOW` du `PolicyEngine` en `DENY` (sur `VETO`) ou en `REQUIRE_APPROVAL` (*fail-closed* sur erreur/timeout LLM) ; il ne peut jamais assouplir un `DENY` ou `REQUIRE_APPROVAL`.

2. **Routage sur Maillage Chiffré Souverain (`Tailscale` + `Ollama`)** *(Planifié — `v0.3.0+`)* :
   - Approfondir l'intégration avec `agentic_ops/adapters/cac_pull_collector.py` et les réseaux privés maillés.
   - En cas de partition cloud, de limitation de débit (`HTTP 429`) ou de rupture d'accès externe :
     - Le serveur MCP bascule automatiquement les appels d'outils et l'évaluation des prompts sur des tunnels WireGuard chiffrés (`Tailscale`) vers des nœuds d'inférence souverains locaux (`Ollama` exécutant `qwen2.5-coder` ou `deepseek-r1`).
     - Garantit une capacité d'intervention d'urgence 100% étanche (air-gapped) sans dépendance cloud externe.

3. **Fédération Multi-Clusters** *(Planifié — `v0.4.0`)* :
   - Permettre à une passerelle MCP `Agentic-Ops` maîtresse d'orchestrer des nœuds travailleurs répartis sur des clusters Kubernetes et des serveurs physiques hétérogènes via TLS mutuel authentifié (`mTLS`) ou sur-réseaux WireGuard.

### 3.3 Critères de Vérification Technique
- [x] Consensus du quorum judiciaire validé sous des simulations d'injection de prompt contradictoires (`SC-101`, `SC-102`) *(vérifié dans `tests/core/test_inspector_agent.py::test_judicial_quorum_under_sc101_and_sc102_adversarial_injections`, `forbidden_executed=0`)*.
- [ ] Bascule automatique vers le nœud souverain local exécutée en $< 500\,\text{ms}$ en cas de défaillance d'API externe *(planifié pour `v0.3.0+`)*.
- [x] Zéro régression sur la suite existante de tests unitaires et d'intégration *(`288 passed, 3 skipped, 0 failed` en `v0.2.0`)*.

---

## Matrice des Invariants Techniques à Travers Toutes les Phases

| Jalon d'Ingénierie | Protocole de Transport | Garantie de Sécurité | Norme Cryptographique | Mode de Contrôle Humain |
| :--- | :--- | :--- | :--- | :--- |
| **Socle (`v0.1.14`)** | HTTP Streamable / Stdio | PolicyEngine Déterministe (0 token) | Chaîne SHA-256 + HMAC-SHA512 + Merkle RFC 6962 | Slack HITL (L2/L3) |
| **Actuel (`v0.2.0` — P1 + P2 + P3.1)** | SSE (`GET /mcp/events`) + HTTP Streamable + Stdio | Télémétrie non bloquante + Merkle $\mathcal{O}(\log N)$ + Quorum monotone `InspectorAgent` | Preuves Merkle RFC 6962 + Pack signé Art. 12 EU AI Act | Slack HITL + `sampling/createMessage` + Quorum Fail-Closed |
| **Planifié (`v0.3.0+` — P3.2 & P3.3)** | Double Maillage (HTTP + WireGuard + `mTLS`) | Bascule souveraine `< 500 ms` `Tailscale`/`Ollama` + Isolation multi-clusters | Consensus multi-parties + Ancrage WORM externe | Quorum souverain air-gapped + Opérateur |

---

## Contribution Communautaire & Correspondance des Issues

Les ingénieurs et chercheurs souhaitant participer à l'implémentation de ces jalons sont invités à consulter :
- **Guide de Contribution** : [`CONTRIBUTING.md`](../CONTRIBUTING.md) (Version française : [`docs/CONTRIBUTING_FR.md`](CONTRIBUTING_FR.md))
- **Issues GitHub Associées** :
  - **[Issue #1](https://github.com/nolll77/agentic-ops/issues/1)** : Raccordement formel du refus opérateur à l'épisode d'origine dans le registre WORM.
  - **[Issue #2](https://github.com/nolll77/agentic-ops/issues/2)** : Garantie d'au moins une livraison, injection de crash et reprise sur incident de worker.
  - **[Issue #6](https://github.com/nolll77/agentic-ops/issues/6)** : Évaluation empirique des LLMs gratuits OpenRouter pour le rôle d'Inspecteur du Quorum.
