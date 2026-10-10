# 🌌 Genèse du Projet Agentic-Ops

Le projet **Agentic-Ops** n'est pas né d'une page blanche. Il s'agit d'une extraction architecturale (spin-off) issue du dépôt monolithique originel : **[nolll77/car_accident](https://github.com/nolll77/car_accident)**.

---

## 1. Origine : Le Monolithe "car_accident"
Le dépôt originel `car_accident` était un immense monorepo MLOps regroupant l'ensemble de la chaîne de valeur :
- Les données brutes (ONISR).
- Les pipelines d'entraînement (Data Engineering & ML Engineering).
- Le déploiement de l'API (FastAPI).
- **Le Control Plane expérimental d'orchestration LLM**.

Au fur et à mesure que l'architecture a gagné en maturité, il est devenu évident que le "cerveau" (les agents LLM) ne devait pas cohabiter dans le même dépôt que les "muscles" (les modèles de Machine Learning et les APIs).

## 2. L'Extraction : Naissance d'Agentic-Ops
Pour respecter les principes SRE de "Séparation des Responsabilités" (Separation of Concerns) et de **Zero-Trust**, le Control Plane autonome a été extrait dans ce dépôt dédié : `agentic-ops-core`.

Cette scission a permis :
1. **L'Agnosticisme** : Agentic-Ops peut désormais se brancher sur n'importe quel projet MLOps (y compris le dépôt de production `plateforme_cible`), et non plus seulement sur le repo historique `car_accident`.
2. **Le Durcissement** : L'implémentation de politiques de sécurité draconiennes (Policy-as-Code, Evidence Store, Prompt Guard).

---

## 3. Schéma de Séparation (Spin-off)

```mermaid
flowchart TD
    %% Historique
    subgraph Monorepo_Historique ["Dépôt Originel (car_accident)"]
        direction TB
        Pipeline_ML["Pipelines ML & Data"]
        Inference["Inférence (API)"]
        Exp_Agents["Agents LLM Expérimentaux"]
    end

    %% Le Spin-off
    Exp_Agents -- "Refactoring & Extraction
(Séparation des Pouvoirs)" --> Agentic_Ops

    %% Nouvelle Architecture
    subgraph Dépôt_Agentic_Ops ["Ce Dépôt : agentic-ops-core"]
        direction TB
        Orchestrateur["Orchestrateur FSM"]
        Policy["Policy Engine"]
        Sec_Agents["Agents Spécialisés Sécurisés"]
    end

    subgraph Dépôts_Cibles ["Dépôts d'Exécution Tiers (plateforme_cible, etc.)"]
        direction TB
        External_Pipelines["Pipelines Airflow / Prefect"]
        External_K8s["Clusters Kubernetes"]
    end

    Dépôt_Agentic_Ops -- "API Calls & Webhooks
(Agnostique)" --> Dépôts_Cibles

    %% Style
    classDef old fill:#ffebee,stroke:#c62828,stroke-width:2px,stroke-dasharray: 5 5;
    classDef new fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px;
    classDef target fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
    
    class Monorepo_Historique old;
    class Dépôt_Agentic_Ops new;
    class Dépôts_Cibles target;
```
