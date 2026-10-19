# Publication de l'image sur GitHub Container Registry

L'image de ce dépôt est destinée à GitHub Container Registry (GHCR), sous
`ghcr.io/nolll77/agentic-ops`. La publication de l'image est indépendante de
la publication du paquet Python sur PyPI.

## Contenu et vérifications de sécurité

Le `.dockerignore` exclut notamment les bases SQLite, journaux, états locaux,
fichiers d'environnement, clés privées, rapports, documentation et tests du
contexte de build. Le Dockerfile ne copie que les fichiers applicatifs requis.
Les bases d'exécution sont initialisées dans `/tmp/state`; les données locales
du poste ne sont pas copiées dans l'image. Les fichiers de l'application sont
possédés par `root` et ne sont pas modifiables par l'utilisateur non privilégié
du conteneur.

Ces mesures réduisent le risque d'inclure des données privées ou des secrets;
elles ne constituent pas une certification exhaustive du contenu du code ou
des preuves d'exemple suivies par Git. Examiner les contenus embarqués avant
toute publication publique.

## Publication automatique par GitHub Actions

Le workflow `.github/workflows/publish-container.yml` construit des images
`linux/amd64` et `linux/arm64` quand une release GitHub est publiée. Il utilise
`GITHUB_TOKEN` avec `packages: write`; aucun mot de passe Docker Hub ni PAT
n'est requis.

1. Pousser ce workflow dans la branche par défaut du dépôt GitHub.
2. Dans **Actions > Publish container image > Run workflow**, choisir la
   branche par défaut et fournir le tag `v0.1.3`; ou publier une release
   GitHub associée au tag `v0.1.3`. L'une ou l'autre méthode lance la
   construction multi-architecture et l'envoi de l'image. Une exécution
   manuelle n'ajoute pas le tag `latest`.
3. Dans GitHub, ouvrir le package `agentic-ops` sous **Packages** et, si
   l'image doit être téléchargeable anonymement, régler sa visibilité à
   **Public**. GHCR peut créer le package en privé lors du premier push; la
   visibilité publique doit être activée explicitement par un propriétaire.
4. Consulter le workflow et vérifier le tag ainsi que les architectures
   publiées. Le chart Helm utilise `ghcr.io/nolll77/agentic-ops:v0.1.3`.

La release PyPI est un workflow distinct; publier une version PyPI ne lance pas
la publication du conteneur.

## Publication manuelle locale (facultative)

Pour publier depuis un poste, créer un Personal Access Token GitHub Classic
avec `write:packages`, puis saisir le token à l'invite de `docker login`. Ne
mettre dans une commande, un fichier suivi par Git ou un message.

```sh
docker login ghcr.io -u nolll77
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --tag ghcr.io/nolll77/agentic-ops:v0.1.3 \
  --push .
```

Pour la première publication, régler le package à **Public** dans les
paramètres GitHub Packages si des téléchargements anonymes sont souhaités. La
publication d'une image ne qualifie pas un cluster distant et ne rend pas
l'état du conteneur persistant par elle-même.
