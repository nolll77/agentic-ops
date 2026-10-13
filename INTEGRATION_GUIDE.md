# Guide d'Intégration Spécifique : Agentic-Ops et Plateforme Cible

Ce guide explique pas à pas comment connecter l'architecture **Agentic-Ops** (Control Plane Agentique) à **n'importe quel dépôt d'exécution MLOps cible**.

`Agentic-Ops` agit comme le **cerveau** (SRE autonome gouverné) tandis que la plateforme cible fournit les **muscles** (Data Engineering, infrastructure, entraînement et inférence des modèles).

---

## 1. Philosophie de Connexion (Decoupled Architecture)

### A. La Couche d'Exécution (La Plateforme Cible)
La plateforme MLOps de production (ex: `CAC MLOps`, `Rakuten`, `Olist`, `Vélib'`, etc.) gère :
- L'acquisition et le stockage de la donnée
- Le feature engineering
- Le Model Training & Registry (`MLflow`)
- Le déploiement de l'API (`FastAPI`, `Docker`, `Kubernetes`)
- La télémétrie de base (`Evidently`, `Prometheus`, `Grafana`, `Loki`)

### B. La Couche Agentique (`Agentic-Ops`)
Le Control Plane vient se brancher "par-dessus" cette infrastructure. Il intercepte l'alerte (ou collecte les métriques en mode `Pull` via `CacPullCollector`), mandate des agents LLM en lecture seule pour analyser les logs et les métriques de la plateforme cible, puis déclenche les actions de réparation (via `Prefect`, `Airflow`, `MLflow` ou `Kubernetes`) uniquement après validation par le `PolicyEngine` et approbation humaine sécurisée via `Slack` (`HMAC-SHA256`).

```mermaid
%%{init: {'theme': 'dark', 'themeVariables': {'lineColor': '#94a3b8', 'primaryTextColor': '#f8fafc'}}}%%
flowchart TD

    %% Palette Semantique Dark-Mode
    classDef platform fill:#0c2d48,stroke:#38bdf8,stroke-width:2px,color:#e0f2fe;
    classDef cognitive fill:#2e1065,stroke:#c084fc,stroke-width:2px,color:#f3e8ff;
    classDef guardrail fill:#451a03,stroke:#f59e0b,stroke-width:2px,color:#fef3c7;
    classDef executor fill:#064e3b,stroke:#34d399,stroke-width:2px,color:#d1fae5;

    subgraph Plateforme_Cible ["Couche Data Engineering & MLOps Cible"]
        A["Data Ingestion"]:::platform --> B["Orchestrateur : Prefect / Airflow"]:::platform
        B --> C["Model Registry : MLflow"]:::platform
        C --> D["Runtime Inference : FastAPI / K8s"]:::platform
        D --> E["Observabilite : Evidently / Prometheus"]:::platform
        E --> F["Grafana / Loki Alerting"]:::platform
    end

    subgraph Agentic_Ops ["Agentic-Ops (Governance Control Plane)"]
        G["Webhook Receiver & Pull Collector (FastAPI)"]:::cognitive
        H["Orchestrator FSM & Agents LLM"]:::cognitive
        I["Evidence Store & Trust Ledger WORM"]:::executor
        J["Policy Engine & Approbation Slack HITL"]:::guardrail
    end

    style Plateforme_Cible fill:#071929,stroke:#38bdf8,stroke-width:2px,color:#e0f2fe
    style Agentic_Ops fill:#160b30,stroke:#c084fc,stroke-width:2px,color:#f3e8ff

    F -- "1. Webhook HTTP / Collecte Pull" --> G
    G --> H
    H -- "2. Evaluation & Demande HITL" --> J
    J -- "3. Validation Signee (HMAC-SHA256)" --> H
    H -- "4. Scellement Cryptographique" --> I
    H -- "5. Retrain (POST API)" --> B
    H -- "6. Rollback / Scale" --> D

    linkStyle 0,1,2,3,4,5 stroke:#38bdf8,stroke-width:2px;
    linkStyle 6,7 stroke:#c084fc,stroke-width:2px;
    linkStyle 8,9 stroke:#f59e0b,stroke-width:2px;
    linkStyle 10,11,12 stroke:#34d399,stroke-width:2px;
```

---

## 2. Pré-requis Réseaux (`Tailscale` / VPN)

L'infrastructure cible est généralement isolée derrière **`Tailscale`** ou un VPC privé.
Le serveur ou conteneur exécutant `Agentic-Ops` démarre le démon `tailscaled` (en mode noyau ou en mode `--tun=userspace-networking` avec proxy `SOCKS5` local sur `127.0.0.1:1055`) et rejoint le même réseau (`Tailnet`) que la cible pour permettre la communication inter-APIs de bout en bout sans exposer les ports d'administration sur Internet.

---

## 3. Configuration de l'Interception des Alertes (`Grafana` -> `Agentic-Ops`)

Lorsque la plateforme cible détecte une dérive via `Evidently` ou `Prometheus`, les alertes peuvent être routées vers le Control Plane :

1. Lancer l'API `FastAPI` d'`Agentic-Ops` sur le port `8001` (ou `7860` en mode PaaS Auto-Wake). L'endpoint d'écoute est `/webhooks/grafana`.
2. L'URL complète sur le réseau `Tailscale` sera par exemple : `http://100.102.123.121:8001/webhooks/grafana`.
3. Ouvrir l'interface **Grafana** de la plateforme cible.
4. Aller dans `Alerting > Contact points > Add contact point`.
5. Choisir le type **Webhook**, coller l'URL d'`Agentic-Ops`, et sauvegarder.
6. Assigner ce Contact Point aux règles d'alerte (ex: `Data Drift Alert`).

Tout franchissement de seuil réveillera automatiquement l'`Orchestrator FSM`. En complément ou en alternative 100 % sans modification de la cible, le module [`CacPullCollector`](agentic_ops/adapters/cac_pull_collector.py) permet d'interroger les 5 services en mode `Pull` lecture seule (`GET`).

---

## 4. Configuration de la Lecture des Télémétries (`Agentic-Ops` -> `MLflow` / `Prometheus` / `Loki`)

L'agent enquêteur analyse l'état du système cible en lecture seule stricte.
Dans le fichier `.env` d'`Agentic-Ops`, configurez les URLs d'accès aux services de la cible :

```ini
# Acces en lecture seule aux metriques et logs de la cible
TARGET_LOKI_URL=http://100.117.99.62:3100
TARGET_PROMETHEUS_URL=http://100.117.99.62:9090
TARGET_MLFLOW_URL=http://100.117.99.62:5001
TARGET_DRIFT_REPORT_URL=https://mlops.jakat-inc.fr/reports/drift/latest_summary.json
```
*(Adaptez l'adresse IP `Tailscale` à celle du serveur cible).*

---

## 5. Configuration de l'Exécution Gouvernée (`Agentic-Ops` -> Orchestrateur Cible)

Une fois le diagnostic établi, l'intention validée de manière déterministe par le `PolicyEngine` et approuvée par un opérateur humain habilité via `Slack`, le module `Executor` d'`Agentic-Ops` est le seul composant autorisé à émettre l'appel d'écriture vers la cible :

```ini
# Acces d'execution gouvernee (exclusivement utilise par Executor apres validation HITL)
TARGET_PREFECT_URL=http://100.117.99.62:4200
TARGET_API_KEY=pnu_xxxxxxxxx
```

---

## 6. Scénario de Validation de Bout en Bout (Auto-Guérison Gouvernée)

Voici la séquence opérationnelle permettant de vérifier l'intégration complète en conditions réelles :

1. **Vérification initiale** : Contrôler l'état nominal des services de la plateforme cible (`GET /api/cac/snapshot`).
2. **Injection d'anomalie** : Déclencher une dérive statistique des données (`cac_mlops_drift_share > seuil`) ou un événement d'alerte `Loki` (`event=alert`).
3. **Observabilité et Gouvernance en direct** :
   - **Ingestion** : `Agentic-Ops` détecte l'alerte et extrait les faits système (`compute_facts()`).
   - **Diagnostic** : L'agent analyse les métriques `MLflow` et le rapport `Evidently`, puis émet une intention `TRIGGER_RETRAINING`.
   - **Garde-Fou (`Fail-Closed`)** : Le `PolicyEngine` classe l'action en `REQUIRE_APPROVAL`, fige la machine à états en `AWAITING_APPROVAL` et envoie une notification interactive **Slack Block Kit**.
   - **Approbation Humaine (`HITL`)** : L'ingénieur SRE clique sur **`[ APPROVE ]`** dans Slack (requête signée `HMAC-SHA256`).
4. **Exécution et Traçabilité Cryptographique** :
   - L'`Orchestrator` vérifie la signature, déverrouille la transaction atomique (`SQLite BEGIN IMMEDIATE`) et délègue l'appel à l'`Executor`.
   - L'orchestrateur de pipelines cible (`Prefect` / `Airflow`) lance le ré-entraînement.
   - **`Agentic-Ops`** scelle l'épisode complet dans le **`Trust Ledger WORM`** (`SHA-256` + `HMAC-SHA512`).
