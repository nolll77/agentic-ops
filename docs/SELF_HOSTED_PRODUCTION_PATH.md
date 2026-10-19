# Profil personnel auto-hébergé : périmètre et qualification

Ce guide distingue un service personnel exploité par une seule personne d'un
service d'entreprise. « Production » n'est pas une propriété binaire du code :
la qualification porte sur un profil, une charge, une infrastructure, des
risques et des objectifs de reprise explicitement choisis.

## Profil atteignable sans tenant Entra

Un profil solo réaliste peut rester limité à **une instance, une personne
opératrice, des investigations en lecture seule et des actions en simulation**.
Il peut être déployé sur une seule machine ou un cluster local. Aucun tenant
Entra n'est requis pour ce périmètre.

Sans Entra, l'application accepte une clé API locale lorsque le mode Entra
n'est pas configuré. Les approbateurs peuvent être configurés statiquement;
SCIM et le worker d'approbation sont facultatifs. Cette option suffit pour des
essais personnels, mais ne prouve pas l'identité indépendante d'un approbateur
et ne fournit pas une séparation des tâches réelle lorsque la même personne
demande et approuve une action. Garder l'exécution réelle désactivée.

| Domaine | Peut être construit et vérifié seul | Limite à rendre explicite |
|---|---|---|
| Inventaire et politique | Le chargeur YAML local et l'allowlist exacte sont implémentés; l'absence, l'expiration et une cible inconnue sont refusées. | Le fichier reste maintenu manuellement; aucune découverte ni synchronisation avec une plateforme externe n'est fournie. |
| Parcours d'alerte | Exercer webhook, déduplication, worker, investigation simulée et reprise après arrêt forcé des processus. Des faux émetteurs locaux peuvent remplacer Grafana. | La connexion à une instance Grafana et ses garanties d'authentification/réseau ne sont pas testées par un faux émetteur. |
| Identité et approbation | Utiliser la clé API, une configuration locale d'opérateur et tester les refus, révocations de configuration et règles de quorum. | Sans fournisseur d'identité externe, il n'y a pas de SSO, de provisionnement de cycle de vie ni de preuve indépendante du rôle. Le quorum solo ne constitue pas une séparation des tâches. |
| SQLite et reprise | Garder un seul réplica; `agentic-ops-db` snapshotte/restaure chaque base via l'API SQLite et vérifie `integrity_check`. La reprise après expiration du bail est testée après arrêt brutal d'un processus. | Les tests locaux ne remplacent pas une sauvegarde restaurée depuis le stockage réellement retenu. Le PVC n'est pas une sauvegarde; pas de HA. |
| Sécurité opérationnelle | Générer et faire tourner les secrets localement; tester le kill switch applicatif, l'accès minimal et l'absence de secrets dans l'image, les logs et les manifests. | Le kill switch applicatif n'est pas un coupe-circuit indépendant de l'hôte; `chmod` et une chaîne de hash ne remplacent pas un stockage WORM indépendant. |
| Exploitation | `agentic-ops-benchmark-alerts` mesure localement le débit SQLite de l'outbox et la latence du worker; répéter sur la machine et le profil de déploiement visés. | Le benchmark est un micro-test sans Grafana, réseau, LLM ou action externe; ses résultats ne sont pas des SLO et ne créent ni astreinte ni redondance humaine. |

## Travaux encore à faire, sans Entra

Ces écarts sont des travaux du projet, pas des prérequis d'entreprise :

- Créer, dater et maintenir l'inventaire local des cibles réellement visées.
  Le code charge un fichier exact et expire sa validité; il ne découvre pas
  les systèmes et ne garantit pas que le fichier reflète leur état réel.
- Exercer une sauvegarde complète des bases et du répertoire d'évidence après
  arrêt des écrivains, restaurer depuis le support de sauvegarde choisi dans
  un environnement isolé et mesurer le RPO/RTO. Les tests CI couvrent le
  snapshot SQLite y compris l'état WAL, pas une sauvegarde du service déployé.
- Exécuter le benchmark sur la machine et le profil choisis, augmenter
  progressivement la charge, puis mesurer disponibilité et reprise après
  panne réelle du processus, du volume et de l'hôte. Le benchmark local inclut
  un arrêt de sous-processus et un bail d'une seconde; il ne mesure pas la
  disponibilité de l'API, le démarrage du pod ni la récupération d'un volume.
- Améliorer métriques, tableaux de bord locaux, alertes et procédures de
  retour arrière pour le profil réellement visé.
- Si le parcours d'approbation est retenu, relier la reprise du claim à
  l'épisode persistant de l'orchestrateur. Le worker actuel reprend une action
  en simulation; il ne reprend pas encore l'épisode suspendu.
- Maintenir les actions mutatrices désactivées tant que les contrats
  d'exécution, vérification post-action, compensation et essais de panne n'ont
  pas été conçus et qualifiés.

## Étapes de qualification autonomes

1. Fixer par écrit le périmètre : mono-instance, charge et durée attendues,
   données conservées, actions autorisées (aucune action mutatrice au départ)
   et objectifs de disponibilité, RPO et RTO. Ne pas choisir des chiffres
   « industriels » arbitraires : les mesurer sur la machine cible.
2. Créer un profil de déploiement local documenté, désactiver Entra/SCIM et
   les actions réelles, injecter les secrets depuis un mécanisme local hors
   dépôt, puis installer l'image publique. Vérifier les versions et les
   probes.
3. Générer un inventaire local exact avec date de génération et fenêtre
   d'expiration; monter le même fichier en lecture seule dans l'API et le
   worker. Tester un inventaire absent, périmé, mal formé et une cible
   inconnue; tous doivent refuser l'action.
4. Exercer le parcours d'alerte puis interrompre API et worker à plusieurs
   points : avant/après persistance, avec bail expiré, et après redémarrage.
   Vérifier qu'une alerte n'est ni perdue ni traitée deux fois de façon
   dangereuse.
5. Sauvegarder les bases selon une méthode cohérente, restaurer sur un
   environnement isolé, contrôler les intégrités SQLite et vérifier les
   épisodes, statuts et preuves récupérés. Consigner le temps de restauration
   et la perte maximale de données observée.
6. Exécuter des essais de charge et d'épuisement des ressources, renouveler
   chaque secret, exercer le kill switch pendant une requête et vérifier les
   logs, métriques et alertes de panne.
7. Conserver résultats, versions, limites et procédures de retour arrière.
   Une modification du code, du stockage, de la charge ou de la machine peut
   invalider une partie de la qualification.

Ces essais sont réalisables sans tenant ni abonnement d'entreprise. Ils
qualifient toutefois uniquement le profil personnel réellement exercé; un
cluster local n'est pas la preuve qu'un cluster distant ou un environnement
de production d'entreprise fonctionnera de la même manière.

### Inventaire local Kubernetes

Le chart peut créer un ConfigMap monté en lecture seule dans l'API et le worker.
Remplacer l'exemple par un `generatedAt` UTC récent avant chaque déploiement et
déclarer les cibles exactement comme les labels `service` ou `job` des alertes:

```yaml
inventory:
  enabled: true
  generatedAt: "2026-10-19T12:00:00Z"
  maxAgeSeconds: 86400
  targets:
    feature-pipeline:
      replicas: 1
      criticality: low
```

`generatedAt` est un exemple : le remplacer par l'heure UTC réelle au moment
de générer l'inventaire. L'inventaire expire après `maxAgeSeconds`; un pod
utilisant un inventaire périmé refusera les actions jusqu'à ce qu'il recharge
un inventaire valide.

Le chargeur refuse les schémas invalides, les clés YAML dupliquées, les
attributs invalides, les horodatages sans fuseau, les dates futures et les
inventaires périmés. En cas d'absence de fichier configuré, les décisions de
politique échouent fermé avec `INV-001`. Un inventaire configuré mais invalide
empêche le démarrage du worker/API plutôt que de se rabattre sur des valeurs
par défaut. Une mise à jour Helm change le checksum du pod template et
déclenche un rollout afin que l'API et le worker rechargent le nouveau fichier.

### Sauvegarde/restauration SQLite locale

Arrêter l'API et tous les workers pour obtenir un point cohérent entre bases,
puis snapshotter chaque base SQLite persistante (`alerts.db`,
`approvals.db`, `policy_quotas.db`) avec l'API de sauvegarde SQLite. Ne pas
copier directement un fichier `.db` pendant que des écrivains actifs utilisent
WAL. Exemple:

```sh
agentic-ops-db backup \
  --source /var/lib/agentic-ops/alerts.db \
  --destination /chemin/backup/alerts.db
agentic-ops-db verify /chemin/backup/alerts.db
agentic-ops-db restore \
  --source /chemin/backup/alerts.db \
  --destination /chemin/restauration/alerts.db
```

Répéter pour les autres bases et copier également le répertoire d'évidence
après arrêt des écrivains. La commande refuse d'écraser un fichier de
destination et émet un SHA-256; conserver ce digest avec le support de backup.
Restaurer dans un chemin isolé, vérifier l'intégrité et contrôler des dossiers
connus avant de redémarrer l'instance. Le runbook ne fournit pas encore un
orchestrateur de sauvegarde atomique multi-base ni une destination distante.

### Mesure de charge locale

```sh
agentic-ops-benchmark-alerts --count 500
```

La sortie JSON rapporte le débit d'ingestion et de traitement de l'outbox,
les latences p50/p95/max du worker, la taille SQLite et le temps entre le
début du crash d'un sous-processus et le traitement après expiration d'un bail
d'une seconde. Elle utilise des alertes synthétiques, une base temporaire
locale et un handler sans effet externe; elle ne mesure pas le débit HTTP,
Grafana, l'infrastructure cible ou une disponibilité en production. Conserver
les résultats avec l'OS, le CPU, la version de l'application et le nombre de
workers pour permettre une comparaison utile.

Résultat de référence exécuté le 19 octobre 2026 dans l'arbre de travail local
(macOS 12.3.1 x86_64, Intel Core i9-9880H, Python 3.11.6, 500 alertes; un
worker, handler sans effet externe) :

| Mesure | Résultat |
|---|---:|
| Ingestion en lot | 12 988 alertes/s |
| Traitement du worker | 216 alertes/s |
| Latence worker p50 / p95 / max | 4,551 / 5,874 / 12,211 ms |
| Crash du sous-processus → traitement après bail de 1 s | 1,147 s |

Ce chiffre de reprise inclut le lancement du sous-processus et l'attente du
bail, mais pas le redémarrage d'un pod, l'indisponibilité du volume ou le
redémarrage complet de l'API. Cette mesure ponctuelle sur un poste local n'est
pas un objectif de service ni une prédiction pour le cluster cible.

## Dépendances uniquement nécessaires à des garanties supplémentaires

- **Microsoft Entra** : requis pour qualifier le SSO OIDC et le
  provisionnement/déprovisionnement SCIM Entra réels. Pas requis pour le
  profil solo à clé API.
- **Grafana, Slack ou autre service** : requis seulement pour qualifier le
  connecteur et le cycle de vie réel du service concerné. Les faux endpoints
  suffisent aux tests de contrat et de panne internes, pas à cette intégration.
- **Stockage/cluster redondant et sauvegarde hors machine** : requis pour
  revendiquer la continuité après perte d'un hôte ou d'un volume. SQLite
  mono-réplica est approprié à un périmètre mono-instance assumé, pas à une
  promesse de haute disponibilité.
- **KMS/HSM, stockage WORM ou journal externe** : requis pour des garanties de
  gestion de clés et d'audit indépendantes de l'administrateur de l'hôte.
- **Opérateurs supplémentaires et identité indépendante** : requis pour une
  vraie séparation des tâches, une revue à plusieurs et une couverture
  d'astreinte.

## Statut vérifié du dépôt

La release `v0.1.4` a été publiée sur PyPI et GHCR; la candidate `v0.1.5`
améliore la gestion d'authentification des interfaces Render. L'automatisation
coordonne PyPI puis GHCR. Un
parcours local Docker/kind sans tenant Entra a
déjà traité une alerte en simulation et conservé son état après redémarrage
du pod sur le même PVC. Cela ne vérifie pas encore une restauration de
sauvegarde, une perte de volume/nœud, une qualification sur machine cible ni
une exécution réelle. L'essai Docker/kind historique portait sur `v0.1.3`;
les changements d'inventaire, backup/restore et benchmark livrés en `v0.1.4`
doivent être exercés sur une cible avant qualification. Voir aussi
[`ENTRA_PREPRODUCTION_QUALIFICATION.md`](./ENTRA_PREPRODUCTION_QUALIFICATION.md),
[`PRODUCTION_READINESS_ROADMAP_AND_GAPS.md`](./PRODUCTION_READINESS_ROADMAP_AND_GAPS.md)
et [`INDUSTRIAL_PRODUCTION_BLUEPRINT.md`](./INDUSTRIAL_PRODUCTION_BLUEPRINT.md).
