# Qualification Entra et préproduction

**Statut au 2026-10-19 :** code local implémenté et testé. Un build Docker
local et un déploiement éphémère sur kind sans tenant Entra ont été exercés;
l'image `v0.1.3` a été publiée publiquement sur GHCR. Aucun cluster cible
distant n'a été qualifié.

Ce document sépare les livrables logiciels des opérations qui nécessitent un
tenant, un registre d'images et un cluster sous la responsabilité de l'équipe.
La réussite de la CI ne vaut pas validation en préproduction ou en production.

## Résumé de ce qui est livré dans le dépôt

- Authentification des routes administratives par jeton Microsoft Entra v2 :
  signature RS256 obtenue via les clés JWKS du tenant, validation de `iss`,
  `aud`, `tid`, `exp`, `iat` et du rôle d'application requis. Lorsque le mode
  Entra est configuré, une clé API ne constitue pas de voie de contournement.
- Endpoints SCIM 2.0 `/scim/v2/Users` et `/scim/v2/Groups`, protégés par un
  bearer secret dédié, avec stockage SQLite, opérations de cycle de vie et
  groupes de rôles autorisés `SRE`, `SRE_LEAD`, `DATA_STEWARD`, `SECOPS`.
- Correspondance SCIM `externalId` ↔ identifiant de membre Slack. L'utilisateur
  doit être actif et appartenir au groupe requis; le worker revalide les rôles
  au moment de traiter un claim.
- Worker d'approbation durable, déployable en sidecar opt-in. Il exécute
  uniquement en simulation et ne reprend pas encore l'épisode suspendu de
  l'orchestrateur.
- Chart Helm version `0.1.3`, image configurée `ghcr.io/nolll77/agentic-ops:v0.1.3`,
  ports/sondes alignés sur `8001`, PVC pour l'état persistant et garde de
  réplica pour le profil SQLite. Le chart exige désormais une référence
  `crypto.signingSecretName` (même clé persistante dans l'API et les workers),
  `grafanaWebhook.secretName` quand le worker d'alertes est activé, et
  `apiAuth.secretName` lorsque Entra n'est pas configuré.

La suite locale avait été vérifiée à **193 tests réussis et 3 ignorés** avant
les dernières modifications. Depuis, un build Docker local a réussi. Le chart
a passé `helm lint`, puis a été installé dans un cluster kind jetable sans
tenant Entra. Après configuration de Secrets locaux, un webhook Grafana a
traversé l'API et le worker; l'alerte a été classée `DATA-042` et a produit
l'épisode simulé `EP-0001`. `/healthz` et `/ready` ont répondu 200. Après un
redémarrage du pod, l'état `COMPLETED` et l'épisode sont restés lisibles sur le
PVC.

Environnement de l'essai : macOS 12.3.1, Docker Engine 24.0.6, Helm 4.3.1,
kind 0.33.0 avec un nœud Kubernetes `kindest/node:v1.37.0`. Le chart a été
rendu avec Entra et SCIM désactivés, l'approval worker désactivé, un seul
réplica, et les références aux Secrets runtime fournies par valeurs Helm.
Le secret de signature, la clé API et le secret webhook ont été générés pour
l'essai dans le cluster local, jamais inscrits dans le dépôt.

Cette expérience démontre un parcours local et la persistance après
redémarrage du pod uniquement. Elle ne teste pas la restauration d'une
sauvegarde, la perte du volume/nœud, un cluster distant, une identité Entra ou
la qualification d'un cluster distant. L'image `v0.1.3` a depuis été publiée
sur GHCR; cette publication ne constitue pas une qualification du déploiement.
Le cluster kind a été supprimé après les essais.

## Travaux restants avant une qualification préproduction

### 1. Configurer l'application Entra pour OIDC

- [ ] Créer ou sélectionner l'enregistrement d'application de l'API
  Agentic-Ops dans le tenant dédié de préproduction.
- [ ] Définir l'App ID URI/audience et un app role `AgenticOps.Admin` (ou
  documenter le nom choisi).
- [ ] Affecter ce rôle uniquement aux principals de service et groupes
  opérateurs autorisés; ne pas accorder de permissions plus larges par défaut.
- [ ] Déployer `ENTRA_TENANT_ID`, `ENTRA_API_AUDIENCE` et
  `ENTRA_REQUIRED_ROLE` depuis la configuration de déploiement. Ne pas les
  laisser partiellement configurés : le service échoue fermé.
- [ ] Vérifier qu'un jeton du bon tenant, audience et rôle passe, et qu'un
  jeton expiré, d'un autre tenant/audience ou sans rôle est refusé. Vérifier
  également qu'une clé API n'ouvre pas ces routes une fois Entra activé.
- [ ] Exercer une rotation JWKS et une indisponibilité du fournisseur; confirmer
  le refus ou la réponse temporaire prévue et l'alerte d'exploitation.

### 2. Configurer le provisionnement SCIM Entra

- [ ] Créer l'application d'entreprise de provisionnement SCIM et configurer
  son URL de base sur l'URL HTTPS publique de l'API suivie de `/scim/v2`.
- [ ] Générer un bearer secret aléatoire d'au moins 32 caractères, le stocker
  dans le gestionnaire de secrets du cluster puis le référencer par
  `identity.scimBearerSecretName` et `identity.scimBearerSecretKey`. Ne pas
  l'ajouter à Git, à une ligne de commande conservée dans l'historique ou aux
  journaux.
- [ ] Activer `identity.scimEnabled` et configurer l'application pour envoyer
  l'identifiant du membre Slack comme SCIM `externalId` de chaque utilisateur.
- [ ] Provisionner uniquement les groupes dont `displayName` correspond
  exactement à `SRE`, `SRE_LEAD`, `DATA_STEWARD` ou `SECOPS`.
- [ ] Limiter le scope de provisionnement aux utilisateurs et groupes autorisés.
  Vérifier les attributs, le provisioning initial, les mises à jour, la
  désactivation/suppression d'utilisateur et l'ajout/retrait d'un groupe.
- [ ] Mesurer le délai réel entre la révocation dans Entra et son application
  par le service. La révocation n'est effective qu'après réception de la mise
  à jour SCIM; le code n'interroge pas Entra en temps réel au clic.
- [ ] Tester token SCIM invalide, secret absent, identifiant Slack dupliqué,
  rôle inconnu, membre inconnu et réponses Entra/SCIM en erreur.
- [ ] Documenter l'équipe responsable de l'application, du bearer secret, de
  la revue des groupes et du traitement des erreurs de synchronisation.

### 3. Publier l'image et déployer le chart

La publication d'image est coordonnée avec PyPI. Ce dépôt utilise GHCR sous
`ghcr.io/nolll77/agentic-ops`; le workflow
`.github/workflows/publish.yml` publie d'abord le paquet PyPI, puis, si cette
étape réussit, construit et publie les images amd64 et arm64 depuis le même
tag de release. Vérifier que la version de `pyproject.toml` correspond au tag
`vX.Y.Z`. Le workflow utilise le checkout de la source pour Docker : il ne
télécharge pas le paquet publié sur PyPI. Pour le premier push, vérifier
également que le package GHCR est rendu public si les téléchargements
anonymes sont souhaités. Le tag attendu par ce chart est
`ghcr.io/nolll77/agentic-ops:v0.1.3`.

Pour le profil personnel solo sans Entra et les validations réalisables sur
une seule machine, voir [`SELF_HOSTED_PRODUCTION_PATH.md`](./SELF_HOSTED_PRODUCTION_PATH.md).

- [ ] Vérifier dans le registre que le tag `v0.1.3` existe, relever le digest
  immuable, analyser l'image et vérifier sa provenance/signature selon la
  politique de release.
- [ ] Installer Helm dans l'environnement de livraison et exécuter
  `helm lint helm/agentic-ops` ainsi qu'un rendu avec les valeurs de
  préproduction; valider le résultat avec les contrôles Kubernetes retenus.
- [ ] Choisir une StorageClass et confirmer que le PVC est `Bound`, sauvegardé
  selon la politique retenue et attachable au pod cible.
- [ ] Créer un Secret Kubernetes hors dépôt contenant un `LEDGER_SECRET_KEY`
  persistant et configurer `crypto.signingSecretName` et
  `crypto.signingSecretKey`. La même valeur doit être injectée dans l'API et
  les workers; une clé éphémère ne permet pas de vérifier les preuves après
  redémarrage.
- [ ] En mode sans tenant Entra, créer un Secret contenant un
  `ADMIN_API_KEY` aléatoire d'au moins 32 caractères et le référencer par
  `apiAuth.secretName` / `apiAuth.secretKey`. Pour ingérer les alertes, créer
  un Secret avec `GRAFANA_WEBHOOK_SECRET` d'au moins 32 caractères et le
  référencer par `grafanaWebhook.secretName` / `grafanaWebhook.secretKey`.
- [ ] Déployer avec `replicaCount=1`, `persistence.enabled=true`,
  `identity.scimEnabled=true` et `approvalWorker.enabled=true`. Configurer
  `identity.entraTenantId`, `identity.entraApiAudience`,
  `identity.entraRequiredRole` et la référence au secret SCIM.
- [ ] Confirmer que l'image démarre sur `8001`, que `/healthz` et `/ready`
  répondent, que l'API et les workers utilisent le même volume et que les
  secrets ne sont pas exposés dans les manifests rendus ou les logs.
- [ ] Confirmer que `SIMULATION_MODE=true` et qu'aucune action réelle n'est
  activée par le déploiement.

Exemple de commandes de vérification et déploiement, à exécuter depuis un
runner approuvé après création d'un fichier de valeurs protégé hors dépôt :

```sh
helm lint helm/agentic-ops \
  --set crypto.signingSecretName=agentic-ops-runtime \
  --set apiAuth.secretName=agentic-ops-runtime \
  --set grafanaWebhook.secretName=agentic-ops-runtime
helm template agentic-ops helm/agentic-ops \
  --namespace agentic-ops-preprod \
  --values /chemin/protege/agentic-ops-preprod-values.yaml
helm upgrade --install agentic-ops helm/agentic-ops \
  --namespace agentic-ops-preprod \
  --create-namespace \
  --values /chemin/protege/agentic-ops-preprod-values.yaml
```

Ne pas ajouter le fichier de valeurs de préproduction au dépôt s'il contient
des références de secrets ou des paramètres internes.

## Limite de stockage SQLite : profil mono-réplica

Le chart actuel partage des fichiers SQLite sur un PVC `ReadWriteOnce` entre
l'API et ses sidecars. `replicaCount` doit rester exactement à **1** lorsque la
persistance est activée. Ce profil n'est ni HA, ni multi-nœud, ni tolérant à la
perte définitive du volume ou du nœud. Ne pas augmenter les réplicas ou
déployer plusieurs releases pointant vers le même fichier SQLite.

Avant de retenir ce profil, l'équipe doit :

- [ ] vérifier le comportement du CSI/PVC lors d'un redémarrage de pod et d'une
  relocalisation sur un autre nœud;
- [ ] arrêter ou quiescer les écrivains avant une copie cohérente des fichiers
  de base; préférer l'API de sauvegarde SQLite ou un snapshot cohérent du
  volume plutôt qu'une copie arbitraire de fichiers WAL actifs;
- [ ] définir fréquence, rétention, chiffrement, contrôle d'accès et
  responsabilité des sauvegardes;
- [ ] restaurer une sauvegarde dans un namespace isolé, vérifier l'intégrité
  SQLite, les demandes/approbations, l'outbox, les épisodes et le redémarrage
  des workers;
- [ ] mesurer le RPO/RTO obtenu et le comparer aux objectifs approuvés.

Si le besoin impose plusieurs réplicas, une reprise multi-nœud ou une
disponibilité supérieure, remplacer SQLite par un adaptateur transactionnel
partagé qualifié (et migrer les outboxes/quotas/épisodes de manière vérifiée)
avant toute mise à l'échelle. Le chart actuel doit alors continuer à refuser le
profil multi-réplica SQLite.

## Exercices de bout en bout et de panne à réaliser

Utiliser un environnement isolé, des identités de test et des cibles sans effet
de production. Conserver pour chaque exercice l'horodatage, la version/digest
de l'image, la configuration de chart, les résultats, les logs corrélés, les
écarts et l'approbateur nommé.

1. **Alerte reconnue** : envoyer une alerte Grafana `CacDriftAlert`; vérifier
   acceptation durable, classification, épisode d'investigation associé et
   statut simulé. Aucun changement de ressource cible ne doit avoir lieu.
2. **Alerte inconnue** : vérifier `REVIEW_REQUIRED`, sans classification
   implicite ni tentative de remédiation.
3. **Approbation** : provisionner un utilisateur via SCIM, le faire approuver
   via Slack, vérifier le quorum et l'outbox, puis confirmer que le worker
   termine en `SIMULATED` seulement.
4. **Révocation** : retirer le groupe ou désactiver l'utilisateur, attendre la
   synchronisation SCIM et prouver qu'un claim non encore traité ne peut plus
   passer à `SIMULATED`.
5. **Crash/reprise** : tuer le worker API/alerte/approbation à des points
   contrôlés (avant claim, après claim, après persistance de résultat et avant
   ack); vérifier lease, reprise, absence de doublon et conservation de
   l'état.
6. **Stockage** : redémarrer le pod, simuler le détachement/rattachement PVC,
   provoquer un manque d'espace dans l'environnement de test, et confirmer
   que les erreurs sont visibles et que l'acceptation n'est pas annoncée
   lorsque la persistance échoue.
7. **Sauvegarde/restauration** : exécuter et chronométrer la procédure de
   sauvegarde puis restaurer dans un namespace isolé; comparer les identifiants
   et états avant/après.
8. **Identité/réseau** : simuler Entra/JWKS inaccessible, jeton invalide,
   bearer SCIM révoqué, et retard/échec de provisionnement; vérifier les refus,
   la télémétrie et l'escalade.
9. **Retour arrière** : restaurer la version antérieure du chart et de l'image
   avec conservation de l'état; documenter la compatibilité du schéma SQLite.

La promotion exige un responsable SRE et un responsable sécurité/identité
nommés, des objectifs SLO/RPO/RTO approuvés et mesurés, des alertes et runbooks
opérationnels, des exercices réussis sans écart critique, ainsi qu'une décision
de promotion enregistrée. Aucun de ces critères n'est réputé satisfait par la
suite de tests locale.

## Registre des validations externes

À compléter par l'équipe avant chaque décision de promotion. Aucun propriétaire
ni résultat de qualification n'est présumé par ce document.

| Porte | Responsable à nommer | Preuve à joindre | État |
|---|---|---|---|
| Entra OIDC / rôles d'application | Équipe IAM / sécurité | App registration, affectations de rôle et résultats des tests de jeton | À configurer |
| Provisionnement SCIM / cycle de vie | Équipe IAM | Rapport de provisioning, tests d'ajout/retrait/désactivation et délai de révocation mesuré | À configurer |
| Publication de l'image `v0.1.3` | Équipe release / supply chain | Digest public vérifié; scan/signature/provenance restent à ajouter ou qualifier | Image publiée; contrôles supply-chain restants |
| Stockage Kubernetes mono-réplica | Équipe plateforme / SRE | StorageClass, PVC `Bound`, comportement de rattachement et procédure de sauvegarde | À déployer |
| Parcours E2E et tests de panne | SRE / équipe applicative | Rapports horodatés, logs corrélés, résultats de reprise et liste d'écarts | À exercer |
| Restauration et objectifs SLO/RPO/RTO | Responsable de service / SRE | Rapport de restauration chronométré et objectifs approuvés | À exercer |
| Décision de promotion | Responsable SRE et sécurité | Approbation nommée, périmètre d'action et critères de rollback | À approuver |

## Décision de capacité

Jusqu'à la clôture et à la preuve des contrôles ci-dessus, le statut est :

> **Code d'intégration présent; environnement Entra et capacité industrielle
> de production non validés. Mode autonome et mutation réelle désactivés.**

Toute exception, tout écart et toute dérogation au profil mono-réplica doivent
être approuvés, bornés dans le temps et documentés avant le déploiement.
