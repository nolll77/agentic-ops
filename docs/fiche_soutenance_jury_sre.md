# 🎓 Guide de Soutenance & Réponses aux Questions-Pièges du Jury (SRE / SecOps)

> **Document de préparation intensive** pour la soutenance du Control Plane **Agentic-Ops**.  
> Ce guide rassemble le pitch d'ouverture, les 3 questions-pièges éliminatoires avec leurs réponses chirurgicales, la formalisation mathématique de la FSM, et le déroulé de la démonstration live.

---

## ⚡ 1. Pitch d'Ouverture (1 minute chrono)

> *"Bonjour à tous. Aujourd'hui, la quasi-totalité des architectures multi-agents sur le marché (type LangChain ou CrewAI) souffrent d'une faille structurelle inadmissible en production : elles donnent à des modèles de langage stochastiques le pouvoir d'exécuter directement des actions destructrices sans garde-fous déterministes.*
> 
> *Avec **Agentic-Ops**, nous avons pris le contre-pied absolu de cette approche. Nous avons conçu un **Control Plane MLOps SRE Défensif**, agnostique de l'infrastructure sous-jacente. Notre système applique une séparation stricte des pouvoirs : **l'Agent LLM propose, mais le code déterministe impose**.*
> 
> *Grâce à une machine à états finis inviolable, une politique Fail-Closed `autonomy_policy.yaml`, un pont réseau privé chiffré **Tailscale** et un registre de preuves immuable de type blockchain locale (**Trust Ledger WORM**), nous garantissons zéro hallucination en production, une traçabilité mathématique infalsifiable et une continuité de service irréprochable face aux dérives de modèles."*

---

## 🎯 2. Les 3 Questions-Pièges du Jury & Réponses Chirurgicales

### ❓ Question 1 : Le piège de la "Double Exécution" (Race Condition / Concurrence)
**Le Jury :**  
*« Si votre système reçoit deux webhooks d'alerte identiques d'Evidently AI au même instant, ou si l'administrateur clique deux fois rapidement sur le bouton d'approbation Slack, comment votre architecture empêche-t-elle de déclencher deux réentraînements Prefect simultanés sur le serveur cible ? »*

**💡 Votre réponse chirurgicale :**  
> « C'est un problème classique de concurrence distribuée que nous avons résolu par le principe d'**Idempotence Sémantique** et de **Verrouillage Atomique via `Redis`**.  
> Dès que la FSM traite une intention, un verrou distribué de type `SET NX EX` est posé dans notre cache `Redis`. La clé de ce verrou est calculée de manière déterministe à partir de l'empreinte sémantique de l'incident : un tuple `tenant:environment:risk_id`.  
> Si un second clic ou une alerte dupliquée arrive pendant que le premier épisode est à l'état `EXECUTING`, le second thread échoue immédiatement à acquérir le verrou `Redis`. Le système applique alors une politique stricte de **Fail-Closed** : la transaction concurrente est rejetée (`409 Conflict`), et l'ordre de mutation n'est transmis qu'une seule fois à l'orchestrateur distant, protégeant ainsi l'infrastructure et le budget cloud (FinOps). »

---

### ❓ Question 2 : Le piège de la disponibilité réseau (Split-Brain / Panne Tailscale)
**Le Jury :**  
*« Votre solution tourne dans une Sandbox Docker et communique via Tailscale. Que se passe-t-il si la connexion réseau entre votre Control Plane et le serveur distant se coupe au moment précis où vous cliquez sur "Approuver" sur Slack ? Votre FSM ne va-t-elle pas se désynchroniser ? »*

**💡 Votre réponse chirurgicale :**  
> « Non, car notre **Architecture Hexagonale** applique une séparation étanche entre la transition d'état logique et la mutation physique, couplée à une gestion rigoureuse des erreurs réseau.  
> Lorsque le webhook Slack est validé, la FSM passe à l'état `EXECUTING` et mandate le module `executor.py`. L'exécuteur utilise un client HTTP synchrone durci via la librairie `httpx`, configuré avec un **Timeout strict de 15 secondes**.  
> Si le tunnel `Tailscale` est rompu, la tentative de connexion vers l'IP cible lève immédiatement une exception `ConnectTimeout`. Notre code intercepte cette exception : l'exécuteur renvoie un statut réel `FAILED` (et non un faux statut simulé). La machine à états rétrograde immédiatement l'épisode vers le statut de sécurité `DENIED`, et cet échec réseau est immédiatement scellé dans le **Trust Ledger**. Il n'y a aucun état fantôme, aucune désynchronisation possible. »

---

### ❓ Question 3 : Le piège de la sécurité du Trust Ledger (Anti-Tampering / Accès Root)
**Le Jury :**  
*« Votre fichier d'audit `trust_ledger.jsonl` est stocké localement. Si un attaquant parvient à s'introduire sur votre machine avec des droits root, il peut simplement éditer le fichier pour effacer ses traces ou falsifier l'historique de vos actions. À quoi sert votre sécurité cryptographique ? »*

**💡 Votre réponse chirurgicale :**  
> « C'est précisément pour cela que notre Trust Ledger n'utilise pas de simples logs textuels, mais une architecture cryptographique combinant une chaîne linéaire de hachage WORM (Write Once, Read Many) et un Arbre de Merkle RFC 6962.  
> Même avec des droits root, un attaquant fait face à une barrière mathématique : chaque ligne du fichier contient le champ `previous_hash`, qui dépend du hachage SHA-256 complet de la ligne précédente. Si un attaquant modifie une décision passée (par exemple changer un `REQUIRE_APPROVAL` en `ALLOW`), le hachage de cette ligne change. Par effet domino, la liaison avec le bloc suivant est mathématiquement brisée.  
> Au démarrage du système ou lors de l'audit automatisé via `agentic-audit`, la méthode `verify_chain_integrity()` recalcule l'intégralité des empreintes. Elle détecte instantanément la rupture de l'invariant cryptographique, refuse de démarrer l'application et lève une alerte de falsification (**Tamper-Evident**). En production, ce fichier `.jsonl` a vocation à être répliqué en continu vers un stockage immuable de type AWS S3 configuré avec **S3 Object Lock** (mode Compliance). »

---

## 📊 3. Formalisation Mathématique de la Machine à États Finis (FSM)

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#ffffff', 'primaryTextColor': '#000000', 'lineColor': '#333333'}}}%%
flowchart TD
    %% Style global pour lisibilité (Thème Clair forcé)
    classDef default fill:#ffffff,stroke:#333333,stroke-width:2px,color:#000000;
    classDef agentic fill:#f3e5f5,stroke:#8e24aa,stroke-width:2px,color:#000000;
    classDef cible fill:#e3f2fd,stroke:#1976d2,stroke-width:2px,color:#000000;
    classDef alert fill:#ffebee,stroke:#d32f2f,stroke-width:2px,color:#000000;

    S1["[ DETECTED ]<br/>Alerte Webhook Inbound"] --> S2["[ INVESTIGATING ]<br/>compute_facts() via Tailscale"]
    S2 --> S3["[ DIAGNOSED & PLANNED ]<br/>ActionIntent formulée par LLM"]
    S3 --> S4{"PolicyEngine<br/>(autonomy_policy.yaml)"}
    
    S4 -- "ALLOW (Low Risk)" --> S6["[ EXECUTING ]<br/>Mutation physique via Executor"]
    S4 -- "REQUIRE_APPROVAL (High Risk)" --> S5["[ AWAITING_APPROVAL ]<br/>Fail-Closed / Slack HITL"]
    
    S5 -- "Clic Slack + Signature HMAC valide" --> S6
    S5 -- "Refus humain ou Signature invalide" --> S8["[ DENIED ]<br/>Scellage WORM"]
    
    S6 -- "Succès API distante (200 OK)" --> S7["[ RESOLVED ]<br/>Scellage WORM SHA-256"]
    S6 -- "Timeout réseau / Échec API" --> S8
```

### Table des Invariants & Sécurités de Code

| État | Événement Déclencheur | Invariant SRE / Sécurité Active |
|:---|:---|:---|
| `DETECTED` | Webhook HTTP POST (Evidently / Prometheus) | Génération d'un `risk_id` unique et timestamp initial non altérable. |
| `INVESTIGATING` | Transition automatique vers `compute_facts()` | Confinement des données distantes dans des balises XML `<untrusted_data>` contre les **injections de prompts**. Lecture seule via `Tailscale`. |
| `PLANNED` | Proposition d'action par l'Agent LLM | Interception immédiate par le `PolicyEngine`. L'Agent LLM ne possède aucun socket réseau mutant. |
| `AWAITING_APPROVAL`| Décision `REQUIRE_APPROVAL` | **Fail-Closed absolu** : suspension du thread. Envoi d'un message interactif Slack Block Kit. |
| `EXECUTING` | Clic Slack de validation | Validation de l'en-tête HMAC-SHA256 en temps constant (`hmac.compare_digest`), fenêtre anti-rejeu $\Delta t \le 300\text{s}$, puis appel HTTP via `executor.py`. |
| `RESOLVED` / `DENIED` | Fin d'exécution physique | Calcul du hash SHA-256 canonique du bloc, chaînage au `previous_hash` et écriture Append-Only dans `trust_ledger.jsonl`. |

---

## 🌐 4. Topologie Réseau & Architecture d'Isolation

```
┌──────────────────────────────────────┐       ┌─────────────────────────────────────────────────────────┐
│     SERVEUR D'EXÉCUTION MLOPS        │       │             CONTROL PLANE AGENTIC-OPS                   │
│         (Infrastructure Cible)       │       │                (Docker Sandbox Cloud)                   │
│                                      │       │                                                         │
│   - Model Registry : MLflow          │       │   ┌──────────────────────┐   ┌──────────────────────┐   │
│   - Orchestrateur : Prefect/Airflow  │       │   │  API Webhook Listener│   │  Orchestrator FSM    │   │
│   - Observabilité : Evidently/Grafana│       │   │  (FastAPI Port 8001) │   │  - INVESTIGATING     │   │
│                                      │       │   └──────────────────────┘   │  - AWAITING_APPROVAL │   │
│                                      │       │               │              │  - EXECUTING         │   │
│                                      │       │               v              └──────────────────────┘   │
│                                      │       │   ┌──────────────────────┐              │               │
│                                      │       │   │  Policy Engine YAML  │              v               │
│                                      │       │   │ (autonomy_policy.yml)│   ┌──────────────────────┐   │
│                                      │       │   └──────────────────────┘   │  Executor Actuator   │   │
│                                      │       │                              │  (Client HTTPX durci)│   │
│                                      │       │                              └──────────────────────┘   │
│                                      │       │   ┌──────────────────────┐              │               │
│                                      │       │   │  Trust Ledger (WORM) │              │               │
│                                      │       │   │ (trust_ledger.jsonl) │<─────────────┘               │
│                                      │       │   └──────────────────────┘                              │
└──────────────────▲───────────────────┘       └───────────────────────────────────▲─────────────────────┘
                   │                                                               │
                   │        ================================================       │
                   └─────── [  TUNNEL PRIVÉ SÉCURISÉ TAILSCALE (L3 OVERLAY) ] ─────┘
                            - Chiffrement WireGuard de bout en bout
                            - Zéro port ouvert sur Internet public
                            - Mode Userspace (TS_USERSPACE=true)
```

---

## 🎬 5. Déroulé de la Démonstration Live (Runbook)

### Lancement du script automatisé
Pour dérouler toute la séquence sous les yeux du jury, placez-vous à la racine et exécutez :
```bash
./scripts/demo_agentic_ops.sh
```

### Le Choix Stratégique pour Slack : Option 1 vs Option 2
* **Option 1 (Vrai Slack sur smartphone)** : Si vous avez une connexion 4G/Wifi irréprochable et un Workspace configuré, montrez la notification push sur votre téléphone. L'effet "waouh" est garanti.
* **Option 2 (Simulation Console / Recommandée en SRE)** : Expliquez au jury :  
  *« En tant qu'ingénieur SRE, j'applique le principe de précaution face à l'aléa réseau d'une salle de soutenance. Le Control Plane se fige en état Fail-Closed dans la console. Je valide l'action via le terminal, ce qui prouve de manière identique la vérification HMAC et le déblocage de la FSM. »*
