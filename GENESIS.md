# Genèse du Projet Agentic-Ops

Le projet **Agentic-Ops** n'est pas né d'une page blanche. Il s'agit d'une extraction architecturale (*spin-off*) issue du dépôt monolithique originel : **[nolll77/car_accident](https://github.com/nolll77/car_accident)**.

---

## 1. Origine : Le Monolithe `car_accident`
Le dépôt originel `car_accident` était un monorepo MLOps regroupant l'ensemble de la chaîne de valeur :
- Les données brutes (`ONISR`).
- Les pipelines d'entraînement (Data Engineering & ML Engineering).
- Le déploiement de l'API (`FastAPI`).
- **Le Control Plane expérimental d'orchestration LLM**.

Au fur et à mesure que l'architecture a gagné en maturité, il est devenu évident que le "cerveau" (les agents LLM et le moteur de politiques) ne devait pas cohabiter dans le même dépôt que les "muscles" (les modèles de Machine Learning et les APIs d'inférence).

## 2. L'Extraction : Naissance d'`Agentic-Ops`
Pour respecter les principes SRE de "Séparation des Responsabilités" (*Separation of Concerns*) et de **Zero-Trust**, le Control Plane autonome a été extrait dans ce dépôt dédié : `agentic-ops-core`.

Cette scission a permis :
1. **L'Agnosticisme** : `Agentic-Ops` peut désormais se brancher sur n'importe quel projet MLOps (y compris la plateforme de production [`jakatt/cac_mlops`](https://github.com/jakatt/cac_mlops)), et non plus seulement sur le dépôt historique `car_accident`.
2. **Le Durcissement** : L'implémentation de politiques de sécurité strictes (*Policy-as-Code*, `Evidence Store WORM`, `Prompt Guard`, `Slack HITL HMAC-SHA256`).

---

## 3. Schéma de Séparation (`Spin-off`)

```mermaid
%%{init: {'theme': 'dark', 'themeVariables': {'lineColor': '#94a3b8', 'primaryTextColor': '#f8fafc'}}}%%
flowchart TD

    classDef platform fill:#0c2d48,stroke:#38bdf8,stroke-width:2px,color:#e0f2fe;
    classDef cognitive fill:#2e1065,stroke:#c084fc,stroke-width:2px,color:#f3e8ff;
    classDef guardrail fill:#451a03,stroke:#f59e0b,stroke-width:2px,color:#fef3c7;
    classDef executor fill:#064e3b,stroke:#34d399,stroke-width:2px,color:#d1fae5;

    subgraph Monorepo_Historique ["Depot Originel (nolll77/car_accident)"]
        direction TB
        Pipeline_ML["Pipelines ML & Data"]:::platform
        Inference["Inference (FastAPI)"]:::platform
        Exp_Agents["Agents LLM Experimentaux"]:::guardrail
    end

    subgraph Depot_Agentic_Ops ["Ce Depot : agentic-ops-core (Control Plane)"]
        direction TB
        Orchestrateur["Orchestrator FSM"]:::cognitive
        Policy["Policy Engine & Slack HITL"]:::guardrail
        Sec_Agents["Executor & Trust Ledger WORM"]:::executor
    end

    subgraph Depots_Cibles ["Plateformes d'Execution Cibles (jakatt/cac_mlops, etc.)"]
        direction TB
        External_Pipelines["Pipelines Prefect / Airflow & MLflow"]:::platform
        External_K8s["Clusters Kubernetes & Observabilite"]:::platform
    end

    style Monorepo_Historique fill:#271102,stroke:#f59e0b,stroke-width:2px,stroke-dasharray: 5 5,color:#fef3c7
    style Depot_Agentic_Ops fill:#160b30,stroke:#c084fc,stroke-width:2px,color:#f3e8ff
    style Depots_Cibles fill:#071929,stroke:#38bdf8,stroke-width:2px,color:#e0f2fe

    Exp_Agents -- "1. Extraction & Durcissement (Separation des Pouvoirs)" --> Orchestrateur
    Orchestrateur --> Policy
    Policy --> Sec_Agents
    Sec_Agents -- "2. Collecte Pull (GET) & Actions Gouvernees (POST)" --> External_Pipelines
    Sec_Agents -- "3. Supervision & Remediation" --> External_K8s

    linkStyle 0 stroke:#f59e0b,stroke-width:2px;
    linkStyle 1,2 stroke:#c084fc,stroke-width:2px;
    linkStyle 3,4 stroke:#34d399,stroke-width:2px;
```
