# 🔌 Guide d'Intégration Spécifique : Agentic-Ops 🤝 Plateforme Cible

Ce guide est destiné à expliquer pas à pas comment connecter l'architecture **Agentic-Ops** (Control Plane Agentique) à **n'importe quel dépôt d'exécution MLOps cible**.

Agentic-Ops agit comme le **cerveau** (SRE autonome) tandis que la plateforme cible fournit les **muscles** (Data Engineering, infrastructure, modèles).

## 1. Philosophie de Connexion (Decoupled Architecture)

### A. La Couche d'Exécution (La Plateforme Cible)
La plateforme MLOps classique (votre projet de fin d'études, Rakuten, Olist, Vélib', etc.) gère :
- L'acquisition de la donnée
- Le feature engineering
- Le Model Training & Registry (MLflow)
- Le déploiement de l'API (FastAPI, Docker, Kubernetes)
- La télémétrie de base (Evidently, Prometheus, Grafana)

### B. La Couche Agentique (Agentic-Ops)
Notre projet vient se brancher "par-dessus" cette infrastructure. Il intercepte l'alerte, mandate des agents LLM pour analyser les logs et les métriques de la plateforme cible, puis déclenche les actions de réparation (via Prefect, Airflow, ou Kubernetes) après une validation humaine ultra-rapide et sécurisée (via Slack).

```mermaid
graph TD

    %% Style global pour lisibilité (Thème Clair forcé)
    classDef default fill:#ffffff,stroke:#333333,stroke-width:2px,color:#000000;
    classDef agentic fill:#f3e5f5,stroke:#8e24aa,stroke-width:2px,color:#000000;
    classDef cible fill:#e3f2fd,stroke:#1976d2,stroke-width:2px,color:#000000;
    classDef alert fill:#ffebee,stroke:#d32f2f,stroke-width:2px,color:#000000;
    subgraph Plateforme_Cible ["🛠️ Couche Data Eng & MLOps Cible"]
        A(Data Ingestion) --> B(Prefect / Airflow)
        B --> C(MLflow Registry)
        C --> D(FastAPI / K8s Inférence)
        D --> E{Evidently / Prometheus}
        E --> F[Grafana Alerting]
    end

    subgraph Agentic_Ops ["🧠 Agentic-Ops (Control Plane)"]
        F -- "Webhook HTTP (Alerte)" --> G[Webhook Receiver (FastAPI)]
        G --> H((Agent SRE Orchestrator))
        H <--> I[(Memory & RAG)]
        H -- "Approbation Humaine (Slack)" --> J[Ingénieur d'Astreinte]
        H -- "Exécution (API REST)" --> B
        H -- "Rollback / Scale" --> D
    end

    class Agentic_Ops agentic;
    class Plateforme_Cible cible;
```

## 2. Pré-requis Réseaux (Tailscale / VPN)

L'infrastructure cible est potentiellement sécurisée derrière **Tailscale** ou un VPC fermé.
👉 Le serveur exécutant `Agentic-Ops` doit installer Tailscale et rejoindre le même réseau (Tailnet) que la cible pour permettre la communication entre les APIs en toute sécurité, sans ouvrir les ports au web public.

## 3. Configuration de l'Interception des Alertes (Grafana -> Agentic-Ops)

Actuellement, la plateforme cible envoie peut-être des emails ou des alertes Slack directes lorsqu'Evidently détecte une dérive. Nous allons câbler ces alertes vers notre système autonome.

1. Lancer l'API FastAPI de `Agentic-Ops` sur le port 8000. L'endpoint d'écoute est `/webhooks/grafana`.
2. L'URL complète sur le réseau Tailscale sera par exemple : `http://100.117.99.123:8000/webhooks/grafana`
3. Ouvrir le **Grafana** de la plateforme cible.
4. Aller dans `Alerting > Contact points > Add contact point`.
5. Choisir le type **Webhook**, coller l'URL de `Agentic-Ops`, et sauvegarder.
6. Assigner ce Contact Point aux règles d'alerte (ex: `Data Drift Alert`).

Désormais, tout franchissement de seuil réveillera l'Agent SRE.

## 4. Configuration de la Lecture des Télémétries (Agentic-Ops -> MLflow/Prometheus)

L'agent a besoin d'analyser l'état du système de la cible.
Dans le fichier `.env` de `Agentic-Ops`, configurez les URLs d'accès aux services de la cible :

```ini
# Accès en lecture aux métriques de la cible
TARGET_MLFLOW_URL=http://100.117.99.62:5001
TARGET_PROMETHEUS_URL=http://100.117.99.62:9090
TARGET_API_URL=http://100.117.99.62:8000
```
*(Remplacez l'IP par celle de la machine cible sur Tailscale).*

## 5. Configuration de l'Exécution (Agentic-Ops -> Orchestrateur Cible)

Une fois le diagnostic établi et l'action validée mathématiquement par notre *Policy Engine* et approuvée par un humain via Slack, l'Executor d'Agentic-Ops doit déclencher l'action chez la cible.

1. Créer une **API Key** dans l'interface de l'orchestrateur cible (Prefect, Airflow, etc.).
2. Dans le `.env` de `Agentic-Ops`, renseigner :

```ini
# Accès en écriture pour déclencher des actions
TARGET_PREFECT_URL=http://100.117.99.62:4200
TARGET_API_KEY=pnu_xxxxxxxxx
```

## 6. Scénario de Démonstration (Soutenance)

Voici la chorégraphie exacte à suivre lors de la soutenance pour prouver la pleine intégration :

1. Montrer le Cockpit de la plateforme cible opérationnel.
2. Déclencher un script de simulation de dérive (`simulate_drift.py`) sur la plateforme cible.
3. Observabilité en direct :
   - **Grafana** (cible) s'affole et tire le Webhook.
   - Les logs de **Agentic-Ops** s'animent : l'agent reçoit l'alerte, analyse les données MLflow, et propose un `TRIGGER_RETRAINING`.
   - Notification **Slack** : vous montrez le message interactif sur votre téléphone/écran.
   - Vous cliquez sur **"Approuver"** dans Slack.
4. Auto-Guérison en direct :
   - L'interface **Prefect/Airflow** (cible) démarre toute seule son pipeline de ré-entraînement.
   - **Agentic-Ops** consigne l'action dans le *Trust Ledger* immuable.

🎉 Le jury vient d'assister à l'auto-guérison d'une architecture MLOps par une IA autonome.
