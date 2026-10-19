# Roadmap de Durcissement Production & Levée des Écarts (Enterprise MLOps Readiness)

> **Document de Référence d'Ingénierie & d'Honnêteté Radicale**  
> **Auteur** : Équipe MLOps / SRE  
> **Statut** : Document d'Architecture Cible & Spécifications des Prochaines Étapes (*Next Steps*)  
> **Périmètre** : Transition du prototype de gouvernance solo vers une plateforme industrielle de classe entreprise (*"Pour être un vrai"*).

> **État du code vérifié** : consulter [`INDUSTRIAL_IMPLEMENTATION_STATUS.md`](./INDUSTRIAL_IMPLEMENTATION_STATUS.md) pour séparer les contrôles implémentés et testés des composants externes, GameDays et profils cloud non qualifiés. Le mapping détaillé repo→production, les contrats de configuration et les gates de promotion sont dans [`INDUSTRIAL_PRODUCTION_BLUEPRINT.md`](./INDUSTRIAL_PRODUCTION_BLUEPRINT.md). Pour la configuration Entra et la qualification préproduction restante, suivre [`ENTRA_PREPRODUCTION_QUALIFICATION.md`](./ENTRA_PREPRODUCTION_QUALIFICATION.md).

---

## 1. Contexte & Démarche d'Ingénierie

À la suite de la contre-expertise chirurgicale du commit `06f6bb6` (validé par `144 passed, 3 skipped, 1 xfail`), ce document formalise avec une **lucidité technique absolue** l'ensemble des écarts existants entre notre plan de contrôle actuel et les exigences d'une infrastructure MLOps de mission critique en entreprise (normes ISO 42001, EU AI Act, SOC 2 Type II).

Dans un projet mené en solo, implémenter un plan de contrôle complet (contrats Pandera, veto déterministe `PolicyEngine`, FSM à 5 états, indexation in-memory de 435 pannes, signatures HMAC Slack et chaînage cryptographique) représente déjà un niveau d'architecture avancé. Toutefois, pour qu'Agentic-Ops devienne un **"vrai" orchestrateur autonome de production**, plusieurs verrous techniques fondamentaux doivent être levés.

Ce document constitue la **feuille de route d'industrialisation (Roadmap Next Steps)**.

---

## 2. Matrice Synthétique des Écarts & Spécifications Cibles

| Dimension Architecturale | État Actuel (Prototype Avancé / Solo) | Écart Identifié par l'Audit | Spécification Cible (*"Pour être un vrai"*) | Priorité & Stack Cible |
| :--- | :--- | :--- | :--- | :--- |
| **1. Ingestion d'Alertes** | `POST /webhook/alerts` authentifie et persiste les alertes en SQLite WAL avant `202`; le worker supervisé utilise un mapping versionné, l'inventaire local exact et crée un épisode `investigate` simulé pour les alertes reconnues. Le code inclut des snapshots SQLite vérifiés et un micro-benchmark local. | Chart PVC+SQLite mono-réplica; la sauvegarde multi-base/evidence depuis l'instance cible, la restauration depuis le support retenu, le débit cible et la perte d'hôte ne sont pas qualifiés. | Exercer le cycle de bout en bout, backup/restore et mesure sur la machine retenue; pour le multi-nœud, remplacer SQLite par un adaptateur transactionnel partagé qualifié. | **P0** (chemin simulé et outils locaux livrés; qualification opérationnelle restante) |
| **2. Exécution des Actions** | Simulation par défaut; le worker revalide le claim et les rôles, simule le résultat, puis prolonge en append-only l'épisode suspendu d'origine (`EXECUTING → RESOLVED`); une reprise après append/avant ack ne simule pas une seconde fois. | Aucune action n'est qualifiée pour mutation réelle; vérification post-action et rollback/kill-switch indépendant restent à construire et déployer. Le refus n'est pas encore réconcilié dans le ledger. | Qualifier l'idempotence/reprise du profil déployé, puis contrats par action, vérification post-action et compensation, puis exercices canary. | **P0** (aucune action réelle activée) |
| **3. Authentification & Sécurité d'Accès** | Middleware API-key fail-closed seulement hors mode Entra; quand Entra est configuré, jeton vérifié (signature RS256/JWKS, tenant, issuer, audience, durée de vie et app-role) requis et les API keys sont ignorées; webhook Grafana avec secret dédié. | Le code OIDC existe, mais aucun tenant Entra n'est configuré ni qualifié; pas de mTLS, rate limit distribué ni test d'intrusion de plateforme. | Enregistrer l'application dans Entra, assigner le rôle d'application, exercer rotation JWKS, révocation et comportement en panne, compléter mTLS/rate limit par profil. | **P0** (code implémenté; configuration et qualification Entra restantes) |
| **4. Registre d'Audit & Arbre de Merkle** | Structure Merkle Tree binaire RFC 6962 implémentée en code ([`merkle.py`](file:///Users/nolll/Documents/car_acc/agentic-ops-core/agentic_ops/core/merkle.py)), preuves d'inclusion $\mathcal{O}(\log N)$, CLI (`merkle-root`, `merkle-proof`). | Les preuves d'inclusion relatives à une racine calculée fonctionnent, mais l'authenticité de la racine n'est pas ancrée indépendamment (RFC 3161 TSA, log de transparence anti split-view) et le stockage WORM cloud physique (S3 Object Lock) reste à câbler. | Ancrage temporel (RFC 3161 TSA), registre de transparence public anti split-view avec preuves de cohérence $\mathcal{O}(\log N)$ (Rekor / Trillian) et stockage persistant sur bucket AWS S3 Object Lock en Compliance Mode avec signature Cloud KMS HSM FIPS 140-2 L3. | **P1 (Code fait / Infra externe à brancher)** (`boto3` S3 Object Lock, RFC 3161 TSA, Sigstore/Rekor) |
| **5. Identité & RBAC des Approbateurs** | SCIM 2.0 optionnel reçoit Users/Groups Entra, mappe `externalId` au Slack member ID et revalide l'appartenance avant la simulation; en solo, le mapping statique reste disponible. La demande d'approbation est maintenant liée à l'épisode persisté et la continuation simulée est append-only. | Aucun tenant, enterprise app ou flux de provisionnement Entra n'est déployé/qualifié; la notification Slack, le profil de demandeur/quorum et la clôture du refus restent à qualifier ou compléter. | Configurer l'app SCIM Entra et le mappage des groupes, tester provisioning/désactivation/suppression, latence de révocation et reprise/restauration sur le profil déployé. | **P1** (chemin logiciel simulé livré; déploiement et qualification Entra restants) |
| **6. Budget de Latence & Collecte Distante** | Paramètre `timeout: float` borné entre `0.5s` et `10.0s` par sous-requête HTTP individuelle. | La collecte séquentielle de multiples métriques peut dépasser 10s au total. | Collecte concurrente via `asyncio.gather` avec budget global strict (`context.deadline` / Annulation cooperative). | **P1** (`asyncio.gather`, `httpx` async timeouts) |
| **7. Validation End-to-End** | CI locale et scénarios sur mocks/TestClient; crash worker, reprise de bail, allowlist inventory, snapshots SQLite et micro-benchmark local ont des tests ciblés. | Aucun GameDay ni cycle complet alerte → identité → approbation → action vérifié sur cluster cible; pas de mesure issue de la machine de déploiement. | Suite E2E sur profil préproduction qualifié, y compris reprise après panne et exercice de restauration. | **P2** (cible et opérations de qualification à fournir) |

---

## 3. Spécifications Techniques Détaillées des Chantiers

### Chantier 1 : Ingestion d'Alertes en Événements Asynchrones (Closed-Loop Trigger)
* **État de l'implémentation** :
  `agentic_ops/entrypoints/grafana_webhook.py` valide et persiste les alertes; le sidecar Helm `agentic-alert-worker` consomme l'outbox et applique `agentic_ops/governance/alert_classification.yaml`. Pour les alertes mappées, il appelle l'orchestrateur avec un diagnostic déterministe borné et l'action non mutante `investigate`, puis persiste le lien vers l'épisode. Une alerte non reconnue passe en `REVIEW_REQUIRED`; aucune action de remédiation n'est déclenchée. Le chart partagé PVC/SQLite est configuré pour un seul pod et ne constitue pas un profil HA.
* **Architecture cible pour être "un vrai"** :
  1. **Transport durable** : Le profil local utilise l'outbox SQLite existante. Un profil multi-instance devra fournir un adaptateur transactionnel partagé qualifié; le passage à Redis Streams n'est pas une garantie en soi et devra préserver l'acceptation durable et l'idempotence.
  2. **Worker Consommateur (`AlertIngestionWorker`)** :
     - Consomme l'outbox avec leases et retries; la commande `agentic-alert-worker` peut tourner en continu ou en mode `--once`.
     - Résout uniquement les noms `alertname` explicitement présents dans le mapping versionné et vérifie les `risk_id` contre le registre des risques.
     - Les alertes inconnues ou sans nom passent en `REVIEW_REQUIRED`; aucune inférence LLM ne les promeut implicitement.
     - L'investigation orchestrée et la persistance d'épisode sont maintenant câblées; le worker livré ne lance pas de remédiation.
  3. **Déduplication & Anti-Flapping** : L'outbox SQLite actuelle déduplique pendant 5 minutes dans son propre état transactionnel. En multi-instance, conserver cette garantie avec le stockage partagé qualifié plutôt que d'ajouter un cache Redis indépendant non atomique.

---

### Chantier 2 : Moteur d'Exécution Asynchrone des Remédiations (Remediation Workers)
* **État actuel** :
  Le quorum validé crée atomiquement un claim et un message durable dans l'outbox. Le sidecar optionnel `agentic-approval-worker` relit ces claims, revérifie les rôles depuis le mapping statique ou l'annuaire SCIM Entra (si activé), et passe par l'exécuteur en simulation seulement. Un claim peut ainsi être repris après redémarrage et le statut `SIMULATED` est persisté sans mutation réelle. Ce worker ne reprend pas encore l'épisode suspendu de l'orchestrateur; le provisionnement SCIM et les rôles d'application OIDC restent à configurer et qualifier dans un tenant Entra.
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
  3. **Ancrage Externe, Horodatage Légal & Détection du Split-View (RFC 3161 TSA & Transparency Logs)** :
     - **Horodatage d'existence certifié (RFC 3161 TSA)** : Chaque racine $\text{Root}_{\text{epoch}}$ est soumise à une Autorité d'Horodatage certifiée (Timestamping Authority selon la norme RFC 3161) produisant un jeton cryptographique horodaté (`.tsr`) prouvant de manière irréfutable que la racine $R$ existait à un instant $t_0$ donné. *Attention : le jeton TSA certifie l'existence temporelle mais ne protège pas contre les attaques par partitionnement de vue (split-view), un opérateur malveillant pouvant faire horodater deux racines divergentes.*
     - **Détection & Atténuation du Split-View via Registre de Transparence Public (Sigstore Rekor / Certificate Transparency)** : Publication de la racine dans un journal d'annexion public vérifiable équipé de preuves de cohérence d'arbre en $\mathcal{O}(\log N)$ (*Tree Consistency Proofs*) entre les tailles $N_1$ et $N_2$ et audité par un réseau de témoins indépendants (*witness gossiping*). Ce mécanisme permet de détecter, dissuader et prouver cryptographiquement la divergence si un opérateur tente de servir deux réalités distinctes à deux régulateurs différents.
     - **Non-Répudiation de l'Identité Signataire (Cloud KMS HSM)** : Signature asymétrique de la Merkle Root via une clé Ed25519 ou ECDSA P-256 stockée dans un HSM certifié FIPS 140-2 Level 3 (AWS KMS / GCP Cloud KMS), liant la racine à l'identité d'entreprise de l'exploitant.
  4. **Stockage Cloud Immuable Certifié (WORM Object Lock)** :
     - Déport des épisodes scellés et de leurs arbres de Merkle vers un bucket **AWS S3 avec Object Lock activé en Compliance Mode** (durée de rétention légale non modifiable même par le compte root AWS) ou **Google Cloud Storage Bucket Lock**.
     - Signature asymétrique de la Merkle Root via **AWS KMS / GCP Cloud KMS avec paire de clés Ed25519 ou ECDSA P-256 stockée dans un HSM certifié FIPS 140-2 Level 3**.

> [!NOTE]
> **État d'Implémentation au 19/10/2026** :
> - **Code & Algorithmes (100% Câblé & Testé)** : Le moteur d'Arbre de Merkle binaire strictement conforme RFC 6962 Section 2.1 (scission récursive à $k = 2^{\lfloor \log_2(n-1) \rfloor}$ sans duplication de nœud impair et traversée par arithmétique d'indices bornés sans copies de tranches) ([`agentic_ops/core/merkle.py`](file:///Users/nolll/Documents/car_acc/agentic-ops-core/agentic_ops/core/merkle.py)), son intégration dans `EvidenceStore` ([`agentic_ops/core/evidence.py`](file:///Users/nolll/Documents/car_acc/agentic-ops-core/agentic_ops/core/evidence.py)) avec liaison cryptographique obligatoire de payload (*Mandatory Cryptographic Payload Binding* rejetant strictement toute preuve sans contenu), la distinction formelle de complexité ($\mathcal{O}(N)$ construction/scan vs $\mathcal{O}(\log N)$ vérification/taille de preuve), l'extraction des preuves d'inclusion $\mathcal{O}(\log N)$ et les commandes CLI d'audit (`merkle-root`, `merkle-proof`) sont pleinement opérationnels et validés par **15 tests unitaires et contradictoires dédiés** ([`tests/adversarial/test_merkle_tree.py`](file:///Users/nolll/Documents/car_acc/agentic-ops-core/tests/adversarial/test_merkle_tree.py)). Suite complète : **183 tests passed, 3 skipped, 0 xfailed**.
> - **Restant pour être "un vrai" (Infrastructure Cloud Externe)** : Ancrage externe RFC 3161 TSA (existence temporelle), registre de transparence Sigstore Rekor (preuves de cohérence d'arbre anti split-view), bucket S3 physique avec Object Lock matériel en Compliance Mode, et clés asymétriques Ed25519 managées dans un HSM Cloud KMS FIPS 140-2 L3 avec persistance cross-restart.



---

### Chantier 5 : Identité des Approbateurs, RBAC & Quorum Multi-Signatures
* **Problème résolu en code local & statut actuel** :
  - La vérification des approbateurs n'est plus un stub : [`agentic_ops/core/approvals.py`](file:///Users/nolll/Documents/car_acc/agentic-ops-core/agentic_ops/core/approvals.py) impose un demandeur obligatoire (`requester_id`), fige la proposition par son hachage SHA-256 (`proposal_hash`), interdit formellement l'auto-approbation (`requester == approver` $\rightarrow$ `SELF_APPROVAL_FORBIDDEN`), applique les rôles Slack via `SLACK_APPROVERS_JSON`, exige un quorum multi-groupes et enregistre atomiquement la décision dans une file durable `execution-outbox`.
* **Architecture cible pour être "un vrai" (Raccordement Entreprise)** :
  1. **Mapping d'Identité Entreprise (SSO / OIDC)** :
     - Association stricte entre l'ID d'utilisateur Slack (`U12345`) et l'annuaire d'entreprise (Okta / Azure Active Directory / Google Workspace).
     - Vérification dynamique des groupes et permissions de l'utilisateur au moment exact du clic via l'API SCIM ou le jeton OIDC de l'opérateur.
  2. **Séparation des Devoirs (*Separation of Duties*) en Production** :
     - Raccordement au registre Git/CI pour certifier que l'ingénieur ayant déployé ou commité la dernière version d'un modèle ne peut pas approuver le rollback ou le redémarrage de son propre service.
  3. **Quorum Multi-Signatures (*M-of-N Approval*) Exercé** :
     - Pour les actions d'impact majeur (`Level L3` : ex. `rollback_prod` ou modification de schéma), exiger l'approbation conjointe de 2 opérateurs distincts (ex: 1 Ingénieur SRE + 1 Responsable Métier MLOps) avec exercice réel en conditions GameDay.

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
  La suite de tests actuelle (**183 tests validés, 3 skipped, 0 xfailed**) est constituée de tests unitaires et d'intégration avec mocks et composants SQLite WAL locaux. Elle valide la logique interne de décision mais ne teste pas l'interaction avec des dépendances réelles en environnement distribué.
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
