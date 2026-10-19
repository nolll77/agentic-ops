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
| Inventaire et politique | Fournir un inventaire local versionné et une allowlist exacte; tester les cibles inconnues et les refus fail-closed. | Ce n'est pas une source d'inventaire mise à jour par une plateforme externe. |
| Parcours d'alerte | Exercer webhook, déduplication, worker, investigation simulée et reprise après arrêt forcé des processus. Des faux émetteurs locaux peuvent remplacer Grafana. | La connexion à une instance Grafana et ses garanties d'authentification/réseau ne sont pas testées par un faux émetteur. |
| Identité et approbation | Utiliser la clé API, une configuration locale d'opérateur et tester les refus, révocations de configuration et règles de quorum. | Sans fournisseur d'identité externe, il n'y a pas de SSO, de provisionnement de cycle de vie ni de preuve indépendante du rôle. Le quorum solo ne constitue pas une séparation des tâches. |
| SQLite et reprise | Garder un seul réplica; écrire une procédure de sauvegarde cohérente, restaurer dans un environnement isolé et mesurer le RPO/RTO effectivement obtenu. Simuler crash, disque plein et perte du pod. | Le PVC survit à certains redémarrages, mais n'est pas une sauvegarde. La perte du disque, du volume ou du nœud peut rendre le service et les données indisponibles. Pas de HA. |
| Sécurité opérationnelle | Générer et faire tourner les secrets localement; tester le kill switch applicatif, l'accès minimal et l'absence de secrets dans l'image, les logs et les manifests. | Le kill switch applicatif n'est pas un coupe-circuit indépendant de l'hôte; `chmod` et une chaîne de hash ne remplacent pas un stockage WORM indépendant. |
| Exploitation | Définir la charge supportée, des seuils de santé, des alertes locales et des objectifs mesurés de disponibilité/reprise; exécuter des scénarios de panne reproductibles. | Les mesures ne valent que pour la machine et la période testées; elles ne créent ni astreinte ni redondance humaine. |

## Travaux encore à faire, sans Entra

Ces écarts sont des travaux du projet, pas des prérequis d'entreprise :

- Ajouter un chargeur d'inventaire local autoritatif et faire respecter une
  allowlist de cibles exacte. Aujourd'hui, une décision orchestrée sans
  fournisseur d'inventaire est refusée, mais aucun adaptateur de production ni
  chargeur `inventory.yaml` n'est livré.
- Ajouter ou documenter un parcours reproductible de sauvegarde/restauration
  SQLite, puis le tester après arrêt propre et panne forcée. La persistance sur
  le PVC après redémarrage du pod a été observée; ce n'est pas un test de
  restauration.
- Exercer les reprises et pannes du worker d'alertes sur le déploiement retenu,
  puis mesurer charge, latence, disponibilité et temps/perte de reprise.
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
3. Brancher une source d'inventaire locale à allowlist exacte. Tester un
   inventaire absent, périmé, mal formé et une cible inconnue; tous doivent
   refuser l'action.
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

La release `v0.1.3` est publiée sur GHCR, et l'automatisation de release
coordonne PyPI puis GHCR. Un parcours local Docker/kind sans tenant Entra a
déjà traité une alerte en simulation et conservé son état après redémarrage
du pod sur le même PVC. Cela ne vérifie pas encore une restauration de
sauvegarde, une perte de volume/nœud, une qualification sur machine cible ni
une exécution réelle. Voir aussi
[`ENTRA_PREPRODUCTION_QUALIFICATION.md`](./ENTRA_PREPRODUCTION_QUALIFICATION.md)
et [`PRODUCTION_READINESS_ROADMAP_AND_GAPS.md`](./PRODUCTION_READINESS_ROADMAP_AND_GAPS.md).
