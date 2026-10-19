# Plan d'exécution autonome — novembre 2026

## But et résultat attendu

Ce plan organise les travaux réalisables dans le dépôt et sur une machine locale,
sans tenant Entra, sans nouveau service payant et sans infrastructure
supplémentaire. Il complète les procédures de
[`SELF_HOSTED_PRODUCTION_PATH.md`](./SELF_HOSTED_PRODUCTION_PATH.md) et le statut
technique de [`INDUSTRIAL_IMPLEMENTATION_STATUS.md`](./INDUSTRIAL_IMPLEMENTATION_STATUS.md).

À la fin de l'exécution, le dépôt doit contenir une réconciliation idempotente
des refus d'approbation dans la preuve de l'épisode d'origine, les tests ciblés
des scénarios de panne et d'inventaire, et une procédure relue de répétition
locale de sauvegarde/restauration et de mesure de charge. Un rapport daté doit
séparer les résultats mesurés localement des garanties qui exigent encore un
déploiement externe.

**Ce document est un plan, pas un compte-rendu d'exercices réalisés.** Les
commandes, résultats et critères ci-dessous ne deviennent des preuves qu'après
exécution et enregistrement des observations.

## Périmètre et garde-fous

### Inclus

- Travail logiciel et tests sur la réconciliation du refus d'approbation.
- Tests déterministes des interruptions du worker dans un environnement isolé.
- Répétition de sauvegarde, vérification, copie locale distincte et restauration
  isolée avec données synthétiques.
- Exercices de durée de vie, expiration et changement de l'inventaire local.
- Mesures reproductibles de débit, latence et reprise du benchmark existant.
- Documentation des résultats, des écarts et des décisions de suite.

### Exclu de cette campagne

- Accès, modification ou redéploiement de Render ou d'une autre cible distante.
- Présentation d'une copie sur un second répertoire du même poste comme
  sauvegarde hors machine.
- Activation de toute action mutatrice réelle, de clé de production ou
  d'intégration à un système client.
- Envoi de vrais messages Slack, création d'une application Slack ou
  qualification d'une identité indépendante.
- Déclaration d'un RPO/RTO de production, d'une disponibilité HA ou d'une
  certification industrielle sur la base de mesures locales.
- Usage de données de production, secrets réels ou tokens dans les fixtures,
  journaux, preuves de test et rapport.

Le mode simulation reste obligatoire. Chaque base, répertoire d'évidence et
destination de restauration doit être explicitement isolé. Ne pas exécuter les
commandes d'exercice contre des chemins configurés par une instance active.

## Préparation et règle de preuve

Avant de commencer :

1. Lire ce plan, les procédures du guide auto-hébergé et l'état courant du
   dépôt; vérifier la branche et noter le commit testé.
2. Utiliser un environnement de développement isolé, des bases temporaires,
   une clé de ledger réservée aux tests et des données synthétiques.
3. Vérifier que l'exécution réelle est désactivée et qu'aucun worker ou serveur
   local ne pointe vers une base persistante utilisée ailleurs.
4. Pour chaque exercice, enregistrer dans le rapport : date UTC, commit,
   version Python et dépendances, système/CPU/RAM disponibles, commandes,
   résultats bruts utiles, durée, écarts et verdict.
5. Ne jamais inclure de secrets, contenus personnels ou identifiants d'un
   déploiement dans les résultats commités.

En cas d'échec d'intégrité, de destination non isolée ou de doute sur un chemin,
arrêter l'exercice. Conserver les diagnostics expurgés et corriger la procédure
avant de recommencer; ne pas contourner un refus fail-closed.

## Calendrier proposé

Le calendrier est indicatif et peut être réalisé en quelques sessions réparties
sur le mois. Une étape ne commence que lorsque ses prérequis sont vérifiés.

| Période | Étape | Livrable |
|---|---|---|
| Semaine 1 | Baseline, limites et analyse du flux de refus | Matrice initiale, contrat de refus et cas de tests convenus |
| Semaine 2 | Implémentation et tests de réconciliation du refus | Changement ciblé, tests de reprise/idempotence, suite concernée verte |
| Semaine 3 | Pannes worker, inventaire et répétition de restauration isolée | Résultats des scénarios, contrôles d'intégrité et durées |
| Semaine 4 | Benchmark local, synthèse et décision de sortie | Rapport de campagne, limites, tâches reportées et critères de reprise |

## Étape 0 — Baseline et environnement sûr

### Actions

1. Noter le commit de départ, la version du paquet, la version Python, le
   système, l'architecture et les ressources disponibles.
2. Exécuter les tests pertinents sans modifier les fichiers de données
   persistants : approbation, worker/outbox, inventaire, sauvegarde et
   benchmark.
3. Relever les points d'entrée du cycle d'approbation : création de proposition,
   décision d'approbation/refus, transitions d'épisode, écriture du ledger,
   émission/acquittement de l'outbox et reprise après erreur.
4. Établir une carte courte des états et événements déjà utilisés par le code;
   conserver les noms du modèle existant au lieu d'ajouter une deuxième
   terminologie métier.
5. Préparer un répertoire temporaire réservé aux tests et vérifier avant
   chaque commande que la source et la destination sont bien sous ce répertoire.

### Critères de sortie

- La baseline est enregistrée avec le commit et les commandes réellement
  exécutées.
- Aucune donnée de production n'est requise.
- Le flux de refus existant et les endroits où l'épisode original est écrit sont
  identifiés avant toute modification.

## Étape 1 — Réconcilier un refus dans l'épisode original

### Objectif fonctionnel

Lorsqu'une demande d'approbation est refusée, le refus doit produire un état
terminal cohérent dans le dépôt d'approbation et une preuve append-only liée à
l'épisode d'orchestration d'origine. Un refus ne doit jamais être interprété
comme une approbation, ne doit pas appeler l'exécuteur et ne doit pas provoquer
une action externe. Les noms exacts des états et événements doivent respecter
les contrats et transitions déjà présents dans le dépôt.

### Actions de réalisation

1. Lire le modèle de décision, le stockage d'approbation, le ledger et la
   machine à états de l'épisode; identifier leur frontière transactionnelle et
   les erreurs possibles entre chaque écriture.
2. Écrire le contrat attendu avant l'implémentation :
   - l'identité/décision du refus est validée selon les règles existantes;
   - une demande déjà refusée ne peut pas être approuvée ensuite;
   - une demande déjà approuvée ne peut pas être refusée ensuite par rejeu;
   - la preuve référence sans ambiguïté l'identifiant de demande, son digest et
     l'épisode source;
   - l'épisode source reste l'épisode d'origine; ne pas créer un nouvel épisode
     artificiel pour le refus;
   - l'épisode passe à l'état terminal de refus prévu par la machine à états
     existante;
   - aucune simulation ni exécution d'action n'est appelée sur le chemin refusé.
3. Implémenter la réconciliation en conservant les écritures append-only et les
   transactions existantes. Rendre la répétition sûre si le processus s'arrête
   après l'ajout de preuve mais avant l'acquittement de la tâche.
4. Rendre visibles les erreurs de persistance/réconciliation : ne pas marquer
   le travail comme réussi si la preuve de refus manque, et laisser le mécanisme
   de reprise existant retenter sans produire de preuve contradictoire.
5. Exposer un résultat vérifiable par les interfaces internes existantes, sans
   ajouter une intégration Slack ni un faux statut de notification envoyée.

### Tests requis

- Refus valide enregistré une fois dans l'approbation et dans l'épisode source.
- Vérification de la chaîne/signature du ledger après le refus.
- Même décision rejouée : résultat idempotent, aucune deuxième transition
  contradictoire ni preuve dupliquée.
- Tentative d'approbation après refus et tentative de refus après approbation :
  refusées selon les règles métier.
- Mauvais identifiant d'épisode, digest invalide, demande inexistante ou état
  non autorisé : aucun acquittement de succès, aucune action.
- Injection d'échec entre décision, append au ledger et acquittement; redémarrage
  et nouvelle tentative aboutissent à un état final cohérent.
- Espion/test double d'exécuteur : zéro appel pour tout chemin de refus.

### Critères de sortie

- Le refus et son episode source peuvent être reliés sans ambiguïté.
- Les tests couvrent le rejeu et les interruptions entre persistances.
- Aucune action n'a été exécutée; les tests prouvent zéro appel à l'exécuteur.
- L'état refusé et ses preuves peuvent être relus après fermeture/réouverture
  des stores.

## Étape 2 — Exercices déterministes de panne du worker

### Objectif

Confirmer la reprise de la file durable à chaque frontière critique, et préciser
la garantie **au moins une fois** : la livraison peut être répétée; l'effet
externe n'est pas « exactement une fois » sans idempotence/réconciliation du
consommateur.

### Matrice des scénarios

| Scénario | Injection isolée | Vérification attendue |
|---|---|---|
| Avant prise en charge | Ajouter un événement puis arrêter le worker avant claim | L'événement reste en attente et est traité après redémarrage |
| Après claim, avant handler | Arrêter le processus après attribution du bail | Le bail expire, un nouveau worker reprend, aucun événement ne disparaît |
| Pendant le traitement | Lever une erreur contrôlée dans un handler synthétique | Tentative/erreur visibles; la politique de retry ou de terminal failure est appliquée |
| Après effet simulé, avant ACK | Enregistrer un effet synthétique idempotent par `tracking_id`, puis interrompre avant ACK | Le message est repris; une seule entrée d'effet logique et un état final cohérent |
| Bail expiré et worker retardataire | Faire expirer le bail, faire reprendre par un deuxième worker, puis terminer l'ancien | L'ancien propriétaire ne peut pas acquitter/écraser le résultat du nouveau |
| Rejeu du même événement | Réinjecter le même événement et son identifiant sémantique | Pas de deuxième épisode logique ni de perte de la relation de tracking |

### Procédure

1. Employer uniquement la base/outbox temporaire, un handler synthétique et
   des délais courts explicitement réglés pour les tests.
2. Pour chaque cas, consigner l'état avant l'arrêt, la façon dont l'interruption
   est provoquée, la durée du bail, le nombre de tentatives et l'état final.
3. Répéter les scénarios de frontière au moins trois fois pour détecter une
   dépendance au timing; garder les tests automatisés déterministes, sans sleep
   fragile si l'horloge ou les points d'injection du dépôt permettent de faire
   autrement.
4. Pour l'arrêt brutal de processus, démarrer un processus enfant explicitement
   associé au test et le terminer par son PID connu. Ne jamais tuer des
   processus non identifiés ni viser un worker partagé.
5. Vérifier les événements terminaux, les métriques de retry, les épisodes
   référencés et les erreurs; ne pas conclure à partir du seul code de sortie du
   processus.

### Critères de sortie

- Chaque événement demeure traçable d'une acceptation à un état final explicite.
- Aucun worker avec un bail périmé ne peut écraser le détenteur courant.
- L'effet de test est unique logiquement pour le même `tracking_id` malgré la
  répétition de livraison.
- Les limites « local, SQLite, mono-instance, au moins une fois » figurent dans
  le compte-rendu.

## Étape 3 — Cycle de vie de l'inventaire local

### Scénarios

1. Inventaire configuré absent : la décision échoue fermé; aucun fallback en
   inventaire implicite.
2. Fichier mal formé, schéma invalide ou clé dupliquée : erreur explicite;
   aucune cible n'est autorisée.
3. `generatedAt` dépassé au-delà de `maxAgeSeconds` : cible refusée.
4. Changement de contenu pendant que le processus tourne : le hash/détection
   de modification invalide l'état chargé conformément au comportement actuel.
5. Redémarrage avec nouveau fichier valide : seule la version valide rechargée
   est appliquée; enregistrer son hash et sa fenêtre de validité.
6. Cible inconnue, nom proche, casse différente ou alias non autorisé : refus.
7. Inventaire revenu à une version précédente ou date future : vérifier que la
   politique de fraîcheur ne l'accepte pas silencieusement.

### Procédure et preuves

- Utiliser une horloge/fichiers temporaires contrôlés et des noms de cibles
  synthétiques.
- Vérifier la décision et le motif précis, pas seulement qu'une exception est
  levée.
- Vérifier que le refus concerne à la fois la requête de politique et le chemin
  d'alerte/worker pertinent.
- Enregistrer le hash de l'inventaire de chaque scénario; ne commiter ni
  inventaire de client ni liste de cibles réelles.

### Critères de sortie

- Tous les scénarios négatifs échouent fermé et les cas valides n'acceptent que
  les entrées exactes et fraîches.
- Le changement de version d'inventaire nécessite le mécanisme de reload ou de
  redémarrage prévu; aucun processus ne conserve silencieusement un fichier
  modifié comme valide.
- Les tests ne suggèrent pas qu'un inventaire local manuel détecte le drift de
  l'infrastructure source.

## Étape 4 — Répétition locale de sauvegarde et restauration

### Objectif et précaution d'interprétation

Répéter `backup-set`, `verify-set` et `restore-set` avec des données
synthétiques, mesurer les durées et vérifier les objets métier et preuves.
Une copie vers un deuxième répertoire ou disque accessible sur le même poste
est seulement un test de copie/lecture; **ce n'est pas une répétition off-host**
et elle ne valide pas la perte de machine ou de volume.

### Procédure

1. Créer un jeu neuf sous un répertoire temporaire unique, avec les bases
   synthétiques des alertes, approbations et quotas ainsi qu'un répertoire de
   preuves signé par une clé de test persistante durant tout l'exercice.
2. Insérer des cas témoins identifiables (une alerte complète, une demande
   approuvée simulée, un refus après l'étape 1 si celle-ci est terminée, et des
   preuves ledger valides). Noter les comptes et identifiants, sans secret.
3. Arrêter/quiescer tous les writers du jeu. Consigner l'heure du dernier
   événement inclus; ne pas copier un fichier SQLite actif ou seulement son
   fichier principal en ignorant WAL.
4. Exécuter `backup-set` avec un manifeste et une destination neuve; mesurer la
   durée totale et la taille du jeu.
5. Exécuter `verify-set` sur l'original sauvegardé. Vérifier manifeste, hash de
   tous les fichiers, `integrity_check` de chaque base et chaîne d'évidence.
6. Copier le jeu vérifié vers un second emplacement temporaire, refaire
   `verify-set`, puis restaurer vers un nouveau dossier vide séparé.
7. Sur la restauration, comparer les comptes, identifiants témoins, relations
   épisode/approbation, derniers événements ledger et chaîne de signature.
8. Chronométrer séparément quiescence, sauvegarde, copie, vérification et
   restauration; mesurer le délai du dernier enregistrement témoin au point de
   sauvegarde.
9. Tester négativement une copie de sauvegarde volontairement altérée dans une
   copie jetable : `verify-set`/`restore-set` doit refuser la corruption.
   Préserver l'original non altéré.
10. Après les contrôles, archiver uniquement un rapport expurgé et supprimer
    seulement les répertoires temporaires nommément identifiés et confirmés.

### Mesures à rapporter

- Durée/volume du jeu de sauvegarde, de vérification, de copie locale et de
  restauration.
- Nombre d'enregistrements témoins récupérés et résultat d'intégrité de chaque
  base/ledger.
- Heure du dernier événement témoin et point de sauvegarde obtenu.
- Temps de restauration local observé; écrire **RTO local mesuré** seulement
  pour ce protocole contrôlé, pas pour Render ou la production.
- Écrire **RPO de l'exercice synthétique** seulement si le rythme d'écriture et
  le point de coupure ont été explicitement instrumentés. Sinon marquer RPO
  « non mesuré ».
- Indiquer que la copie locale ne mesure ni transfert distant, ni disponibilité
  du stockage off-host, ni perte de l'hôte source.

### Critères de sortie

- Backup, vérification, copie locale et restauration s'achèvent sans écraser une
  destination existante.
- L'intégrité DB et ledger est vérifiée avant et après restauration.
- Les données témoins sont retrouvées; la sauvegarde corrompue est rejetée.
- Toutes les durées sont annotées avec leurs limites; aucun RPO/RTO externe
  n'est revendiqué.

## Étape 5 — Mesure locale de charge et reprise

### Protocole

1. Fixer commit, version de Python, OS, CPU, RAM, paramètres worker et
   répertoire de stockage; exécuter une série de chauffe exclue des résultats.
2. Mesurer les tailles `100,500,1000` avec `agentic-ops-benchmark-alerts`.
   Augmenter à `5000` seulement si les premières mesures montrent une marge
   mémoire/espace suffisante et si la machine reste utilisable. Stopper si la
   consommation ou la latence dégrade l'environnement partagé.
3. Répéter chaque taille trois fois. Garder chaque mesure séparée et rapporter
   médiane et plage observée; ne pas mélanger les runs ni supprimer un échec
   sans explication.
4. Consigner ingestion/s, traitement/s, p50/p95/max, taille SQLite, nombre de
   records terminaux et délai crash contrôlé → reprise après bail.
5. Tester les seuils configurables du benchmark : seuil volontairement
   atteignable donnant succès, puis seuil volontairement impossible donnant
   échec. Les valeurs ne sont pas des seuils de production.
6. Si la capacité est sûre, observer la tendance en augmentant la taille; ne
   pas pousser jusqu'à saturer le disque ou bloquer d'autres services.
7. Comparer aux références locales historiques avec leur contexte matériel.
   Signaler toute différence de machine, runtime, commit ou profil; une
   comparaison entre machines n'est pas un SLO.

### Critères de sortie

- JSON complet est conservé localement pour analyse et le résumé expurgé
  comporte les paramètres de l'essai.
- Chaque taille aboutit à un compte terminal explicable; les tests de seuil
  contrôlent le code de sortie attendu.
- Les résultats ne sont pas extrapolés à Grafana, Render, un cluster,
  plusieurs workers, une panne de volume ou un appel LLM.
- Toute mesure instable est présentée comme plage/limite et non comme garantie.

## Étape 6 — Synthèse et décision de suite

Produire un compte-rendu daté sous `docs/` ou joindre la synthèse à une mise à
jour de ce plan, selon les résultats. Le compte-rendu doit contenir :

1. Commit et état des tests avant/après.
2. Résultat de chaque étape avec verdict `réussi`, `partiel`, `échoué` ou `non
   exécuté`; ne pas masquer un cas bloqué.
3. Commandes, versions, environnement et mesures, sans données sensibles.
4. Pour refus : preuve d'état terminal, intégrité du ledger, comportement de
   rejeu et zéro appel à l'exécuteur.
5. Pour worker/inventaire : matrice de scénario, nombre de répétitions,
   résultats et motifs de refus.
6. Pour restauration/benchmark : métriques brutes utiles, méthode, périmètre et
   limites d'extrapolation.
7. Liste séparée des travaux hors scope : restauration véritable depuis
   stockage distant, perte de machine/volume, RPO/RTO de Render, livraison Slack,
   identité indépendante, qualification de la cible et exécution mutatrice.
8. Décision explicite : travaux terminés dans le scope, défauts ouverts,
   prochaine action et prérequis externes. La décision de poursuivre ne doit pas
   activer le mode live.

## Matrice de sortie de campagne

| Domaine | Preuve minimale pour dire « fait dans le scope local » | Ce que cela ne prouve pas |
|---|---|---|
| Refus d'approbation | Tests d'état terminal, ledger append-only, idempotence, reprise et zéro exécution | Livraison Slack, identité indépendante, refus dans un déploiement réel |
| Panne du worker | Matrice d'interruptions isolées répétée et reprise traçable | Disponibilité d'un hôte/pod, stockage partagé, absence générale de doublon externe |
| Inventaire | Tests absent/périmé/modifié/invalide/inconnu et rechargement sûr | Fraîcheur d'un inventaire synchronisé à une vraie plateforme |
| Backup/restore | Backup-set vérifié, copie locale distincte, restauration isolée et contrôles de données/ledger | Résilience off-host, perte d'hôte, sauvegarde planifiée, RPO/RTO Render |
| Charge/reprise | Runs répétables avec environnement et sorties enregistrés | SLO, capacité en production, disponibilité ou autoscaling |

## Dépendances à ouvrir dans une campagne séparée

- **Stockage off-host réel :** choisir/avoir accès à une destination déjà
  approuvée, vérifier les droits, chiffrement, rétention et restauration depuis
  cette destination. Sans ce support, reporter; ne pas maquiller la copie locale.
- **Render ou autre déploiement :** fenêtre autorisée, accès aux logs/stockage,
  sauvegardes disponibles et opérateur capable d'approuver les actions. Aucun
  essai de perte de volume ou redéploiement dans ce plan.
- **Slack :** app, espace de test, secrets injectés hors dépôt et destinataire
  consentant; sans cela, conserver les tests de contrat seulement.
- **Identité indépendante :** fournisseur et comptes test; une clé locale ou une
  liste statique n'est pas une identité indépendante.

## Reprise après report

Si une étape n'est pas possible en novembre, enregistrer son statut comme
`non exécuté` avec le blocage et le prérequis précis. Ne pas la marquer
`réussie` sur la base des tests CI existants. Reprendre uniquement l'étape
bloquée et ses dépendances, puis mettre à jour le compte-rendu et le statut
technique.
