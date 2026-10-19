# Dépannage Console et Chat sur Render

## Diagnostic du `503` observé

Les actions de la Console et la sonde LLM du panneau Chat appellent des routes
protégées par `AdminAPIKeyMiddleware` :

- `GET /api/diagnostics/{command}`
- `POST /api/llm/probe`

Sans `ADMIN_API_KEY` (ou configuration Entra complète), le middleware répond
volontairement `503 administrative authentication is not configured`. Il ne
faut pas supprimer cette protection ni rendre les routes de diagnostic
publiques : plusieurs d'entre elles exécutent des commandes ou des tests dans
le conteneur.

Au contrôle du service Render, `/api/llm/status` indiquait qu'une clé de
fournisseur LLM était configurée, tandis que les routes protégées renvoyaient
le `503` ci-dessus. Le message de la sonde qui demandait de vérifier
`OPENROUTER_API_KEY` était donc trompeur pour ce cas : le refus se produisait
avant l'appel au fournisseur LLM.

## Configuration requise sur Render

1. Dans le tableau de bord Render, ouvrir le service web Agentic-Ops puis
   **Environment**.
2. Ajouter `ADMIN_API_KEY` comme variable secrète, avec une valeur aléatoire
   d'au moins 32 caractères. Ne pas la mettre dans Git, un Dockerfile, une
   commande, un ticket ou une conversation.
3. Enregistrer les changements et attendre le redéploiement/redémarrage du
   service.
4. Recharger `/console` ou `/chat`. Lorsqu'une route protégée renvoie `401`,
   l'interface demande la clé; elle l'envoie comme `X-API-Key` et la garde
   uniquement en mémoire dans l'onglet courant. Un rechargement de page
   l'efface.
5. Lancer une seule action de diagnostic puis vérifier que la réponse n'est
   plus `401`/`503`. N'exécuter les commandes de test de charge que lorsque
   leur coût CPU sur le service Render est acceptable.

La variable `ADMIN_API_KEY_PREVIOUS` peut servir à une rotation à deux clés;
retirer l'ancienne après vérification des clients. Si Entra est configuré,
`ENTRA_TENANT_ID` et `ENTRA_API_AUDIENCE` doivent l'être ensemble et les
clients doivent fournir un jeton portant le rôle requis.

## Distinguer l'authentification de la disponibilité du Chat

`POST /api/chat` est distinct de `POST /api/llm/probe` et n'est pas protégé
par le middleware administratif. La sonde LLM du panneau MAS est protégée;
son `503` ne prouve donc pas que la conversation elle-même soit en panne.
`OPENROUTER_API_KEY` configure le fournisseur LLM, tandis que
`ADMIN_API_KEY` protège les opérations d'administration. Vérifier
`GET /api/llm/status` pour le fournisseur et traiter séparément les erreurs
retournées par `POST /api/chat`.

La publication d'une version sur GitHub, PyPI et GHCR ne modifie pas le service
Render ni ses variables. Lors du diagnostic du 2026-10-19, son
`GET /openapi.json` déclarait encore `info.version=0.1.3`, alors que `v0.1.5`
était publiée. Il faut donc déclencher le déploiement dans le tableau de bord
Render : déployer le commit `3e4261b` si le service suit le dépôt Git, ou
sélectionner `ghcr.io/nolll77/agentic-ops:v0.1.5` si le service utilise une
image de conteneur. Ajouter `ADMIN_API_KEY` avant le redémarrage, puis vérifier
que `/openapi.json` annonce `0.1.5` et qu'une route protégée n'émet plus ce
`503`. Aucun secret Render ne doit être transmis pour publier les paquets.
