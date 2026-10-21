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

## Phase 1 : Sondes Sensorielles Temps Réel & Streaming de Télémétrie

### 1.1 Objectif & Contexte
Actuellement, `Agentic-Ops` expose 8 outils gouvernés et 5 ressources de connaissance via HTTP synchrone `POST /mcp` (JSON-RPC 2.0 avec streaming de chunks) et `stdio` local. Bien qu'adaptée aux requêtes transactionnelles, la réponse aux incidents MLOps à haute cadence exige une observation sensorielle continue sans boucles de scrutation (*polling*) côté client.

### 1.2 Livrables Architecturaux

1. **Prise en Charge Double Transport (`SSE` + `HTTP Streamable`)** :
   - Introduire un point de terminaison natif Server-Sent Events (`SSE`) sur `GET /mcp/events` parallèlement au `POST /mcp` existant.
   - Préserver une rétrocompatibilité intégrale avec la spécification Anthropic MCP `2024-11-05`.
   - Gérer le battement de cœur (*heartbeat*) et la reconnexion automatique des sessions clientes sans perte d'état.

2. **Diffusion Continue de Télémétrie via Ressources Dynamiques** :
   - Exposer des schémas d'URI dynamiques :
     - `mlops://telemetry/live/drift` : Streaming continu des métriques de distance de Wasserstein et de Kolmogorov-Smirnov calculées par `Evidently AI`.
     - `mlops://telemetry/live/latency` : Flux de latence P95/P99 sub-seconde collecté depuis les points de terminaison Prometheus.
   - Les LLMs externes peuvent s'abonner aux notifications de ressources (`notifications/resources/updated`) plutôt que de scruter périodiquement `poll_target_mlops_snapshot`.

3. **Échantillonnage Dynamique de Prompts (`sampling/createMessage`)** :
   - Implémenter l'échantillonnage de requêtes initié par le serveur MCP, permettant au plan de contrôle de déléguer une analyse heuristique locale au modèle client connecté.
   - Permet une étape de validation humaine interactive (*Human-in-the-Loop* / `HITL`) au sein des environnements de développement (`Cursor`, `Claude Desktop`) avant d'exécuter des actions de niveau `REQUIRE_APPROVAL`.

### 1.3 Critères de Vérification Technique
- [ ] Test de charge SSE : soutenir 50 connexions de streaming concurrentes avec une latence de distribution d'événements $< 15\,\text{ms}$.
- [ ] Boucle d'événements non bloquante : s'assurer que la télémétrie sensorielle en direct ne bloque pas les appels d'outils synchrones dans `mcp_server.py`.
- [ ] Validation de schéma sans dérive : s'assurer que tous les flux d'événements respectent les schémas stricts Pydantic v2 (`TelemetrySnapshot`).

---

## Phase 2 : Auditabilité Cryptographique & Conformité EU AI Act

### 2.1 Objectif & Contexte
Les cadres réglementaires encadrant les systèmes autonomes — au premier rang desquels le **Règlement sur l'Intelligence Artificielle de l'Union Européenne (`Règlement (UE) 2024/1689`)** — imposent une journalisation rigoureuse (Article 12 : *Tenue de registres*) et une surveillance humaine effective (Article 14 : *Contrôle humain*) pour les systèmes d'IA à haut risque opérant sur des infrastructures critiques.

La Phase 2 intègre la génération de preuves mathématiques formelles directement au niveau du protocole MCP.

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
   - Connecté directement à `agentic_ops/core/merkle_tree.py` (`RFC6962MerkleTree`).
   - Restitue un certificat d'audit de preuve structuré :
     - Hashes des nœuds frères du chemin d'audit : `[\"0x00...\", \"0x01...\"]`.
     - Verdict d'égalité entre racine calculée et racine attendue (`MATCH` / `TAMPERING_DETECTED`).
     - Complexité de vérification computationnelle : $\mathcal{O}(\log_2 N)$ opérations de hachage.

2. **Dossier de Conformité Automatisé EU AI Act Article 12** :
   - Exposer une ressource MCP `mlops://compliance/eu-ai-act/article-12/audit-pack` fournissant un export consolidé et signé numériquement comprenant :
     - Journal d'événements WORM continu (`ledger.jsonl`).
     - Certificat de continuité de la chaîne linéaire de hashes SHA-256.
     - Traces de décisions déterministes du Moteur de Règles avec journaux de vetos à 0 token (`R-001` à `R-005`).
     - Enregistrements des approbations humaines signés par HMAC-SHA512.

3. **Preuve de Rejet d'Altération en CI/CD** :
   - Ajouter des cas de tests contradictoires automatisés validant que toute altération d'un seul bit dans l'historique des épisodes provoque l'échec immédiat de la vérification avec codes diagnostics précis.

### 2.3 Critères de Vérification Technique
- [ ] La génération de preuve en $\mathcal{O}(\log N)$ s'exécute en $< 2\,\text{ms}$ pour des registres dépassant $10^5$ épisodes.
- [ ] Suite cryptographique intégralement validée par les tests automatisés dans `tests/entrypoints/test_mcp_server.py`.
- [ ] Conformité stricte à 100% avec la norme RFC 6962 pour le préfixe de hachage des feuilles (`0x00`) et des nœuds intérieurs (`0x01`).

---

## Phase 3 : Quorum Multi-Agents Judiciaire & Maillage Souverain

### 3.1 Objectif & Contexte
Autoriser un agent d'IA unique ou un fournisseur LLM exclusif à la fois à élaborer un plan de remédiation et à valider sa propre sécurité crée un point de défaillance unique et un biais cognitif systémique inacceptable. La Phase 3 implémente une **Gouvernance par Quorum Judiciaire** et des **Replis par Maillage Réseau Souverain**.

### 3.2 Livrables Architecturaux

```text
                               +----------------------------------+
                               |      INCIDENT DÉTECTÉ VIA        |
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
| * Rayon impact < 0.2  |                                                   | (ex: DeepSeek / Llama |
| * Quota de fréquence  |                                                   | via nœud souverain)   |
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

1. **Séparation Judiciaire des Pouvoirs (Proposeur vs Inspecteur)** :
   - Découplage des rôles cognitifs durant la remédiation d'incidents :
     - **Agent Proposeur** : Génère des hypothèses de diagnostic et soumet une proposition d'action (`ActionProposal`).
     - **Agent Inspecteur (Auditeur)** : Opère sous une famille de LLM distincte avec des contraintes de prompt indépendantes. Il audite la proposition pour identifier tout effet de bord masqué, hypothèse non démontrée ou masquage de dérive.
   - Toute exécution est bloquée tant que le **Moteur de Règles Déterministe** ET le **Quorum d'Inspecteurs** n'ont pas émis un accord unanime.

2. **Routage sur Maillage Chiffré Souverain (`Tailscale` + `Ollama`)** :
   - Approfondir l'intégration avec `agentic_ops/adapters/cac_pull_collector.py` et les réseaux privés maillés.
   - En cas de partition cloud, de limitation de débit (`HTTP 429`) ou de rupture d'accès externe :
     - Le serveur MCP bascule automatiquement les appels d'outils et l'évaluation des prompts sur des tunnels WireGuard chiffrés (`Tailscale`) vers des nœuds d'inférence souverains locaux (`Ollama` exécutant `qwen2.5-coder` ou `deepseek-r1`).
     - Garantit une capacité d'intervention d'urgence 100% étanche (air-gapped) sans dépendance cloud externe.

3. **Fédération Multi-Clusters** :
   - Permettre à une passerelle MCP `Agentic-Ops` maîtresse d'orchestrer des nœuds travailleurs répartis sur des clusters Kubernetes et des serveurs physiques hétérogènes via TLS mutuel authentifié (`mTLS`) ou sur-réseaux WireGuard.

### 3.3 Critères de Vérification Technique
- [ ] Consensus du quorum judiciaire validé sous des simulations d'injection de prompt contradictoires (`SC-101`, `SC-102`).
- [ ] Bascule automatique vers le nœud souverain local exécutée en $< 500\,\text{ms}$ en cas de défaillance d'API externe.
- [ ] Zéro régression sur la suite existante de 231 tests unitaires et d'intégration.

---

## Matrice des Invariants Techniques à Travers Toutes les Phases

| Jalon d'Ingénierie | Protocole de Transport | Garantie de Sécurité | Norme Cryptographique | Mode de Contrôle Humain |
| :--- | :--- | :--- | :--- | :--- |
| **Actuel (`v0.1.14`)** | HTTP Streamable / Stdio | PolicyEngine Déterministe (0 token) | Chaîne SHA-256 + HMAC-SHA512 + Merkle RFC 6962 | Slack HITL (L2/L3) |
| **Phase 1 (`v0.2.0`)** | SSE + HTTP Streamable | Bac à sable de télémétrie non bloquant | Idem v0.1.14 + empreinte de flux continu | Échantillonnage de Prompt dans l'IDE |
| **Phase 2 (`v0.3.0`)** | SSE + HTTP Streamable | Vérification d'inclusion en $\mathcal{O}(\log N)$ | Preuves Merkle RFC 6962 + Pack Art. 12 EU AI Act | Attestation Cryptographique |
| **Phase 3 (`v0.4.0`)** | Double Maillage (HTTP + WireGuard) | Quorum Multi-Agents Judiciaire + Veto | Consensus multi-parties + Scellement WORM | Quorum multi-agents + Opérateur |

---

## Contribution Communautaire & Correspondance des Issues

Les ingénieurs et chercheurs souhaitant participer à l'implémentation de ces jalons sont invités à consulter :
- **Guide de Contribution** : [`CONTRIBUTING.md`](../CONTRIBUTING.md) (Version française : [`docs/CONTRIBUTING_FR.md`](CONTRIBUTING_FR.md))
- **Issues GitHub Associées** :
  - **[Issue #1](https://github.com/nolll77/agentic-ops/issues/1)** : Raccordement formel du refus opérateur à l'épisode d'origine dans le registre WORM.
  - **[Issue #2](https://github.com/nolll77/agentic-ops/issues/2)** : Garantie d'au moins une livraison, injection de crash et reprise sur incident de worker.
  - **[Issue #6](https://github.com/nolll77/agentic-ops/issues/6)** : Évaluation empirique des LLMs gratuits OpenRouter pour le rôle d'Inspecteur du Quorum.
