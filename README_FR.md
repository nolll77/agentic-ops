# Agentic-Ops Control Plane

![Status](https://img.shields.io/badge/Status-Production%20Hardened-success)
![Security](https://img.shields.io/badge/Security-Red%20Teamed-critical)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Architecture](https://img.shields.io/badge/Architecture-Hexagonal-purple)

> **Language / Langue** : **[Read the main documentation in English (README.md)](README.md)** | **Version Française (actuelle)**

**Agentic-Ops** est un *Control Plane MLOps* de classe entreprise conçu pour orchestrer des Agents IA (LLMs) dans la résolution d'incidents de production (`Data Drift`, `Model Staleness`, `OOMKilled Pods`). 

Contrairement aux frameworks d'agents classiques (`LangChain`, `AutoGen`) qui privilégient l'autonomie absolue, `Agentic-Ops` est bâti sur les piliers du **SRE (Site Reliability Engineering)** : Déterminisme, Observabilité, Sécurité Distribuée (`Fail-Closed`) et `Human-in-the-Loop (HITL)` asynchrone.

> **Rapports Officiels de Déploiement et d'Interconnexion** :
> 1. **Validation Cloud Sandbox (`Docker Agentic Platform`)** : Déploiement sur micro-VM isolée et interprétation ligne par ligne des 30 tests unitaires, adversariaux et cryptographiques :  
>    **[Consulter le Rapport de Déploiement et Validation Cloud Sandbox (DOCKER_SANDBOX_VALIDATION.md)](DOCKER_SANDBOX_VALIDATION.md)**
> 2. **Branchement Tailscale sur la Plateforme Cible [`jakatt/cac_mlops`](https://github.com/jakatt/cac_mlops)** : Tunnelisation `Tailscale` en espace utilisateur (`userspace-networking` / proxy `SOCKS5` / relais `DERP`), ingestion en lecture seule stricte des 5 sources (`Loki`, `Prometheus`, `MLflow`, `Prefect`, `Evidently`) et validation par 13 tests unitaires :  
>    **[Consulter l'Architecture et la Validation du Connecteur Tailscale Pull (CAC_TAILSCALE_PULL_CONNECTOR.md)](CAC_TAILSCALE_PULL_CONNECTOR.md)**

---

## Architecture Globale (Hexagonale)

Le système repose sur une **Architecture Hexagonale** couplée à une **Machine à États Finis (FSM)**.

1. **Orchestrator (FSM)** : Coordonne le cycle de vie strict d'un incident (`DETECTED` -> `INVESTIGATING` -> `DIAGNOSED` -> `PLANNED` -> `AWAITING_APPROVAL` / `EXECUTING` -> `RESOLVED` / `DENIED`).
2. **Policy Engine** : Le cerveau de la gouvernance. Évalue chaque proposition d'action contre un manifeste YAML strict (`autonomy_policy.yaml`) pour décider de l'autonomie permise.
3. **Trust Ledger (Evidence Store)** : Registre cryptographique immuable (`WORM`). Chaque décision crée un hachage canonique avec chaînage du précédent (`Merkle`).
4. **Executor & Model Registry (Simulated / Adapter)** : Exécute les actions approuvées, modifie strictement le cycle de vie du modèle (`ModelRegistryStatusEnum`, `ModelDeploymentStatusEnum`).
5. **Agent Tools (Sandboxing)** : Outils mis à disposition des LLMs, confinés au niveau de l'OS avec un timeout implacable.

---

## Structure du Projet (ASCII Tree)

L'architecture applicative est reflétée par cette structure de dossiers formelle, où chaque composant joue un rôle critique dans la chaîne de sécurité :

```text
agentic-ops-core/
├── agentic_ops/
│   ├── core/
│   │   ├── orchestrator.py       # FSM principale. Stoppe physiquement sur REQUIRE_APPROVAL, gère la reprise (resume_episode).
│   │   ├── policy.py             # Moteur de gouvernance (Pydantic), évalue les manifestes de droits.
│   │   ├── executor.py           # Dernier kilomètre. Mute le Model Registry. Bloque et retourne FAILED en cas de rejet métier.
│   │   ├── evidence.py           # Trust Ledger WORM. Sérialisation canonique, chaînage de blocs (previous_hash).
│   │   ├── distributed.py        # Idempotence et Rate Limiting via Redis (Pipelines atomiques & Locks).
│   │   └── circuit_breaker.py    # Protection FinOps contre le Monitoring Storm (bascule en mode dégradé).
│   ├── adapters/
│   │   ├── cac_pull_collector.py # Connecteur Tailscale Pull (GET uniquement) vers jakatt/cac_mlops (Loki, Prometheus, MLflow, Prefect).
│   │   └── registry_adapter.py   # Protocole et simulation du Gatekeeper (ex: rejet automatique si F1 < 0.85).
│   ├── governance/
│   │   ├── autonomy_policy.yaml  # Manifeste MLOps strict de production (exigences d'approbation).
│   │   └── shadow_policy.yaml    # A/B testing des politiques de sécurité (analyse de divergence).
│   └── entrypoints/
│       └── slack_webhook.py      # HITL : Réception des validations humaines (HMAC-SHA256, Anti-replay attack max 5m).
├── docs/
│   └── mlops_simulation_scenarios_registry.md # Registre des scénarios de simulation MLOps
├── tests/
│   ├── adapters/
│   │   └── test_cac_pull_collector.py # 13 tests unitaires (parsing, résilience offline, enforcement read-only).
│   ├── integration/
│   │   └── test_registry_e2e.py       # Preuve formelle E2E du blocage de l'Orchestrateur sans intervention humaine.
│   └── security/
│       ├── test_trust_ledger.py       # Détection de falsification de la blockchain WORM (Anti-tampering).
│       └── test_executor.py           # Tests des invariants de sécurité (Sandboxing, OS-Level isolation).
├── DOCKER_SANDBOX_VALIDATION.md       # Rapport de déploiement et validation sur Cloud Sandbox Docker.
├── CAC_TAILSCALE_PULL_CONNECTOR.md    # Architecture et validation du connecteur Tailscale Pull vers CAC MLOps.
├── README.md                          # Documentation principale (Anglais).
├── README_FR.md                       # Documentation complète (Français).
└── pyproject.toml                     # Manifeste des dépendances (Pydantic, FastAPI, Redis, httpx, etc.)
```

---

## Interconnexion en Conditions Réelles : Branchement d'`Agentic-Ops` sur `CAC MLOps` ([`jakatt/cac_mlops`](https://github.com/jakatt/cac_mlops))

**`Agentic-Ops` n'est pas une plateforme d'entraînement supplémentaire : c'est un "Control Plane" (un cerveau de gouvernance SRE) qui vient se brancher au-dessus d'une plateforme MLOps d'exécution existante.**

Dans le cadre du déploiement de référence, `Agentic-Ops` (hébergé dans un conteneur isolé `Docker Agentic Platform`, IP Tailscale `100.102.123.121`) est branché sur la plateforme de production cible `CAC MLOps` :
* **Dépôt GitHub de la plateforme cible** : **[`https://github.com/jakatt/cac_mlops`](https://github.com/jakatt/cac_mlops)** (Prédiction de la gravité des accidents de la route).
* **Serveur de production cible (VPS Scaleway)** : `scw-jovial-dubinsky` — Adresse IP Tailscale : **`100.117.99.62`** — Domaine public : `https://mlops.jakat-inc.fr`.
* **Documentation technique complète du connecteur** : **[`CAC_TAILSCALE_PULL_CONNECTOR.md`](CAC_TAILSCALE_PULL_CONNECTOR.md)**.

---

### A. Schéma Architectural de Branchement (`Agentic-Ops` <-> `jakatt/cac_mlops` <-> `Slack HITL`)

Ce schéma ASCII illustre l'intégralité des points de connexion réseau, la séparation stricte entre les **ports d'observabilité en lecture seule** et la **zone sanctuarisée d'écriture**, ainsi que la boucle d'interaction humaine via **Slack** :

```text
+=======================================================================================================+
| PLATEFORME MLOPS CIBLE EN PRODUCTION : jakatt/cac_mlops (VPS Scaleway scw-jovial-dubinsky)            |
| Repo : https://github.com/jakatt/cac_mlops  |  IP Tailscale : 100.117.99.62                           |
+=======================================================================================================+
|                                                                                                       |
|  [ ZONE 1 : POINTS DE BRANCHEMENT D'OBSERVABILITE (AUTORISES - LECTURE SEULE HTTP GET) ]              |
|  +-------------------------------------------------------------------------------------------------+  |
|  | 1. Grafana Loki   (:3100) -> GET /loki/api/v1/query_range    (Logs d'alertes, rollbacks, CI/CD) |  |
|  | 2. Prometheus     (:9090) -> GET /api/v1/query               (cac_mlops_drift_share, model_info)|  |
|  | 3. MLflow Server  (:5001) -> GET /api/2.0/mlflow/...         (Alias @Production, F1-score, run) |  |
|  | 4. Prefect Server (:4200) -> GET /api/flow_runs              (Etat des 10 derniers pipelines)   |  |
|  | 5. Evidently Web  (:443)  -> GET https://mlops.jakat-inc.fr/reports/drift/latest_summary.json   |  |
|  +------------------------------------------------+------------------------------------------------+  |
|                                                   |                                                   |
|  [ ZONE 2 : ZONE SANCTUARISEE (INTERDITE EN MODE PULL - PROTEGEE PAR PARE-FEU LOGIQUE) ]              |
|  +------------------------------------------------v------------------------------------------------+  |
|  | [X] POST /predict (API Inference)        -> Interdit (polluerait la base et le calcul de drift) |  |
|  | [X] POST /loki/api/v1/push               -> Interdit (injecterait de fausses alertes en prod)   |  |
|  | [X] POST/DELETE .../registered-models    -> Interdit hors Executor approuve (changerait le mod.)|  |
|  | [X] POST /api/deployments/.../flow_run   -> Interdit hors Executor approuve (risque de reset)   |  |
|  | [X] Port :7860 (Cockpit Admin Gradio)    -> Interdit (declenche des actions humaines directes)  |  |
|  +-------------------------------------------------------------------------------------------------+  |
+===================================================|===================================================+
                                                    |
                                                    | Réseau Maillé Chiffré WireGuard (Tailscale)
                                                    | Traversée pare-feu via Relais DERP (Paris <-> Seattle)
                                                    | + Flux HTTPS direct pour le rapport Evidently public
                                                    v
+=======================================================================================================+
| CONTROL PLANE DE GOUVERNANCE : AGENTIC-OPS (Cloud Sandbox Docker - IP Tailscale : 100.102.123.121)    |
+=======================================================================================================+
|                                                                                                       |
|  1. COUCHE D'INGESTION RESEAU                                                                         |
|     [ Demon tailscaled (--tun=userspace-networking) ] ---> [ Proxy local SOCKS5 : 127.0.0.1:1055 ]    |
|                                                                      |                                |
|                                                                      v                                |
|  2. ADAPTATEUR D'OBSERVABILITE (agentic_ops/adapters/cac_pull_collector.py)                           |
|     [ CacPullCollector.collect_all() ]                                                                |
|       |-- Interroge les 5 sources en GET (Timeout 20s)                                                |
|       |-- Absorbe les pannes réseau (Retourne ONLINE, PARTIAL ou REMOTE_TARGET_OFFLINE sans crash)    |
|       +-- Produit un contrat Pydantic immuable : CacCollectedSnapshot                                 |
|                                                                      |                                |
|                                                                      v                                |
|  3. EXTRACTION DES FAITS & DIAGNOSTIC COGNITIF                                                        |
|     [ compute_facts() ] ---> Extrait objectivement : drift_share=0.34, colonnes dérivées, F1=0.883    |
|     [ Agent LLM Enquêteur ] -> Analyse les faits isolés (<untrusted_data>) et propose un ActionIntent |
|                                (ex: intent = TRIGGER_RETRAINING ou PROMOTE_MODEL)                     |
|                                                                      |                                |
|                                                                      v                                |
|  4. MOTEUR DE GOUVERNANCE DETERMINISTE (agentic_ops/core/orchestrator.py & policy.py)                 |
|     [ PolicyEngine ] -> Croise l'ActionIntent avec autonomy_policy.yaml et risk_register.yaml         |
|       |-- Si Action = Faible Risque (ex: INVESTIGATE) -----> Decision = ALLOW                         |
|       |-- Si Action = Interdite ou Hors Quota Redis -------> Decision = DENY (Blocage immédiat)       |
|       +-- Si Action = Critique (PROMOTE_MODEL / RETRAIN) --> Decision = REQUIRE_APPROVAL              |
|                                                                      |                                |
|     [ Orchestrator FSM ] -> Transitionne vers l'état AWAITING_APPROVAL et STOPPE PHYSIQUEMENT.        |
|                             Sauvegarde la transaction dans SQLite (WAL) + Verrou d'idempotence Redis. |
+===================================================|===================================================+
                                                    |
                      +-----------------------------+-----------------------------+
                      | 5. NOTIFICATION SORTANTE                                  | 6. WEBHOOK ENTRANT SIGNE
                      |    (Message Slack Block Kit)                              |    POST /webhooks/slack (:8001)
                      v                                                           |    (Signature HMAC-SHA256 + TTL 5m)
+=================================================================================|=====================+
| INTERFACE HUMAN-IN-THE-LOOP (SLACK)                                             |                     |
|                                                                                 |                     |
|  +---------------------------------------------------------------------------+  |                     |
|  | [ALERTE MLOPS - DATA-042] Dérive détectée sur jakatt/cac_mlops            |  |                     |
|  | - Source : Prometheus (cac_mlops_drift_share = 34%) & Evidently           |  |                     |
|  | - Colonnes en dérive : age_conducteur, hrmn, surf                         |  |                     |
|  | - Modèle actif : lgbm_accidents v7 (F1 = 0.883)                           |  |                     |
|  | - Action proposée par l'Agent : TRIGGER_RETRAINING                        |  |                     |
|  |                                                                           |  |                     |
|  |   Bouton 1 : [ APPROUVER L'EXECUTION ]      Bouton 2 : [ REJETER (DENY) ] +--+                     |
|  +---------------------------------------------------------------------------+                        |
+=======================================================================================================+
                                                    |
                                                    | 7. REPRISE TRANSACTIONNELLE (Si "APPROVE" validé)
                                                    v
+=======================================================================================================+
| EXECUTION DU DERNIER KILOMETRE & REGISTRE DE PREUVES (agentic_ops/core/executor.py & evidence.py)     |
|                                                                                                       |
|  1. [ slack_webhook.py ] -> Vérifie HMAC-SHA256, anti-rejeu (< 5 min), groupe d'approbateurs YAML     |
|                             et pose un verrou atomique SQLite (BEGIN IMMEDIATE) contre le double-clic.|
|  2. [ orchestrator.resume_episode() ] -> Débloque la FSM (AWAITING_APPROVAL -> EXECUTING).            |
|  3. [ Executor ] -> Seul module autorisé à émettre l'appel d'écriture validé.                         |
|  4. [ Trust Ledger WORM (evidence.py) ] -> Scelle l'épisode complet (Snapshot CAC + Décision +        |
|                             Identité de l'approbateur Slack + Résultat) avec chaînage SHA-256         |
|                             (`previous_hash`) et signature cryptographique `HMAC-SHA512`.             |
+=======================================================================================================+
```

---

### B. Détail des 5 Points de Branchement d'Observabilité (`CacPullCollector`)

Pour surveiller la plateforme [`jakatt/cac_mlops`](https://github.com/jakatt/cac_mlops) sans jamais perturber son fonctionnement, le module [`agentic_ops/adapters/cac_pull_collector.py`](agentic_ops/adapters/cac_pull_collector.py) interroge cinq points de terminaison précis :

| N° | Service Distant (`jakatt/cac_mlops`) | Adresse & Port | Route HTTP Interrogee (`GET` uniquement) | Donnees d'Observabilite Extraites pour `Agentic-Ops` |
| :--- | :--- | :--- | :--- | :--- |
| **1** | **Grafana Loki** | `100.117.99.62:3100` (via `SOCKS5`) | `GET /loki/api/v1/query_range` | Requête LogQL `{service="prefect-worker"} \|= "event=alert"` sur 6h glissantes. Capture les alertes structurées en JSON (`risk_id`, rollbacks automatiques, erreurs de pipelines). |
| **2** | **Prometheus** | `100.117.99.62:9090` (via `SOCKS5`) | `GET /api/v1/query` | Interroge 3 jauges et compteurs temps réel : `cac_mlops_drift_share` (taux de colonnes en dérive), `mlops_model_info{alias="Production"}` (modèle actif) et `http_requests_total` (trafic API). |
| **3** | **MLflow Registry** | `100.117.99.62:5001` (via `SOCKS5`) | `GET /api/2.0/mlflow/registered-models/alias` & `GET /api/2.0/mlflow/runs/get` | Identifie la version exacte du modèle `lgbm_accidents` portant l'alias `@Production`, son `run_id`, ses tags et ses métriques d'évaluation (`f1_score`, `accuracy`). |
| **4** | **Prefect Server** | `100.117.99.62:4200` (via `SOCKS5`) | `GET /api/flow_runs?limit=10&sort=START_TIME_DESC` | Récupère l'état d'exécution des 10 derniers flows (`COMPLETED`, `FAILED`), leurs noms et leurs durées (`start_time`, `end_time`) pour détecter les échecs d'entraînement. |
| **5** | **Evidently Drift** | `mlops.jakat-inc.fr:443` (HTTPS direct) | `GET /reports/drift/latest_summary.json` | Télécharge le dernier rapport statistique de dérive généré par `Evidently` : date du rapport, `drift_share` global et liste exacte des colonnes en dérive (`drifted_columns`, ex: `["age_conducteur", "hrmn", "surf"]`). |

#### Résilience face à l'extinction du serveur distant (`Offline Tolerance`)
Si le VPS Scaleway `scw-jovial-dubinsky` est mis hors tension (ou si un service individuel redémarre), `CacPullCollector.collect_all()` intercepte proprement les exceptions `httpx.ConnectError` et `httpx.TimeoutException` :
- Si les 5 sources répondent : `snapshot.status = RemoteServiceStatus.ONLINE`.
- Si une seule source est indisponible : `snapshot.status = RemoteServiceStatus.PARTIAL` (les données des 4 autres sources sont conservées et exploitées).
- Si le VPS est totalement éteint : `snapshot.status = RemoteServiceStatus.REMOTE_TARGET_OFFLINE` (l'orchestrateur `Agentic-Ops` reste en veille active sans jamais planter).

---

### C. Comment fonctionne l'Interaction via les Alertes et Approbations Slack (`HITL`)

L'intégration entre la télémétrie lue sur [`jakatt/cac_mlops`](https://github.com/jakatt/cac_mlops) et la prise de décision humaine sur `Slack` suit un protocole de sécurité en **6 étapes séquentielles** :

#### 1. Collecte et Déclenchement de l'Épisode
L'orchestrateur déclenche une collecte via `CacPullCollector().collect_all()` (soit périodiquement en mode `Pull`, soit réveillé par un webhook d'alerte entrant). Le `CacCollectedSnapshot` révèle par exemple que `cac_mlops_drift_share` a atteint `0.34` (34 % des variables ont dérivé) et qu'une alerte `event=alert` est apparue dans `Loki`.

#### 2. Calcul Déterministe des Faits (`System Facts`) et Isolation du Prompt
Avant même d'appeler le LLM, la fonction `compute_facts()` extrait mathématiquement les faits avérés depuis le snapshot. Les logs bruts provenant de `Loki` sont encapsulés dans des balises de quarantaine `<untrusted_data>` par le `Prompt Guard` afin qu'aucune injection de prompt cachée dans un log externe ne puisse manipuler l'agent.

#### 3. Diagnostic de l'Agent et Interception par le `PolicyEngine`
L'agent cognitif analyse le contexte (modèle `lgbm_accidents` v7, dérive sur `age_conducteur`, `hrmn`, `surf`) et émet une intention structurée : `ActionIntent(action="TRIGGER_RETRAINING", target="lgbm_accidents")` ou `PROMOTE_MODEL`.
Le `PolicyEngine` évalue immédiatement cette intention contre le manifeste [`autonomy_policy.yaml`](agentic_ops/governance/autonomy_policy.yaml) :
- Toute action modifiant le modèle de production ou relançant un pipeline lourd est classée **`REQUIRE_APPROVAL`**.
- La machine à états (`Orchestrator FSM`) passe à l'état **`AWAITING_APPROVAL`** et **s'arrête physiquement**. L'agent IA est désactivé.

#### 4. Envoi de l'Alerte Interactive sur Slack
Le Control Plane envoie une notification formatée (`Slack Block Kit`) sur le canal d'astreinte MLOps contenant :
- L'identifiant unique de l'épisode (`episode_id`) et le `risk_id`.
- Le résumé des preuves collectées sur `jakatt/cac_mlops` (taux de dérive `Prometheus`/`Evidently`, métriques `MLflow` actuelles, état du dernier flow `Prefect`).
- L'action proposée et son rayon d'impact (`blast_radius`).
- Deux boutons d'action : **`[ APPROVE ]`** et **`[ DENY ]`**.

#### 5. Réception et Vérification Cryptographique du Clic Humain (`slack_webhook.py`)
Lorsque l'ingénieur SRE clique sur **`[ APPROVE ]`** dans Slack, les serveurs de Slack envoient une requête `POST /webhooks/slack` vers notre API `FastAPI` (port `8001`). Le module [`agentic_ops/entrypoints/slack_webhook.py`](agentic_ops/entrypoints/slack_webhook.py) applique **4 barrières de sécurité successives** :
1. **Authenticité Cryptographique (`HMAC-SHA256`)** : Vérifie la signature `X-Slack-Signature` calculée avec le `SLACK_SIGNING_SECRET` sur le corps brut de la requête. Toute requête non signée ou falsifiée est rejetée en `0.002s` avec **`HTTP 401 Unauthorized`**.
2. **Protection Anti-Rejeu (`Replay Attack`)** : Vérifie l'en-tête `X-Slack-Request-Timestamp`. Si la requête a plus de **5 minutes** d'ancienneté ou si sa signature a déjà été vue, elle est rejetée.
3. **Contrôle d'Autorisation (`approvers.yaml`)** : Vérifie que l'utilisateur Slack qui a cliqué appartient bien au groupe d'approbateurs habilités pour ce niveau de criticité.
4. **Verrou Transactionnel Atomique (`SQLite BEGIN IMMEDIATE`)** : Si deux opérateurs cliquent simultanément sur le bouton dans Slack (faille du *Double Clic*), la transaction SQLite garantit qu'un seul clic effectue la transition `PENDING -> APPROVED`, le second étant immédiatement rejeté.

#### 6. Exécution du Dernier Kilomètre et Scellement `WORM` (`Trust Ledger`)
Une fois l'approbation validée :
- `orchestrator.resume_episode()` réhydrate l'épisode et passe la FSM à l'état `EXECUTING`.
- Le module déterministe `Executor` exécute l'action autorisée (et uniquement celle-ci).
- L'intégralité de l'épisode (le snapshot initial de la plateforme cible, la proposition de l'IA, l'identité de l'approbateur Slack, l'horodatage et le résultat d'exécution) est sérialisée en JSON canonique, chaînée au bloc précédent (`previous_hash` `SHA-256`) et signée en `HMAC-SHA512` dans le registre immuable **`Trust Ledger` (`evidence.py`)**.

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#ffffff', 'primaryTextColor': '#000000', 'primaryBorderColor': '#333333', 'lineColor': '#333333', 'noteBkgColor': '#fff59d', 'noteTextColor': '#000000'}}}%%
sequenceDiagram
    autonumber
    participant CAC as Plateforme jakatt/cac_mlops (100.117.99.62)
    participant Pull as CacPullCollector (SOCKS5 :1055)
    participant FSM as Orchestrator FSM & PolicyEngine
    participant Slack as Ingénieur SRE (Slack HITL)
    participant Exec as Executor & Trust Ledger WORM

    Note over CAC, Pull: Phase 1 : Observation Passive (100% GET Read-Only)
    Pull->>CAC: GET Loki (:3100), Prometheus (:9090), MLflow (:5001), Prefect (:4200), Evidently (:443)
    CAC-->>Pull: JSON (drift_share=0.34, lgbm_accidents v7, alertes LogQL)
    Pull->>FSM: CacCollectedSnapshot (status=ONLINE)

    Note over FSM, Slack: Phase 2 : Diagnostic & Blocage Fail-Closed
    FSM->>FSM: compute_facts() + Diagnostic Agent -> ActionIntent(TRIGGER_RETRAINING)
    FSM->>FSM: PolicyEngine évalue autonomy_policy.yaml -> REQUIRE_APPROVAL
    FSM->>Slack: Alerte Slack Block Kit (Preuves CAC + Boutons [APPROVE] / [DENY])
    Note over FSM: Arrêt physique en état AWAITING_APPROVAL (SQLite WAL)

    Note over Slack, Exec: Phase 3 : Validation Humaine Signée & Scellement WORM
    Slack->>FSM: Clic [APPROVE] -> POST /webhooks/slack (Signé HMAC-SHA256)
    FSM->>FSM: Vérifie HMAC-SHA256 + Anti-Replay (<5m) + Verrou BEGIN IMMEDIATE
    FSM->>Exec: resume_episode() -> Ordre déterministe d'exécution
    Exec->>Exec: Scelle la preuve complète dans le Trust Ledger (SHA-256 + HMAC-SHA512)
```

---

## Fonctionnalités Clés & Hardening (Red-Teaming)

Ce dépôt a subi un audit architectural offensif (*Red-Teaming*) exhaustif et a été corrigé avec une politique absolue du "Fail-Closed" sur la chaîne d'exécution.

### 1. Gouvernance E2E & Model Registry
- **Contrôle Strict (Incontournable)** : L'`Orchestrator` gère le cycle de vie MLOps. Si l'action `PROMOTE_MODEL` est classée `REQUIRE_APPROVAL`, l'orchestrateur s'arrête physiquement. **Aucune action n'est soumise à l'exécuteur**.
- **Réhydratation Asynchrone (HITL)** : L'approbation humaine déclenche `orchestrator.resume_episode()` qui valide cryptographiquement l'approbateur, reprend la machine d'état et transmet l'ordre à l'Exécuteur.
- **Model Registry Gatekeeping** : L'Exécuteur pilote directement le Registre de Modèle. Ce dernier refuse silencieusement les promotions non valides (ex: F1 < 0.85 ou schéma incompatible), forçant l'Exécuteur à renvoyer un statut `FAILED` détectable (et non un faux `SIMULATED`). Seule une version de modèle peut être `ACTIVE` à la fois.

### 2. Traçabilité Cryptographique (Trust Ledger WORM)
- **Chaîne de blocs (Previous Hash)** : L'`EvidenceStore` attribue à chaque épisode un `previous_hash` garantissant l'ordonnancement chronologique strict.
- **Canonicalisation** : L'état complet (Pydantic `mode='json'`) est encodé via `get_canonical_json` avec un hachage `SHA-256`.
- **Anti-Falsification (Tamper-Evident)** : Un pirate qui tenterait de forcer l'état WORM (`state_trace` = `APPROVE`) invalidera la signature au sein de `verify_episode()`. Interdiction formelle de réécrire un ID d'épisode localement.

### 3. Sécurité Distribuée & Concurrence (Redis)
- **Rate Limiting Atomique** : Limite le nombre d'actions destructrices via pipelines atomiques Redis (`INCR` + `EXPIRE`). Aucune *Race Condition* en multi-réplicas.
- **Idempotence Sémantique** : Verrous distribués Redis (`SET NX EX`) basés sur l'empreinte sémantique (`tenant:env:service:risk_id`). Élimine les doubles exécutions.
- **Webhook Slack Sécurisé** : L'approbation humaine via Slack (Block Kit) exige la validation cryptographique `HMAC-SHA256` et bloque les requêtes âgées de plus de 5 minutes (Anti Replay-Attack).

### 4. Résilience Financière & Organisationnelle
- **FinOps Circuit Breaker** : Coupe l'accès aux API LLM en cas de "Monitoring Storm" (ex: boucle infinie d'alertes) pour protéger le budget, basculant sur une remédiation déterministe (`CREATE_ISSUE`).
- **Shadow Mode (A/B Testing de Sécurité)** : L'Orchestrateur évalue le `shadow_policy.yaml` en parallèle du manifeste primaire et consigne les divergences sans jamais modifier la production.
- **Isolation d'Exécution OS-Level** : Chaque outil LLM s'exécute dans un processus distinct (`multiprocessing.Process`) avec un Timeout impitoyable évitant l'OOM ou le hanging process.

### 5. Décision Déterministe sur les Faits (PR2)
- **Policy Engine V2** : Le LLM (Remediation Agent) ne propose plus qu'un `ActionIntent` (action, cible). Le moteur de politiques (`PolicyEngine`) calcule lui-même les attributs de risque (`blast_radius`, `reversible`) en s'appuyant sur un `action_catalog.yaml` et un `risk_register.yaml` déterministes.
- **System Facts** : L'état réel du cluster (télémétrie, pods OOM, drift détecté) est calculé formellement via `compute_facts()` sans passer par la subjectivité du LLM, empêchant les hallucinations de contourner les règles.

### 6. Harnais Adversarial & Confinement (PR3)
- **Prompt Guard** : Isolation cryptographique (`<untrusted_data>`) des logs et payloads pour empêcher les attaques d'injection de prompt (`Prompt Injection`).
- **Red Team Scenarios** : Tests E2E stricts (`known_gaps.yaml`) validant que l'orchestrateur refuse toute action ciblée forgée par un LLM corrompu.

### 7. Dépôt d'Approbation Transactionnel (PR4)
- **State Machine Atomique (SQLite WAL)** : L'approbation humaine est gérée via un verrou `BEGIN IMMEDIATE` pour empêcher la faille de la "Double Exécution" (Double Clic).
- **Anti-Rejeu & Cryptographie** : Les webhooks Slack sont vérifiés via `HMAC-SHA256` sur le corps brut. Chaque signature est stockée avec un TTL (Fenêtre anti-rejeu).
- **Gouvernance as Code** : Les approbateurs sont explicitement définis dans `approvers.yaml` avec vérification de groupes distincts pour les décisions L3.

### 8. Trust Ledger Cryptographique (PR5)
- **Stockage Append-Only WORM** : Le journal des preuves (`evidence.py`) utilise un stockage immuable où chaque épisode est lié cryptographiquement au précédent.
- **Signature HMAC-SHA512** : Toute altération locale (modification d'un fichier JSON ou de l'index) brise mathématiquement la chaîne, rendant impossible la dissimulation d'une action toxique par un attaquant ou un agent corrompu.

### 9. Concurrence Distribuée Stricte (PR6)
- **Verrous d'Idempotence (Redis)** : Pour prévenir la double exécution d'une réparation sur deux réplicas, un verrou distribué atomique est posé sur l'empreinte sémantique de l'incident. Ce verrou a une durée de vie (TTL) et est lié cryptographiquement au processus "propriétaire" (UUID) pour empêcher qu'un autre noeud ne libère un verrou expiré (Vol de verrou).
- **Fail-Closed en Production** : Si le coordinateur de concurrence (`Redis`) devient injoignable, le système passe en arrêt d'urgence plutôt que de basculer silencieusement sur un cache local non distribué.

### 10. Durcissement Opérationnel & CI/CD (PR7)
- **RBAC Kubernetes Restreint** : Le `ServiceAccount` Kubernetes du Control Plane fonctionne selon le principe du moindre privilège. Il a uniquement les droits `get/list/watch` sur les Pods (pour la lecture des logs) et `patch` sur les Deployments (uniquement pour forcer le redémarrage d'un modèle fautif).
- **Fiabilité Kubernetes (Probes)** : Le Chart Helm intègre des `livenessProbe` et `readinessProbe` pointant vers une API `FastAPI` native pour assurer que le pod est sain et prêt à recevoir le trafic Slack Webhook.
- **Dépendances & CI Matrix** : L'environnement Python est déterministe avec une matrice de test GitHub Actions sur Python 3.10, 3.11, et 3.12, validant le comportement sur toutes les cibles modernes. L'image Docker est fixée par tag.

---

## Télémétrie & Observabilité Interne

Exposition de métriques de niveau SRE via **Prometheus** (sans explosion de cardinalité) :
- `agentic_ops_fsm_transitions_total` : Suivi de la Machine à États.
- `agentic_ops_policy_decisions_total` : Ratio des `ALLOW`, `DENY`, et `REQUIRE_APPROVAL`.
- `agentic_ops_circuit_breaker_status` : Déclenchement du coupe-circuit FinOps.

---

## Séparation des Pouvoirs (Isolation Cognitive vs Exécutive)

L'une des vulnérabilités majeures des frameworks d'agents autonomes classiques est de donner les "clés du réseau" à l'IA. `Agentic-Ops` résout ce problème par une séparation stricte des privilèges :

- **Phase d'Enquête (L'IA lit)** : Les agents LLM ont un accès **strictement restreint à la lecture seule** (Mode Pull). Ils interrogent les bases de métriques et les logs pour poser un diagnostic. Ils sont physiquement incapables d'altérer la production. Ils se contentent de rédiger une "intention de modification" textuelle.
- **Phase d'Exécution (Le Code écrit)** : L'agent IA s'arrête. C'est le programme Python rigide (l'`Executor`), totalement déterministe, qui prend le relais **uniquement** après l'approbation humaine. C'est lui, et lui seul, qui détient les clés API et qui déclenche les mutations (Mode Push).

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#ffffff', 'primaryTextColor': '#000000', 'primaryBorderColor': '#333333', 'lineColor': '#333333', 'noteBkgColor': '#fff59d', 'noteTextColor': '#000000'}}}%%
sequenceDiagram
    autonumber
    participant Platform as Plateforme MLOps
    participant Agent as Agent LLM (Enquêteur)
    participant FSM as Orchestrator & Policy
    participant Human as Humain (Slack)
    participant Exec as Executor Python (Actionneur)

    Note over Platform, Exec: Phase 1 : Enquête (Lecture Seule)
    Platform->>FSM: Alerte Webhook (Inbound)
    FSM->>Agent: Réveille l'Agent
    Agent->>Platform: Requêtes REST (GET Logs, GET Metrics)
    Platform-->>Agent: JSON (État du système)
    Agent-->>FSM: Intention : "Je propose de relancer l'entraînement"

    Note over FSM, Exec: Phase 2 : Le Garde-Fou (Block & Attente)
    FSM->>FSM: Policy Engine intercepte
    FSM->>Human: Demande d'approbation Slack
    Note over Agent: L'Agent LLM est désactivé
    
    Note over Human, Exec: Phase 3 : Validation & Exécution (Écriture)
    Human-->>FSM: Clic sur [ APPROUVER ]
    FSM->>Exec: Ordre formel & déterministe
    Exec->>Platform: Requête mutante (POST /deploy /retrain)
    Platform-->>Exec: Succès de l'opération
    Exec-->>FSM: Scellage dans le Trust Ledger
```

### Architecture d'Intégration Générique (`flowchart TD`)

**`Agentic-Ops` n'est pas une plateforme MLOps de plus, c'est un "Control Plane" (un cerveau) agnostique.** Il se branche sur vos outils existants via une Architecture Orientée Événements (Event-Driven) et des API REST en 3 phases physiques :

1. **Les Capteurs (Inbound - Comment réveiller l'Agent)** :
   Les outils d'observabilité (`Evidently AI`, `Prometheus`, `Datadog`) envoient des alertes via **Webhooks HTTP** vers l'API d'`Agentic-Ops` contenant un `risk_id` (ex: `DATA-042`).
2. **Le Contexte (Read-Only - Comment l'Agent enquête)** :
   Les agents spécialisés utilisent les SDKs (`MLflow`, `Kubernetes`, `DVC`) ou le collecteur `CacPullCollector` en mode **Lecture Seule** pour analyser le registre de modèles, les métriques ou les logs des pods.
3. **Les Actuateurs (Outbound - Comment l'Agent répare)** :
   Une fois la décision validée par le *Policy Engine* (et le *Human-in-the-Loop*), le module `Executor` traduit l'intention en appels d'API mutantes (déclencher un flow `Prefect`/`Airflow`, changer un tag `MLflow`, redémarrer un déploiement `K8s`).

```mermaid
flowchart TD

    %% Style global pour lisibilité (Thème Clair forcé)
    classDef default fill:#ffffff,stroke:#333333,stroke-width:2px,color:#000000;
    classDef agentic fill:#f3e5f5,stroke:#8e24aa,stroke-width:2px,color:#000000;
    classDef cible fill:#e3f2fd,stroke:#1976d2,stroke-width:2px,color:#000000;
    classDef alert fill:#ffebee,stroke:#d32f2f,stroke-width:2px,color:#000000;
    subgraph Plateforme MLOps
        Evidently[Moniteur Dérive : Evidently/Prometheus]
        MLflow[Model Registry : MLflow]
        Airflow[Pipeline Orchestrator : Prefect/Airflow]
        K8s[Inférence : Kubernetes]
    end

    subgraph Agentic-Ops Control Plane
        API[Webhook API Listener]
        FSM[Orchestrator FSM]
        Agents[Agents LLM Spécialisés]
        Policy[Policy Engine & Risk Register]
        Exec[Executor & Adapters]
    end

    subgraph Humain
        Slack[Slack HITL]
    end

    Evidently -- "1. Alerte Webhook (Drift détecté)" --> API
    API --> FSM
    FSM --> Agents
    Agents -- "2. Lecture (API REST)" --> MLflow
    Agents -- "2. Lecture (Logs)" --> K8s
    Agents --> Policy
    Policy -- "3. REQUIRE_APPROVAL" --> Slack
    Slack -- "4. Approve (Webhook signé)" --> FSM
    FSM --> Exec
    Exec -- "5. Action (REST API)" --> Airflow
```

---

## Catalogue des Actions Physiques (Pouvoirs de Mutation de l'`Executor`)

Le module d'exécution (`Executor`) est le seul composant autorisé à réaliser des écritures. Ces actions sont strictement soumises à la désactivation du mode simulation (`SIMULATION_MODE=False`) et à l'approbation humaine Slack (si requise par la politique).

#### 1. Intégration Code & Audit (API GitHub)
*Action d'alerte et de traçabilité asynchrone.*
- **Action ciblée** : `CREATE_ISSUE`
- **Mécanisme** : Forge une requête HTTP POST sécurisée avec un Token d'accès vers l'API de GitHub.
- **Résultat** : Crée instantanément un ticket de remédiation (Issue) sur le dépôt distant, taggé avec `mlops-incident`, détaillant le diagnostic de l'Agent.

#### 2. Remédiation d'Infrastructure (API Kubernetes)
*Action de protection d'urgence (Coupe-circuit).*
- **Action ciblée** : `SCALE_TO_ZERO`
- **Mécanisme** : Utilise le client officiel Python `kubernetes` pour se connecter au cluster de production et patcher le déploiement d'un pod.
- **Sécurité Fail-Closed** : L'exécuteur est bridé par une *Whitelist*. Il refusera formellement d'altérer un namespace ou un conteneur non explicitement autorisé.
- **Résultat** : Éteint totalement une API de prédiction défaillante pour stopper une hémorragie de mauvaises décisions, avec une vérification *Read-After-Write* post-exécution.

#### 3. Orchestration MLOps (API Prefect via Tunnel)
*Action de ré-entraînement.*
- **Action ciblée** : `TRIGGER_RETRAINING`
- **Mécanisme** : Cible l'infrastructure distante via le réseau superposé (ex: `Tailscale`) et envoie un appel formel `POST /api/deployments/{id}/create_flow_run`.
- **Résultat** : Force l'orchestrateur distant à lancer le pipeline d'ingestion de données et de réentraînement du modèle d'apprentissage automatique.

#### 4. Promotion de Modèle (API MLflow via Tunnel)
*Action de mise en production.*
- **Action ciblée** : `PROMOTE_MODEL`
- **Mécanisme** : Interagit avec l'API REST du Model Registry (`POST /api/2.0/mlflow/registered-models/alias`) via le réseau superposé.
- **Résultat** : Assigne l'alias `@Production` à un nouveau modèle candidat, déclenchant ainsi le basculement du trafic d'inférence.

#### Actions en mode "Dry-Run" (Simulées)
Certaines actions exploratoires ou à risque asymétrique sont maintenues en simulation stricte (journalisées dans le registre WORM sans exécution réseau) :
- `ROLLBACK` : Rétrograder une version d'image ou de modèle.
- `INVESTIGATE` : Consigner formellement une enquête sans altération.

---

## Interfaçage Universel (Agnostic MLOps Control Plane)

Au-delà de son branchement effectif sur [`jakatt/cac_mlops`](https://github.com/jakatt/cac_mlops), **Agentic-Ops** a été pensé dès le premier jour comme un plan de contrôle agnostique. Il ne dépend pas du code source du modèle qu'il surveille. Il n'a besoin que de trois éléments pour piloter une infrastructure tierce :
1. Un accès réseau sécurisé (ex: *Tailscale*).
2. Des points de terminaison d'observabilité en lecture seule ou Webhooks d'alerte (ex: *Loki, Prometheus, Evidently, Grafana*).
3. Des points de terminaison d'exécution gouvernée (ex: *API Prefect, MLflow, Kubernetes, GitHub*).

À titre d'illustration, voici comment **Agentic-Ops** peut se greffer "Plug & Play" sur diverses architectures MLOps de production open-source (sans modifier leur code source) pour leur apporter l'auto-guérison :

| N° | Projet Cible | Type & Enjeu | Écosystème MLOps | Métriques de Télémétrie | Scénario d'Auto-Guérison Agentic-Ops |
|:---|:---|:---|:---|:---|:---|
| **0** | **[CAC MLOps Platform](https://github.com/jakatt/cac_mlops)** | **Gravité Accidents (Branchement Réel)** | **`Prefect`, `MLflow`, `Loki`, `Prometheus`, `Evidently`, `Tailscale`** | **`cac_mlops_drift_share`, F1-Score (`lgbm_accidents`), Alertes LogQL** | **`INVESTIGATE_LOGS` -> `TRIGGER_RETRAINING` -> `PROMOTE_MODEL` -> `ROLLBACK`** |
| **1** | [MultiModalAI-MLOps (Référence)](https://github.com/YBengala/MultiModalAI-MLOps) | Multimodal | `FastAPI`, `Docker`, `Prometheus`, `MLflow`, `Evidently` | F1-Score, Divergence KL, Latence API | `SCALE_UP` -> `INVESTIGATE_LOGS` -> `TRIGGER_RETRAINING` -> `PROMOTE_MODEL` |
| **2** | [Road Accidents BAAC (France)](https://github.com/DataScientest-Studio/oct25_bmlops_int_accidents) | Sévérité Accidents | `Evidently`, `Airflow`, `FastAPI`, `Docker`, `Grafana`, `MLflow` | *Data Drift* (Météo/Lieu), Accuracy, OOM Kills | `INVESTIGATE_LOGS` -> `SCALE_UP` -> `TRIGGER_RETRAINING` -> `ROLLBACK` |
| **3** | [MLOps Accidents (BentoML)](https://github.com/aupaysdesdata/MLOps_accidents) | Inférence Sévérité | `BentoML`, `GitHub Actions`, `Airflow`, `Grafana` | Requêtes/sec (RPS), Latence, Faux Positifs | `SCALE_UP` -> `INVESTIGATE_LOGS` -> `CREATE_ISSUE` -> `NOTIFY_ONCALL` |
| **4** | [Rakuten MLOps Platform](https://github.com/DataScientest-Studio/jun25_bmle_mlops_rakuten2) | Texte/Image | `Airflow`, `DVC`, `PostgreSQL`, `MLflow`, `Docker` | F1-Score, *Data Drift*, Latence, Erreurs API | `INVESTIGATE_LOGS` -> `CREATE_ISSUE` -> `TRIGGER_RETRAINING` -> `PROMOTE_MODEL` |
| **5** | [Rakuten (K8s & Evidently)](https://github.com/DataScientest-Studio/jun25_bmle_mlops_rakuten1) | Déploiement K8s | `Kubernetes`, `Evidently`, `GitHub Actions`, `MLflow` | *Concept Drift*, RAM Pods, mAP, Covariate Shift | `SCALE_UP` -> `RESTART_PODS` -> `ROLLBACK` -> `NOTIFY_ONCALL` |
| **6** | [Rakuten Pipeline (FastAPI)](https://github.com/DataScientest-Studio/sep25_cmlops_rakuten) | Temps Réel | `FastAPI`, `Airflow`, `Grafana`, `Streamlit` | Drift Embeddings, RPS, Erreurs 4xx/5xx | `INVESTIGATE_LOGS` -> `CREATE_ISSUE` -> `TRIGGER_RETRAINING` |
| **7** | [Rakuten Core Pipeline](https://github.com/DataScientest-Studio/avr25_bmlops_rakuten) | Pipeline Base | `MLflow`, `Prometheus`, `Grafana`, `Airflow` | Précision métier, Temps de réponse global | `INVESTIGATE_LOGS` -> `RESTART_PIPELINE` -> `TRIGGER_RETRAINING` |
| **8** | [Reco Films MLOps](https://github.com/DataScientest-Studio/jun25_bmle_mlops_reco_films) | Collaboratif | `Evidently`, `FastAPI`, `DVC`, `Airflow`, `MLflow` | CTR, Score Diversité, *Feature Drift*, Latence | `SCALE_UP` -> `INVESTIGATE_LOGS` -> `TRIGGER_RETRAINING` -> `PROMOTE_MODEL` |
| **9** | [Reco Films Streaming](https://github.com/DataScientest-Studio/sep25_cmlops_reco_films1) | Recommandation | `Airflow`, `FastAPI`, `Docker`, `Grafana`, `MLflow` | Taux Cold-Start, Temps exécution DAG | `SCALE_UP` -> `RESTART_PODS` -> `CREATE_ISSUE` |
| **10** | [Reco Films Registry](https://github.com/DataScientest-Studio/sep25_bmle_mlops_reco_films) | Registre Modèles | `DVC`, `MLflow`, `Docker`, `FastAPI`, `Streamlit` | MAE/RMSE, CPU Throttling, *Data Drift* | `INVESTIGATE_LOGS` -> `ROLLBACK` -> `NOTIFY_ONCALL` |
| **11** | [Australian Weather Spatial](https://github.com/DataScientest-Studio/jul26_bmlops_int_weather) | Séries Spatiales | `Nginx`, `FastAPI`, `Airflow`, `MLflow`, `DVC` | *Covariate Shift* (Pluie), MAE, CPU Nginx | `INVESTIGATE_LOGS` -> `RESTART_PIPELINE` -> `NOTIFY_ONCALL` |
| **12** | [Rain in Australia](https://github.com/DataScientest-Studio/oct25_bmlops_int_weather) | Régression | `Docker`, `FastAPI`, `MLflow`, `Streamlit` | Précision, Recall, Biais saisonnier, Valeurs nulles | `CREATE_ISSUE` -> `TRIGGER_RETRAINING` -> `PROMOTE_MODEL` |
| **13** | [London Fire Brigade](https://github.com/DataScientest-Studio/juin23_continu_mlops_pompiers) | Temps Inter. | `Airflow`, `Docker`, `Streamlit`, `FastAPI` | RMSE, Temps inférence, Taux erreurs API | `INVESTIGATE_LOGS` -> `RESTART_PODS` -> `TRIGGER_RETRAINING` |
| **14** | [Plant Reco (Vision)](https://github.com/DataScientest-Studio/sep26_bmlops_int_plant_reco) | Computer Vision | `FastAPI`, `Docker`, `MLflow`, `GitHub Actions` | Faux Négatifs (Critique), Latence Image, GPU OOM | `SCALE_UP` -> `ROLLBACK` -> `CREATE_ISSUE` |
| **15** | [Maintenance Préventive](https://github.com/yann112/mlops_project_2022_preventive_maintenance) | Classif. IoT | `FastAPI`, `Docker`, `Airflow`, `Prometheus` | *Concept Drift* (Usure), Latence, Capteurs HS | `SCALE_TO_ZERO` (Coupe-circuit) -> `INVESTIGATE_LOGS` |

### Glossaire des Actions de l'`Executor`
Afin de transformer un simple tableau de bord passif en un véritable **Control Plane Auto-Réparateur**, le module `executor.py` d'Agentic-Ops traduit chaque décision validée en appels d'API physiques vers l'infrastructure cible :

- `INVESTIGATE_LOGS` : L'agent récupère de manière autonome les logs du service défaillant (ex: via `Loki` ou `kubectl logs`) et utilise son LLM pour générer un résumé de la cause racine (*Root Cause Analysis*) sans intervention humaine.
- `CREATE_ISSUE` : Génération d'un ticket formaté (GitHub/Jira/GitLab) contenant le contexte de l'incident, les métriques déviantes, et une recommandation de correctif ou d'ajustement des hyperparamètres.
- `SCALE_UP` / `SCALE_TO_ZERO` : Interaction directe avec le plan de contrôle de l'infrastructure (Kubernetes HPA, AWS ASG, API Docker) pour allouer de la puissance de calcul face à un pic de requêtes, ou couper un service qui génère des prédictions dangereuses (mode coupe-circuit).
- `TRIGGER_RETRAINING` : Appel asynchrone à un orchestrateur de pipelines (`Prefect`, `Airflow`, `GitHub Actions`) avec les bonnes balises temporelles pour forcer un ré-entraînement du modèle sur des données fraîches.
- `PROMOTE_MODEL` : Une fois le ré-entraînement validé, l'agent déplace le nouveau modèle du statut `Staging` à `@Production` dans le *Model Registry* (`MLflow`) pour amorcer son déploiement.
- `RESTART_PIPELINE` / `RESTART_PODS` : Redémarrage brutal (hard-reset) d'un job de données bloqué ou d'un service d'inférence Web victime de fuite mémoire (OOM).
- `ROLLBACK` : En cas de dégradation extrême (baisse dramatique de l'accuracy suite à un nouveau modèle), l'agent bascule immédiatement le trafic vers la version `N-1`.
- `NOTIFY_ONCALL` : L'agent alerte l'ingénieur d'astreinte sur Slack/PagerDuty en lui poussant directement le contexte pré-mâché, les logs pertinents et la décision qui a été prise.

---

## Installation & Tests (E2E Validation)

```bash
# 1. Préparation de l'environnement
git clone https://github.com/nolll77/agentic-ops.git
cd agentic-ops-core
uv venv .venv
source .venv/bin/activate
uv pip install -e .
uv pip install 'httpx[socks]'

# 2. Exécuter l'Intégration Continue de Sécurité E2E (Red-Team + Connecteur CAC MLOps)
PYTHONPATH=. pytest tests/ -v
# > Vérifie l'immutabilité WORM, le Fail-Closed de la Gouvernance,
# > l'incapacité de contournement de l'Orchestrateur et les 13 tests de CacPullCollector.

# 3. Lancer la TUI d'Audit du Trust Ledger
python -m agentic_ops.cli.trust_ledger list
```

---

## Documentation de Référence et Preuves de Déploiement

1. **[Main Documentation in English (`README.md`)](README.md)** :
   Version anglaise principale du dépôt.
2. **[Rapport de Validation Cloud Sandbox (`DOCKER_SANDBOX_VALIDATION.md`)](DOCKER_SANDBOX_VALIDATION.md)** :
   Déploiement sur micro-VM isolée (4 vCPUs AMD EPYC, 8 Go de RAM), exécution commentée des 30 tests de sécurité (`forbidden_executed = 0`), rejet `HTTP 401 Unauthorized` sur les webhooks non signés, et captures d'écran de session.
3. **[Architecture et Validation du Connecteur Tailscale Pull (`CAC_TAILSCALE_PULL_CONNECTOR.md`)](CAC_TAILSCALE_PULL_CONNECTOR.md)** :
   Documentation complète de l'interconnexion avec [`https://github.com/jakatt/cac_mlops`](https://github.com/jakatt/cac_mlops) (`100.117.99.62`), configuration du démon `tailscaled` en mode `userspace-networking` (`SOCKS5 127.0.0.1:1055`), diagnostic des relais `DERP`, anatomie de `cac_pull_collector.py`, et détail des 13 tests unitaires.
4. **[Guide d'Intégration Générique (`INTEGRATION_GUIDE.md`)](INTEGRATION_GUIDE.md)** :
   Spécifications de branchement d'`Agentic-Ops` sur une infrastructure MLOps tierce.
