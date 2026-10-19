# Blueprint de trajectoire vers une production industrielle

**Statut :** spécification de travail, pas une qualification ni un engagement de
service. Elle décrit le chemin entre les contrats présents dans ce dépôt et
les valeurs, systèmes, propriétaires et preuves qu'une exploitation réelle
devra fournir. Le profil actuel reste mono-réplica, SQLite, inventaire local
maintenu manuellement, actions en simulation et qualification personnelle.

Lire avec :

- [`INDUSTRIAL_IMPLEMENTATION_STATUS.md`](./INDUSTRIAL_IMPLEMENTATION_STATUS.md)
  pour l'état du code et des tests;
- [`SELF_HOSTED_PRODUCTION_PATH.md`](./SELF_HOSTED_PRODUCTION_PATH.md) pour
  l'exploitation solo réalisable sans tenant Entra;
- [`ENTRA_PREPRODUCTION_QUALIFICATION.md`](./ENTRA_PREPRODUCTION_QUALIFICATION.md)
  pour la qualification Entra et Kubernetes déjà envisagée.

## 1. Ce que « prêt pour la production » doit vouloir dire

Il n'existe pas de case « production » universelle. Une qualification doit
nommer au minimum la version de l'application, le profil d'infrastructure,
les systèmes cibles, la charge, les données traitées, les actions permises,
les opérateurs responsables, les objectifs de service, les risques acceptés
et les preuves d'essai. Une validation sur un profil ne qualifie pas un autre.

Pour cette application, séparer deux niveaux :

1. **Profil de production personnelle borné** : une personne, un hôte ou un
   nœud, SQLite mono-réplica, inventaire local, investigations en lecture seule,
   simulations seulement, sauvegarde testée hors de la machine et procédure
   de restauration comprise. Cela peut être préparé seul, sans Entra.
2. **Profil industriel d'équipe** : identité et séparation des tâches
   indépendantes, déploiement redondant, stockage/queue partagés qualifiés,
   sauvegarde hors site, observabilité avec astreinte, maîtrise de la chaîne
   logicielle, tests de panne sur la cible, action par action autorisée,
   rollback et propriétaires opérationnels nommés. Cela implique des systèmes
   et opérateurs réels, et n'est pas livré par ce dépôt seul.

Ne pas annoncer haute disponibilité, RPO/RTO, SLO, conformité réglementaire,
WORM physique ou remédiation autonome tant que les contrôles correspondants
n'ont pas été exercés sur la cible et leurs résultats conservés.

## 2. Maillons de la chaîne opérationnelle de bout en bout

### 2.1 Détection, transport et admission d'une alerte

**Chaîne visée :** source de métriques/logs → règle d'alerte → webhook
authentifié → validation de taille/schéma → commit durable → accusé HTTP 202 →
tracking ID → endpoint de statut.

| Élément | Contrat dans le dépôt | Valeur ou mapping à fournir dans la vraie cible | Preuve avant promotion |
|---|---|---|---|
| Source/règle | L'API accepte des événements conformes au webhook Grafana. | URL du service exposée en HTTPS, nom stable de l'alerte, labels, annotations, `startsAt`, statut et fréquence de répétition. | Rejouer une alerte réelle expurgée, invalide, trop grande, répétée et résolue; confirmer le code HTTP et le statut. |
| Identité du webhook | Secret `GRAFANA_WEBHOOK_SECRET`; l'API accepte `X-Grafana-Token` ou la forme documentée par le handler. | Secret dédié au webhook, créé hors Git, injecté via Kubernetes Secret; procédure de rotation avec clé courante/précédente. | Test secret absent/erroné/courant/précédent; vérifier logs sans valeur secrète. |
| Réseau | Route webhook de l'API et limites de corps existantes. | DNS, certificat TLS, ingress/gateway, règles d'entrée, origine autorisée et plan de rotation certificat. | Test de connectivité TLS depuis Grafana et de refus depuis les réseaux non autorisés. |
| Durabilité de l'admission | `AlertOutbox` persiste avant l'accusé, SQLite WAL/FULL, fingerprint sémantique et tracking ID. | Pour le profil actuel : PVC stable, `replicaCount: 1`, `persistence.enabled: true`. Pour plusieurs instances : adaptateur transactionnel partagé à concevoir/qualifier. | Arrêter l'API après commit et avant réponse; rejouer le webhook; confirmer qu'aucune alerte n'est perdue et que les doublons ont le même tracking ID. |
| Sémantique de livraison | Déduplication temporaire, leases, retry borné, terminal `DEAD`. | Décider si répétitions Grafana et événements `resolved` doivent fusionner ou rester distincts; définir la rétention et l'escalade `DEAD`. | Essais sur le vrai rythme de répétition, panne prolongée, événement résolu et après expiration de fenêtre. |
| Statut | Endpoint de statut protégé par l'authentification administrative. | Rendre le tracking ID accessible au système d'exploitation sans exposer les payloads d'alerte à des utilisateurs non autorisés. | Vérifier statut pour `RECEIVED`, `PROCESSING`, `RETRY`, `COMPLETED`, `DEAD`, identifiant inconnu et utilisateur non authentifié. |

### 2.2 Classification, inventaire et décision de politique

**Chaîne visée :** nom d'alerte autorisé → `risk_id` connu → cible stable →
inventaire frais → calcul d'impact → règles et quotas → décision liée à la
version de politique et d'inventaire.

| Clé du repo / contrat | Sens | Mapping réel à fournir | Garde / test obligatoire |
|---|---|---|---|
| `agentic_ops/governance/alert_classification.yaml` → `mappings.<alertname>.risk_id` | Associe un nom d'alerte exact à un risque. | Chaque `alertname` de Grafana doit correspondre exactement à une entrée et son `risk_id` doit exister dans `risk_register.yaml`. | Inconnu, mauvais format, clé dupliquée ou risque supprimé → `REVIEW_REQUIRED`, sans inférence implicite. |
| Label d'alerte `service`, sinon `job` | Devient la cible évaluée par l'inventaire dans le worker. | Choisir un label canonique; nommer les cibles d'inventaire exactement selon la valeur produite par le système observé. | Vérifier les valeurs réelles, casse, alias, cardinalité et stabilité lors d'un renommage. Un label absent ne doit pas autoriser une cible de repli. |
| `AGENTIC_OPS_INVENTORY_PATH` | Chemin vers la source YAML locale. Sans cette variable, l'inventaire est indisponible et le verdict est refusé. | ConfigMap Helm `inventory.enabled`, générée par `inventory.generatedAt`, `inventory.maxAgeSeconds`, `inventory.targets.<id>.replicas` et `criticality`. Le même contenu est monté en lecture seule dans l'API et le worker. | Cible inconnue, fichier absent/périmé/invalide → `DENY`/`INV-001` ou démarrage refusé. Tester le rollout sur chaque changement; ne pas utiliser des valeurs estimées comme inventaire réel. |
| `replicas`, `criticality` | Paramètres du calcul de blast radius dans le moteur. | Nombre et criticité obtenus depuis une source de vérité autorisée; identifier le propriétaire qui maintient les valeurs et la fréquence de rafraîchissement. | Comparer avec l'orchestrateur réel; démontrer que l'agent/API appelant ne peut pas fournir des nombres plus favorables. |
| `autonomy_policy.yaml`, `action_catalog.yaml`, `risk_register.yaml` | Niveaux, approbations, classes, formats, quotas et interdictions. | Identifier le propriétaire d'approbation des règles, le processus de revue et les exceptions; versionner les changements avec l'application. | Tests de contrat sur les cas autorisés/interdits, mise à jour sans désalignement, évaluation de drift entre versions. |
| `POLICY_QUOTA_DB_PATH` | État durable des réservations de quota SQLite. | Chemin sur le PVC de l'instance unique; en HA, un adaptateur transactionnel partagé et une sémantique de réservation atomique. | Concurrence au-dessus du quota, crash pendant réservation, redémarrage et fenêtre glissante. |
| `policy_version`, `inventory_version` | Version de politique et hash de l'inventaire inscrits dans le verdict/épisode. | Inclure ces identifiants dans la recherche incident, le rapport d'audit et la promotion. | À partir d'un épisode, retrouver les fichiers exacts et les revues ayant produit la décision. |

L'inventaire local ajouté dans la version source est une **allowlist
opérationnelle**, mais pas une découverte autoritative. Tant que son
générateur/synchroniseur et sa responsabilité ne sont pas définis, il ne prouve
pas que ses replicas et sa criticité reflètent l'état de la plateforme.

### 2.3 Authentification, identité et autorisation humaine

**Chaîne visée :** appelant identifié → rôle vérifié → moindre privilège →
approbateur distinct → révocation appliquée → preuve d'identité conservée.

| Clé / composant | Usage | Valeur manquante côté exploitant | Critère de qualification |
|---|---|---|---|
| `ADMIN_API_KEY`, optionnel `ADMIN_API_KEY_PREVIOUS` | Authentification locale API quand Entra n'est pas configuré. | Secret aléatoire long, Secret Kubernetes hors dépôt, utilisateur/automation autorisés, calendrier de rotation et procédure de révocation. | Clé absente/invalide rejetée; ancienne et nouvelle coexistent pendant une fenêtre contrôlée; ancienne supprimée ensuite. |
| `ENTRA_TENANT_ID`, `ENTRA_API_AUDIENCE`, `ENTRA_REQUIRED_ROLE` | OIDC/JWT Entra : tenant, audience, rôle applicatif. | Tenant, app registration, URI d'audience, app role, affectations utilisateurs/groupes, politiques CA et propriétaires. Aucun n'est déductible du repo. | Jeton valide et négatifs (mauvais tenant/audience, rôle absent, expiry), rotation JWKS, panne Entra et révocation. |
| `SCIM_ENABLED`, `SCIM_DB_PATH`, `SCIM_BEARER_TOKEN` | Provisionnement local des utilisateurs/groupes, seulement si activé. | Application d'entreprise, URL HTTPS `/scim/v2`, bearer secret, scope, mapping attributs, planning de synchronisation, propriétaire des erreurs. | Create/update/deactivate/delete, groupe et membership add/remove, latence mesurée de retrait d'accès. |
| SCIM `externalId` ↔ ID Slack; groupes `SRE`, `SRE_LEAD`, `DATA_STEWARD`, `SECOPS` | Lien de l'utilisateur et rôle d'approbation. | Source autoritative de l'identifiant, mapping de groupe exact, noms de groupe dans le tenant, choix de groupe obligatoire par action. | Compte inconnu/inactif/groupe inattendu refusé; test de déprovisionnement jusqu'au worker. |
| `SLACK_APPROVERS_JSON` ou `SLACK_APPROVERS_FILE` | Configuration statique alternative, sans SCIM, pour les essais. | Liste utilisateur→groupes maintenue et révisée hors dépôt; attribution d'identités réellement distinctes. | Refuser self-approval et rôle retiré. En mode solo, ne pas présenter un quorum simulé comme séparation des tâches indépendante. |
| Permissions de routes | Middleware protège routes admin/webhook selon leur périmètre. | Définir les clients, ingress, CORS, TLS/mTLS externe et règles réseau. Vérifier en particulier chaque route publique `/api/diagnostics/*`, `/mcp` et endpoints sensibles pour cette configuration. | Matrice route × rôle × statut HTTP; tests externes de non-authentification, CORS et rate limit. |

Une clé API est une authentification par secret partagé, pas un SSO, un
identifiant humain individuel ni une preuve de séparation des tâches. Entra
n'est pas nécessaire pour le profil solo; il l'est pour qualifier le parcours
Entra réel.

### 2.4 Approbation, reprise et exécution

**Chaîne visée :** épisode `AWAITING_APPROVAL` durable → proposition immuable →
demande d'approbation → quorum indépendant → claim durable → revalidation
identité/politique/état cible → exécution limitée → vérification post-action →
compensation/rollback → clôture et audit.

| Maillon | État du dépôt | Mapping/implémentation restant |
|---|---|---|
| Création proposition/demande | `FrozenProposal` lie `episode_id`, action, cible, risque, version de politique, quorum et `requester_id`; le hash protège les champs. | Câbler le vrai `request_approval` à la transition de l'orchestrateur et persister la demande avant de notifier. Le stub actuel `request_approval` ne suffit pas. |
| Interface d'approbation | Repo possède validations de hash, expiration, quorum, rôle, doublon et self-approval. | Configurer le canal réel (par exemple Slack), workspace/app, signing secret, callback URL, événements autorisés et politique de retry; mapper user ID et groupe à la source d'identité. |
| Claim durable | Quorum et entrée d'outbox sont transactionnels; le worker reprend un claim en simulation. | Idempotence sur toutes les répétitions de callback; concurrence entre approbateurs/workers; état terminal/TTL; réconciliation si action réussie mais ack perdu. |
| Reprise de l'épisode | `Orchestrator.resume_from_claim` est actuellement un stub; le worker simule l'action depuis le claim et ne continue pas l'épisode suspendu. | Persister/recharger l'épisode et ses preuves; revalider l'empreinte de proposition, la version de politique, la fraîcheur d'inventaire, l'identité et l'état courant; transition FSM explicite; événement append-only au lieu d'écraser le record; déduplication crash/retry. |
| Exécuteur | Live reste désactivé; le chart donne actuellement un Role Kubernetes de lecture pods/logs et patch deployments. | Définir contrat par action et cible, compte de service distinct par worker/action si possible, permissions minimales précises, validation d'objet avant/après et interdiction explicite des commandes génériques. |
| Vérification/compensation | Il n'existe pas de contrat générique pour attester que l'effet souhaité a eu lieu puis annuler en cas d'échec. | Pour chaque action : préconditions, idempotency key, état attendu, métrique de succès, délai, seuil d'échec, stratégie de compensation et approbation associée. Tester échec partiel et rollback. |
| Kill switch | Contrôle applicatif via gateway, pas indépendant de l'hôte/cluster. | Ajouter contrôle indépendant (policy admission, permission révocable, réseau, opérateur) qui bloque même si le processus est compromis; tester latence d'activation et comportement en panne. |

**Gate ferme :** ne pas activer les actions mutatrices en production avant la
reprise d'épisode, un executor qualifié pour une action et une seule, les
droits minimaux, la vérification post-action, la compensation, les tests de
crash/duplication, un kill switch indépendant et une approbation distincte.

### 2.5 Stockage, sauvegarde et restauration

**Chaîne visée :** données identifiées → écritures transactionnelles →
persistance durable → sauvegarde cohérente → stockage hors hôte → intégrité/
confidentialité contrôlées → restauration isolée → promotion de la restauration.

| Chemin / ressource | Contenu | Ce qui doit être fourni et prouvé |
|---|---|---|
| `ALERT_OUTBOX_DB_PATH` → `alerts.db` | Alertes, statuts, leases, déduplication, classification. | PVC/volume, quota, chiffrement, rétention, snapshot cohérent et vérification des enregistrements attendus. |
| `APPROVAL_DB_PATH` / `SCIM_DB_PATH` → `approvals.db` | Approbations, claims, identité SCIM si activée. | Sauvegarde protégée comme donnée personnelle/sensible; mêmes exigences, ACL et rétention conformes à la politique de l'opérateur. |
| `POLICY_QUOTA_DB_PATH` → `policy_quotas.db` | Réservations et quotas. | Décider si sauvegardé ou régénérable; ne jamais restaurer un état qui permet de contourner un quota sans évaluation explicite. |
| `EVIDENCE_STORE_DIR` | Fichiers d'épisode, `_index.json`, `ledger.jsonl`. | Copier le répertoire après quiescence; vérifier chaîne/signatures après restauration. Préserver les fichiers d'épisode associés à l'index et au ledger. |
| `LEDGER_SECRET_KEY` | Secret de signature des preuves locales. | Sauvegarde séparée et protégée, rotation versionnée; perte de clé peut rendre anciennes preuves non vérifiables, compromission compromet leur authenticité. |
| `agentic-ops-db backup/restore/verify` | Snapshot par fichier SQLite via API backup, `integrity_check`, SHA-256. | L'outil est par base; un opérateur doit arrêter tous les écrivains et sauvegarder le lot + preuves de façon cohérente. Il n'offre pas encore stockage distant, chiffrement, planification, catalogue ni sauvegarde atomique globale. |
| Profil Helm | `replicaCount: 1`, PVC `ReadWriteOnce`. | C'est mono-réplica et non HA. Pour nœud/volume perdu : copie hors cluster et procédure de reconstruction. Pour HA : changer d'adaptateur avant d'augmenter les réplicas. |

Runbook de qualification de restauration : sauvegarder depuis la cible, relever
horodatage/version/digests; restaurer sur un namespace ou environnement isolé;
contrôler `PRAGMA integrity_check`, comptes/statuts des bases, chaîne d'évidence,
probes, lecture du statut d'alertes et un événement de test; mesurer RPO/RTO;
ne basculer qu'après décision explicite et conserver l'original pour retour
arrière. Tester aussi le cas où une base ou l'index est manquant/corrompu.

### 2.6 Déploiement Kubernetes et runtime

**Chaîne visée :** source revue → artefact versionné → configuration → secrets →
image vérifiée → admission → rollout → readiness → smoke test → rollback.

| Clé Helm / env | Usage | Mapping à renseigner sur la cible |
|---|---|---|
| `image.repository`, `image.tag`, `image.pullPolicy` | Référence à l'image GHCR. | Version exacte par digest immuable en environnement qualifié; droits de pull selon la visibilité du package; éviter le tag flottant `latest`. |
| `replicaCount`, `persistence.enabled`, `persistence.size`, `accessModes`, `storageClassName`, `mountPath` | Nombre d'instances et stockage stateful. | StorageClass, type/zone du disque, capacité/croissance, reclaim policy, encryption, snapshots, attach/recovery, quota et owner. Aujourd'hui `replicaCount` doit rester 1 avec SQLite. |
| `resources`, `alertWorker.resources`, `approvalWorker.resources` | Requests/limits CPU/mémoire par conteneur. | Mesurer utilisation réelle sous charge, définir headroom, limites et comportement OOM/eviction; vérifier que les processus ont le temps de shutdown. |
| `probes.liveness`, `probes.readiness` | `/healthz`, `/ready`. | S'assurer que readiness dépend des services indispensables et que liveness n'entraîne pas une boucle de redémarrages lors d'une panne externe. Définir délai de grâce et startup probe si nécessaire. |
| `serviceAccount`, `rbac` | Identité Kubernetes de l'application et permissions. | Nommer le cluster/namespace et documenter chaque ressource/verbe; retirer toute permission non requise par les adaptateurs activés. Séparer worker d'alerte, worker d'approbation et API si leur périmètre diffère. |
| `crypto.signingSecretName`, `apiAuth.secretName`, `grafanaWebhook.secretName`, `approvalWorker.approversSecretName`, `identity.scimBearerSecretName` | Références aux Secrets précréés; les valeurs des secrets ne vont pas dans values Git. | Créer via Secret Manager/External Secrets/SOPS approuvé; mapper chaque clé requise; restreindre RBAC lecture; tester rotation et absence dans rendered manifest/log. |
| `identity.*` | OIDC/SCIM facultatifs. | Ne configurer OIDC que si tenant ID et audience sont tous deux connus; SCIM séparé, bearer secret, URL publique HTTPS et mapping d'attributs. |
| `inventory.enabled`, `inventory.generatedAt`, `inventory.maxAgeSeconds`, `inventory.targets` | Allowlist locale en ConfigMap en lecture seule; checksum provoque rollout. | Pipeline ou opérateur qui produit la valeur depuis un inventaire vrai; revue/approbation de changement; monitorer expiration avant le délai de refus. |
| `env.ENVIRONMENT`, `env.LOG_LEVEL` | Contexte et verbosité. | Noms d'environnement convenus, règles de logs et politique de données personnelles; pas de secrets ni payloads sensibles en logs. |

Éléments souvent à fournir hors du chart : ingress et TLS, DNS, NetworkPolicy,
PodDisruptionBudget (à évaluer pour profil mono-réplica), anti-affinity,
backup controller, External Secrets, admission policy, image signature policy,
quota/limitrange, autoscaling (désactivé/inadapté avec SQLite mono-réplica),
GitOps, RBAC opérateur et stratégie de promotion/rollback.

### 2.7 Secrets, clés et données

Pour chaque secret, dresser une ligne de registre : identifiant logique, nom
Kubernetes/manager, propriétaire, consommateurs, permissions, rotation,
révocation, dépendances après rotation et test de reprise. Inclure au minimum :

- `ADMIN_API_KEY` et éventuellement `ADMIN_API_KEY_PREVIOUS`;
- `GRAFANA_WEBHOOK_SECRET` et éventuellement clé précédente;
- `LEDGER_SECRET_KEY`;
- `SCIM_BEARER_TOKEN`;
- `SLACK_SIGNING_SECRET` si le callback Slack est activé;
- credentials OIDC/LLM ou GitHub éventuels pour adaptateurs activés.

Les secrets ne doivent apparaître ni dans les commits, logs, images, valeurs
Helm en clair, artefacts CI ou captures. Pour les preuves cryptographiques,
définir qui peut générer/faire tourner la clé, comment les anciennes preuves
sont vérifiées, comment la restauration récupère une version de clé et quelle
alerte est déclenchée si une clé manque.

Pour les données d'alerte et d'épisode, classer les labels, annotations,
identifiants, noms d'utilisateur et extraits de logs; définir minimisation,
masquage, accès, chiffrement, rétention, suppression et export d'audit.

### 2.8 Observabilité, SLO, incident response

Avant un SLO, mesurer au moins : taux d'admission HTTP, `202`/`4xx`/`5xx`,
alertes en attente/`DEAD`, âge de plus vieille alerte, retries par motif,
durée admission→classification→épisode, heartbeat worker, leases expirées,
erreurs DB/verrou, utilisation disque/PVC, état de probes, auth refusée,
inventaire proche de l'expiration, actions bloquées et vérification ledger.

| Maillon d'exploitation | Mapping réel à fournir | Preuve |
|---|---|---|
| Signal → métrique/log | Noms de métriques et labels de faible cardinalité; éviter tracking ID comme label. | Dashboard et test qu'une alerte de test apparaît de bout en bout. |
| Seuil → alerte opérateur | Seuils d'alerte backlog, âge, `DEAD`, worker absent, PVC/disque, DB errors, inventaire expirant, auth anormale. | Simuler chaque panne et vérifier notification/contact responsable. |
| SLO | Disponibilité, fraîcheur admission/traitement, erreur, intégrité et fenêtres de mesure définies. | Mesure historique; budget d'erreur; ne pas inventer de pourcentage sans trafic et criticité convenus. |
| RPO/RTO | Perte maximale tolérée et temps de reprise séparés par base/évidence et scénario. | Exercice de restauration chronométré et data loss effectivement mesuré. |
| Runbook/astreinte | Responsable primaire, secondaire, canal, pouvoir de couper l'exécution, escalade et communication. | Exercice hors heures ouvrées ou simulation avec opérateur, retour d'expérience et tâches suivies. |
| Incident postmortem | Chronologie, impact, déclencheur, données/actions affectées, correction et prévention. | Modèle de postmortem non blâmant et action item avec owner/date. |

### 2.9 Supply chain, versions et promotion

La release GitHub actuelle construit/teste, vérifie l'accord des versions,
publie le package PyPI via Trusted Publishing puis l'image multiarchitecture
GHCR. Elle ne déploie pas. Les registres ne forment pas une transaction
atomique.

Avant la release : revue des changements, tests complets, scan dépendances et
image, vérification de l'absence de données locales/secrets, licence/SBOM,
provenance/signature selon politique. Après publication : vérifier les hashes
PyPI, digest image/architectures, visibilité GHCR et téléchargement anonyme
si attendu. Pour promotion, référencer un digest, déployer d'abord en
préproduction, smoke test, approbation opérateur, promotion en cible puis
rollback version/digest testé. Un succès PyPI suivi d'un échec GHCR laisse un
état partiel; relancer le job image sans republier une version PyPI existante.

### 2.10 Adaptateurs d'observabilité et LLM

Si une intégration distante est activée, pour chaque adaptateur remplir :
base URL/DNS, CA TLS, audience ou token, identité de service, permission
lecture/écriture exacte, timeout total, concurrence, quota, retry/backoff,
limite de réponse, classification de données et comportement si indisponible.
Les URLs de test codées en exemple ou les endpoints personnels ne sont pas une
configuration de production.

Une réponse LLM doit rester non fiable : parser via schéma, valider action et
cible contre catalogue/inventaire/politique, appliquer un budget total (pas
seulement par sous-requête), tracer le modèle/version/coût sans secrets,
refuser la sortie invalide et faire des tests adversariaux. Le parcours
d'alerte actuel est déterministe et ne requiert pas de LLM; garder cette
propriété sauf qualification explicite.

### 2.11 Conformité, audit et gouvernance

Le dépôt comprend des mécanismes de hash/HMAC et Merkle; ils ne signifient pas
à eux seuls WORM physique, non-répudiation, conformité EU AI Act, SOC 2 ou ISO
42001. Pour revendiquer une garantie, mapper chaque obligation à : contrôle,
owner, preuve, durée de conservation, tiers de confiance, fréquence de revue,
procédure de déviation et audit indépendant.

Pour audit indépendant, définir la menace (admin hôte, opérateur CI, vol de
clé), séparation des clés, signature de racines, horodatage/transparence,
stockage immuable externe, témoins, rétention, droit de rectification/
effacement applicable et procédure de vérification côté auditeur. Tester
restauration et divergence/split-view; une chaîne locale seule ne protège pas
contre l'administrateur qui contrôle à la fois l'hôte et la clé.

## 3. Registre consolidé des clés de mapping à compléter

Compléter ce registre pour **une cible nommée** avant toute qualification. Ne
pas placer les valeurs secrètes dans ce document versionné; inscrire un
référent ou un identifiant de secret manager non sensible.

| Domaine | Clés/objets dans le repo | Valeur de mapping externe à décider/renseigner | Responsable attendu | Preuve exigée |
|---|---|---|---|---|
| Release | `project.version`, `Chart.yaml:version/appVersion`, `values.yaml:image.tag` | Tag de release, commit source, digest PyPI/OCI. | Mainteneur/release owner | Run CI, hashes, architectures, provenance. |
| Cible | `inventory.targets.<id>` | `alertname` → `risk_id` → label `service/job` → ressource réelle, replicas et criticité. | Owner de la plateforme cible | Échantillons de labels réels, comparaison inventory↔API source, cible absente refusée. |
| Webhook | `GRAFANA_WEBHOOK_SECRET`, endpoint webhook | Instance/folder/rule Grafana, DNS/TLS, labels, secret manager. | Observability owner | Test de bout en bout et rotation. |
| API | `ADMIN_API_KEY` ou `ENTRA_*` | Client/service principal, audiences/roles, route exposure, scopes et CA. | IAM/API owner | Tests positifs/négatifs, révocation. |
| SCIM | `SCIM_ENABLED`, `SCIM_DB_PATH`, `SCIM_BEARER_TOKEN` | Enterprise app URL, externalId, groupe exact, scope et cadence. | IAM owner | Create/update/revoke/delete et délai mesuré. |
| Approbation | `SLACK_APPROVERS_*`, `SLACK_SIGNING_SECRET`, quorum | Workspace, application, user IDs, groupes, quorum, séparation demandeur/approbateur. | Process owner/SecOps | Self-approval refusé, rôle retiré, callback replay et crash. |
| Policy | fichiers YAML `autonomy_policy`, `action_catalog`, `risk_register` | Owner, exceptions, approbations, quotas, risque et cycle de revue. | Risk/SRE owner | Scénarios de veto, revue signée/versionnée. |
| Exécution | `serviceAccount`, `rbac`, executor profile | Cluster/namespace, UID, ressources/verbes, action cible, contrôles d'après action. | Platform/action owner | Test least privilege et action sandbox avec rollback. |
| Données | `*_DB_PATH`, `EVIDENCE_STORE_DIR`, PVC | StorageClass, taille, chiffrement, rétention, backup target, region et ACL. | Data/platform owner | Restore chronométrée, integrity check, ledger verification. |
| Cryptographie | `LEDGER_SECRET_KEY` | Secret manager/KMS, version de clé, rotation, récupération et accès. | Security owner | Preuves avant/après rotation et restauration. |
| Réseau | Service/Ingress hors valeurs complètes | DNS, TLS issuer, ingress, egress, NetworkPolicy, IP source fiable. | Network owner | Scan/connection tests et isolation. |
| SLO/astreinte | Health/ready, logs et métriques existants | SLI, seuils, RPO/RTO, canaux, équipe et escalade. | Service owner | Historique, panne simulée, astreinte testée. |
| Supply chain | `.github/workflows/publish.yml` | Environment PyPI trusted publisher, package GHCR owner/visibility, approvals, scanners. | Release/security owner | Attestations vérifiées, scans et rollback de déploiement. |
| LLM/adaptateurs | Provider registry/adapters | Endpoint, modèle, identité, budget global, quotas, données autorisées. | AI/platform owner | Timeouts, panne, adversarial input, facturation/quotas. |

**Règle :** une cellule vide est un blocage, pas une valeur implicite. Les
exemples (`service/prediction-api`, `feature-pipeline`, valeurs de ressources,
groupes) ne sont pas les identifiants de votre environnement jusqu'à
confirmation par le propriétaire du système.

## 4. Gating de promotion proposé

| Gate | Conditions de sortie |
|---|---|
| G0 — Périmètre | Profil, données, actions, risques, owner, charge, objectifs mesurables écrits. |
| G1 — Source/config | Mapping d'alertes, inventaire daté, politique revue, clés/secrets provisionnés hors Git. |
| G2 — Sécurité | Routes/API/webhook testés; RBAC minimal; rotation; scan secret/image/dépendances; threat model révisé. |
| G3 — Durabilité | Crash/retry/idempotence; backup hors hôte; restoration drill complet; intégrité SQLite + ledger. |
| G4 — Préproduction | Digest exact; admission et probes; parcours webhook/status; chaos ciblé; dashboard/alerting et rollback. |
| G5 — Exécution | Pour une action unique : approbation indépendante, reprise d'épisode, least privilege, post-check, compensation, kill switch indépendant, game day. |
| G6 — Promotion | Acceptation explicite par owner, limites et risques résiduels consignés, procédure d'arrêt et revue post-déploiement. |

Sans G5, rester en observation/simulation. Sans G3/G4, ne pas qualifier la
disponibilité ou la reprise. Une nouvelle image publiée ne fait franchir aucun
gate à elle seule.

## 5. Priorités adaptées à un projet solo

1. Remplacer les exemples par un inventaire réel et validé manuellement; garder
   l'expiration courte et les actions mutatrices désactivées.
2. Faire un exercice de sauvegarde/restauration sur une instance arrêtée et un
   support hors machine; inclure tous les fichiers de preuves et vérifier les
   hashes/ledger.
3. Déployer la version candidate sur une cible contrôlée; mesurer latence,
   débit, saturation disque, crash API/worker et récupération réelle du PVC.
4. Ajouter un tableau de bord et des alertes minimales pour backlog, worker,
   DB, inventaire et probes; écrire un runbook perso et une procédure de
   rollback.
5. Stabiliser une action en simulation; documenter préconditions et résultats.
   Ne pas activer mutation réelle sans second opérateur, sandbox cible,
   least-privilege attesté, validation post-action et kill switch indépendant.
6. Réévaluer après chaque changement de stockage, chart, secrets, version,
   cible ou charge; conserver les preuves datées et les limites.

Ces étapes produisent une trajectoire crédible vers un service personnel
fiable. Pour une exploitation industrielle d'équipe, les limites restantes
(notamment mono-réplica, absence d'owner/astreinte et d'identité indépendante)
doivent être levées avec les systèmes réels et leurs responsables.
