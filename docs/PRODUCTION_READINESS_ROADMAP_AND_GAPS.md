# Roadmap de Durcissement Production & Levée des Écarts (Enterprise MLOps Readiness)

> **Document de Référence d'Ingénierie & d'Honnêteté Radicale**  
> **Auteur** : Équipe MLOps / SRE  
> **Statut** : Document d'Architecture Cible & Spécifications des Prochaines Étapes (*Next Steps*)  
> **Périmètre** : Transition du prototype de gouvernance solo vers une plateforme industrielle de classe entreprise (*"Pour être un vrai"*).

---

## 1. Contexte & Démarche d'Ingénierie

À la suite de la contre-expertise chirurgicale du commit `06f6bb6` (validé par `144 passed, 3 skipped, 1 xfail`), ce document formalise avec une **lucidité technique absolue** l'ensemble des écarts existants entre notre plan de contrôle actuel et les exigences d'une infrastructure MLOps de mission critique en entreprise (normes ISO 42001, EU AI Act, SOC 2 Type II).

Dans un projet mené en solo, implémenter un plan de contrôle complet (contrats Pandera, veto déterministe `PolicyEngine`, FSM à 5 états, indexation in-memory de 435 pannes, signatures HMAC Slack et chaînage cryptographique) représente déjà un niveau d'architecture avancé. Toutefois, pour qu'Agentic-Ops devienne un **"vrai" orchestrateur autonome de production**, plusieurs verrous techniques fondamentaux doivent être levés.

Ce document constitue la **feuille de route d'industrialisation (Roadmap Next Steps)**.

---

## 2. Matrice Synthétique des Écarts & Spécifications Cibles

| Dimension Architecturale | État Actuel (Prototype Avancé / Solo) | Écart Identifié par l'Audit | Spécification Cible (*"Pour être un vrai"*) | Priorité & Stack Cible |
| :--- | :--- | :--- | :--- | :--- |
| **1. Ingestion d'Alertes** | Adaptateur HTTP `POST /webhook/alerts` validant le JSON et comptant les alertes (`202 Accepted`). | Aucune transmission asynchrone vers l'orchestrateur (pas de boucle fermée). | File d'attente découplée (Redis Streams / Kafka), mapping d'alertes vers la taxonomie et réveil automatique de la FSM. | **P0** (`Redis Streams`, `Celery`/`arq`) |
| **2. Exécution des Actions** | `_resume_from_claim` se borne à journaliser l'approbation (`logging.info`). Mode simulation par défaut. | L'agent n'exécute aucune action sur l'infrastructure cible lors de l'approbation humaine. | Workers d'exécution asynchrones branchés sur Kubernetes API / Argo Workflows / MLflow avec rollback et validation canary. | **P0** (`kubernetes-client`, `temporal.io` ou `arq`) |
| **3. Authentification & Sécurité d'Accès** | Endpoints de diagnostic (`/api/diagnostics/{command}`) et MCP (`/mcp`) publics sans jeton. | Le verrou `_diagnostic_lock` protège de l'OOM cgroup (512 MiB), pas des accès non autorisés. | Authentification mutuelle TLS (mTLS) ou API Keys JWT avec rotation, rate-limiting distribué Redis par IP. | **P0** (`fastapi-limiter`, `Authlib`, `mTLS`) |
| **4. Registre d'Audit & Arbre de Merkle** | Chaîne linéaire de hachage séquentielle (`state/ledger.jsonl`) scellée par HMAC-SHA512. | Pas de véritable structure d'Arbre de Merkle (impossibilité d'émettre des preuves d'inclusion logarithmiques $\mathcal{O}(\log N)$ sans divulguer l'historique complet). Fichier local sans WORM matériel cloud. | Implémentation d'un Arbre de Merkle binaire / Sparse Merkle Tree (SMT) avec extraction de Merkle Root d'époque, preuves cryptographiques d'inclusion (Audit Path $\mathcal{O}(\log N)$), ancrage RFC 3161 et stockage AWS S3 Object Lock (Compliance Mode). | **P1** (`pycryptodome`, Merkle Tree engine, `boto3` S3 Object Lock, RFC 3161 TSA) |
| **5. Identité & RBAC des Approbateurs** | Résolution d'approbateur statique via stub `group_of=lambda user, level: "admin"`. | Tout utilisateur Slack ayant accès au canal peut approuver n'importe quelle action critique. | Intégration SSO/OIDC/SCIM (Okta, Azure AD), séparation des devoirs (*Separation of Duties*) et quorum multi-signatures. | **P1** (`OIDC`, Slack SCIM API, Quorum M-of-N) |
| **6. Budget de Latence & Collecte Distante** | Paramètre `timeout: float` borné entre `0.5s` et `10.0s` par sous-requête HTTP individuelle. | La collecte séquentielle de multiples métriques peut dépasser 10s au total. | Collecte concurrente via `asyncio.gather` avec budget global strict (`context.deadline` / Annulation cooperative). | **P1** (`asyncio.gather`, `httpx` async timeouts) |
| **7. Validation End-to-End** | 144 tests unitaires et d'intégration tournant sur des mocks et `TestClient`. | Pas de validation de bout en bout sur un vrai cluster de production. | Suite E2E sur cluster éphémère (K3s / Kind via Testcontainers) testant l'intégralité du cycle alerte → Slack → pod restart. | **P2** (`testcontainers-python`, `kind`) |

---

## 3. Spécifications Techniques Détaillées des Chantiers

### Chantier 1 : Ingestion d'Alertes en Événements Asynchrones (Closed-Loop Trigger)
* **Problème actuel** :
  L'endpoint `agentic_ops/entrypoints/grafana_webhook.py` valide la charge utile Grafana mais ne communique pas avec `FSMOrchestrator`. L'alerte reste lettre morte dans les logs.
* **Architecture cible pour être "un vrai"** :
  1. **Bus d'Événements** : Le webhook publie immédiatement le payload validé dans un flux Redis (`XADD alerts:stream * ...`).
  2. **Worker Consommateur (`AlertIngestionWorker`)** :
     - Consomme les messages du flux Redis via un Consumer Group dédié.
     - Extrait les labels Prometheus / Grafana (`alertname`, `service`, `namespace`, `metric_value`, `threshold`).
     - Utilise le moteur `DeterministicRAGEngine` pour classifier l'alerte et lui associer son identifiant de taxonomie (ex: `Prometheus: HighMemoryUsage` $\rightarrow$ `INFRA-018: Host Out-of-Memory Kill`).
     - Instancie un épisode d'investigation : `orchestrator.step(IncidentContext(...))`.
  3. **Déduplication & Anti-Flapping** : Fenêtre glissante de 5 minutes dans Redis pour agréger les alertes identiques évitant de submerger l'orchestrateur.

---

### Chantier 2 : Moteur d'Exécution Asynchrone des Remédiations (Remediation Workers)
* **Problème actuel** :
  Lorsque l'opérateur humain clique sur "Approuver" dans Slack, la fonction `_resume_from_claim` se contente d'émettre un log. L'action (`restart_pod`, `rollback_prod`) n'est jamais transmise à l'infrastructure cible.
* **Architecture cible pour être "un vrai"** :
  1. **File de Tâches d'Exécution** : La validation de la signature Slack et du claim SQLite pousse une commande dans une file de tâches sécurisée (ex: Celery ou `arq`).
  2. **Drivers d'Exécution Découplés (`agentic_ops/executors/`)** :
     - `KubernetesExecutor` : Utilise `kubernetes-asyncio` pour déclencher un redémarrage ordonné de Pod (`apps_v1.patch_namespaced_deployment`) avec compte de service RBAC à privilèges minimaux (*Least Privilege*).
     - `MLflowExecutor` : Appelle le Model Registry MLflow pour rétrograder le tag de modèle `alias="champion"` vers la version stable précédente (`alias="fallback"`).
     - `GitHubExecutor` : Ouvre une issue ou une PR de rollback avec le rapport d'incident complet.
  3. **Validation Post-Action (Canary & Rollback Automatique)** :
     - Après exécution, l'orchestrateur surveille les sondes de santé (`/healthz`, taux d'erreur HTTP 5xx) pendant 180 secondes.
     - Si la métrique ne se rétablit pas, déclenchement immédiat d'une alerte d'échec critique et réouverture du ticket Slack.

---

### Chantier 3 : Authentification Zéro-Trust, Rate-Limiting & Isolation Sandbox
* **Problème actuel** :
  Le point d'accès `/api/diagnostics/{command}` n'exige aucun secret d'authentification. Le mutex `_diagnostic_lock` prévient uniquement les plantages par manque de mémoire (512 MiB), mais n'offre aucune sécurité de périmètre.
* **Architecture cible pour être "un vrai"** :
  1. **Contrôle d'Accès Périmétrique** :
     - Protection des routes d'administration et de diagnostic par authentification mutuelle TLS (mTLS) pour les communications inter-services ou tokens Bearer JWT cryptographiquement signés.
  2. **Rate-Limiting Distribué par IP** :
     - Intégration de `fastapi-limiter` adossé au Redis local : maximum 5 requêtes par minute sur `/api/diagnostics/` et 20 requêtes par minute sur `/api/chat`.
  3. **Micro-Isolation Sandbox (gVisor / Firecracker)** :
     - L'exécution de `pytest` ou de scripts de diagnostic ne doit pas partager le même espace mémoire ou les mêmes cgroups que le serveur API principal.
     - Déport de l'exécution des diagnostics dans des conteneurs éphémères jetables via Docker-in-Docker isolé ou workers Fargate / Cloud Run dédiés.

---

### Chantier 4 : Vrai Registre WORM Matériel Cloud & Architecture en Arbre de Merkle (Merkle Tree Cryptographique)
* **Problème actuel & Limites de la Chaîne Linéaire** :
  1. **Complexité de Vérification Linéaire $\mathcal{O}(N)$** : Actuellement, le Trust Ledger est une chaîne séquentielle de hachage ($H_i = \text{Hash}(H_{i-1} + \text{canonical}(P_i))$). Pour prouver à un auditeur qu'un incident $E_k$ n'a pas été altéré dans un historique de $N$ épisodes, il faut obligatoirement recalculer et rejouer l'intégralité des $N$ hachages depuis le bloc genesis.
  2. **Absence de Divulgation Sélective (*No Selective Disclosure*)** : Pour vérifier la chaîne, l'auditeur externe doit avoir accès à l'intégralité des épisodes précédents. Cela interdit de fournir une preuve à un tiers sur un incident précis sans lui exposer les métadonnées et données confidentielles des autres incidents.
  3. **Absence de Racine Compacte Unique** : Impossible de condenser l'état de 10 000 incidents en une empreinte immuable unique de 32 octets pouvant être ancrée publiquement.
  4. **Stockage Local Vulnérable** : Le fichier `state/ledger.jsonl` réside sur le disque de l'hôte sans verrouillage matériel WORM.

* **Architecture Cible pour être "un vrai"** :
  1. **Structure de Données en Arbre de Merkle Binaire (`MerkleTreeEngine`)** :
     - **Feuilles de l'Arbre** : Chaque épisode validé forme une feuille : $L_i = \text{SHA-256}(\text{canonical\_json}(E_i))$.
     - **Arborescence Cryptographique** : Les feuilles sont combinées deux à deux jusqu'au sommet :
       $$\text{Node}_{\text{parent}} = \text{SHA-256}(\text{Node}_{\text{left}} \mathbin{\Vert} \text{Node}_{\text{right}})$$
     - **Merkle Root d'Époque ($\text{Root}_{\text{epoch}}$)** : À chaque clôture d'époque (ex: toutes les 100 décisions ou chaque heure), une racine unique de 32 octets est consolidée, représentant l'intégrité absolue de l'ensemble du lot.
  2. **Preuves d'Inclusion Logarithmiques en $\mathcal{O}(\log N)$ (*Audit Path / Merkle Proof*)** :
     - Pour prouver à un régulateur (ex: conformité EU AI Act) qu'un épisode critique $E_k$ a été scellé sans lui divulguer le contenu des $N-1$ autres épisodes, le système génère un certificat d'audit compact contenant uniquement l'épisode $E_k$ et sa branche de hachages frères :
       $$\text{Proof}(E_k) = \{H_{\text{sibling}, 1}, H_{\text{sibling}, 2}, \dots, H_{\text{sibling}, \lceil \log_2 N \rceil}\}$$
     - L'auditeur recalcule la racine en seulement $\lceil \log_2 N \rceil$ opérations de hachage (ex: 14 opérations pour 10 000 incidents au lieu de 10 000) et compare le résultat à la racine certifiée.
  3. **Ancrage Externe & Horodatage Légal (RFC 3161 TSA & Transparency Logs)** :
     - Chaque racine $\text{Root}_{\text{epoch}}$ est soumise à une Autorité d'Horodatage certifiée (Timestamping Authority selon la norme RFC 3161) fournissant un jeton cryptographique horodaté infalsifiable prouvant que l'état existait à cette seconde précise.
     - Publication optionnelle de la racine dans un registre de transparence public immuable (ex: Rekor / Sigstore).
  4. **Stockage Cloud Immuable Certifié (WORM Object Lock)** :
     - Déport des épisodes scellés et de leurs arbres de Merkle vers un bucket **AWS S3 avec Object Lock activé en Compliance Mode** (durée de rétention légale non modifiable même par le compte root AWS) ou **Google Cloud Storage Bucket Lock**.
     - Signature asymétrique de la Merkle Root via **AWS KMS / GCP Cloud KMS avec paire de clés Ed25519 ou ECDSA P-256 stockée dans un HSM certifié FIPS 140-2 Level 3**.


---

### Chantier 5 : Identité des Approbateurs, RBAC & Quorum Multi-Signatures
* **Problème actuel** :
  Dans [`main.py`](file:///Users/nolll/Documents/car_acc/agentic-ops-core/agentic_ops/cli/main.py), la vérification du groupe d'approbateur est un stub `approvers=SimpleNamespace(group_of=lambda user, level: "admin")`. De plus, une seule signature Slack suffit pour valider une action critique.
* **Architecture cible pour être "un vrai"** :
  1. **Mapping d'Identité Entreprise (SSO / OIDC)** :
     - Association stricte entre l'ID d'utilisateur Slack (`U12345`) et l'annuaire d'entreprise (Okta / Azure Active Directory / Google Workspace).
     - Vérification dynamique des groupes et permissions de l'utilisateur au moment exact du clic via l'API SCIM ou le jeton OIDC de l'opérateur.
  2. **Séparation des Devoirs (*Separation of Duties*)** :
     - L'ingénieur ayant déployé ou commité la dernière version d'un modèle ne peut pas approuver le rollback ou le redémarrage de son propre service.
  3. **Quorum Multi-Signatures (*M-of-N Approval*)** :
     - Pour les actions d'impact majeur (`Level L3` : ex. `rollback_prod` ou modification de schéma), exiger l'approbation conjointe de 2 opérateurs distincts (ex: 1 Ingénieur SRE + 1 Responsable Métier MLOps) avant libération du verrou dans la FSM.

---

### Chantier 6 : Budget de Latence Global & Collecte Distante Asynchrone
* **Problème actuel** :
  Dans `get_cac_snapshot` ([`main.py`](file:///Users/nolll/Documents/car_acc/agentic-ops-core/agentic_ops/cli/main.py)), le paramètre `timeout` est appliqué individuellement à chaque sous-requête séquentielle. En cas d'indisponibilité de plusieurs sondes distantes, la requête globale peut durer jusqu'à 30 secondes.
* **Architecture cible pour être "un vrai"** :
  1. **Parallélisation via `asyncio.gather`** :
     - Lancer simultanément l'ensemble des requêtes de collecte métriques, santé et contrats.
  2. **Budget de Latence Global Strict (`context.deadline`)** :
     - Encapsuler la collecte complète dans un bloc `asyncio.timeout(overall_timeout)` borné à 10.0 secondes max pour l'intégralité du traitement.
     - Annulation coopérative : si le délai global expire, retourner immédiatement les données partielles collectées avec un indicateur d'état dégradé (`partial_telemetry=True`) plutôt que de faire attendre le client.

---

### Chantier 7 : Validation End-to-End sur Cluster Éphémère (CI/CD Rigoureuse)
* **Problème actuel** :
  La suite de tests actuelle (**144 tests**) est constituée de tests unitaires et d'intégration avec mocks. Elle valide la logique interne de décision mais ne teste pas l'interaction avec des dépendances réelles.
* **Architecture cible pour être "un vrai"** :
  1. **Cluster Éphémère dans GitHub Actions** :
     - Déploiement d'un mini-cluster Kubernetes éphémère (Kind ou K3s) lors des tests de nuit ou des runs de pré-release.
     - Déploiement d'un vrai pod Prometheus et Grafana configuré pour émettre un webhook réel.
  2. **Scénario d'Intégration Bout en Bout (E2E)** :
     - Injection de dérive dans les données $\rightarrow$ Détection Prometheus $\rightarrow$ Webhook Grafana $\rightarrow$ FSM Agentic-Ops $\rightarrow$ Veto PolicyEngine $\rightarrow$ Émission de proposition Slack $\rightarrow$ Simulation de clic avec signature HMAC valide $\rightarrow$ Action réelle exécutée sur le Pod Kind $\rightarrow$ Vérification du rétablissement $\rightarrow$ Vérification de la preuve scellée.

---

## 4. Guide Stratégique pour la Soutenance & Entretien Technique

Face à un jury ou un auditeur expérimenté, voici la posture recommandée pour présenter ce travail :

```
                        ┌──────────────────────────────────────────────┐
                        │        POSTURE D'INGÉNIERIE MATURE           │
                        ├──────────────────────────────────────────────┤
                        │ 1. Revendiquer le Plan de Contrôle (Fait)    │
                        │ 2. Justifier la Simulation (Safety Design)   │
                        │ 3. Présenter la Roadmap des Gaps (Next Steps)│
                        └──────────────────────────────────────────────┘
```

### Argumentaire Recommandé :
1. **La Frontière Assumée entre Plan de Contrôle et Plan d'Exécution** :
   > *"En tant qu'ingénieur, mon premier objectif était de concevoir un plan de contrôle inviolable : des contrats déclaratifs Pandera, un moteur de règles déterministes à veto immédiat, une FSM à 5 états et un registre d'audit cryptographique. Donner les droits d'écriture et de suppression à une IA sur une production réelle sans ce plan de contrôle préalable aurait été une faute grave d'architecture."*

2. **Le Statut du Mode Simulation** :
   > *"Le fait que `SIMULATION_MODE = True` soit actif par défaut n'est pas un manque, c'est un garde-fou délibéré (*Safety Safeguard by Design*). Dans un contexte critique, un agent cognitif ne doit jamais avoir le pouvoir d'altérer la production en aveugle. Notre architecture formalise le consensus humain et la politique de sécurité avant toute chose."*

3. **La Clarté sur les Prochaines Étapes (*Next Steps*)** :
   > *"Nous avons consigné l'intégralité des écarts identifiés dans notre document `PRODUCTION_READINESS_ROADMAP_AND_GAPS.md`. Pour passer d'un prototype de contrôle avancé à une plateforme d'entreprise, nous avons spécifié les 7 chantiers nécessaires : le découplage événementiel via Redis Streams, les workers d'exécution asynchrones, le stockage WORM sur AWS S3 Object Lock et le quorum multi-signatures d'approbateurs."*

---

*Document d'ingénierie compilé et intégré à la base de connaissances du projet `Agentic-Ops`.*
