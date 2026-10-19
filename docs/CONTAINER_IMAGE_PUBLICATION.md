# Publication de l'image sur GitHub Container Registry

L'image de ce dépôt est destinée à GitHub Container Registry (GHCR), sous
`ghcr.io/nolll77/agentic-ops`. Le workflow de release publie aussi le paquet
Python sur PyPI; les deux artefacts restent des distributions distinctes.

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

## Publication coordonnée par GitHub Actions

Le workflow `.github/workflows/publish.yml` publie PyPI et GHCR dans la même
chaîne de release. Il installe le projet et exécute la suite de tests, vérifie
les versions puis construit les distributions Python à partir du tag. Après
publication sur PyPI, et **seulement si cette étape réussit**, il construit et
publie l'image `linux/amd64` et `linux/arm64` sur GHCR à partir du même tag
source. Il utilise `GITHUB_TOKEN` avec `packages: write`; aucun mot de passe
Docker Hub ni PAT n'est requis.

1. Mettre à jour `project.version` dans `pyproject.toml` et `version` /
   `appVersion` dans le chart Helm à `X.Y.Z`, ainsi que `image.tag` dans
   `helm/agentic-ops/values.yaml` à `vX.Y.Z`. Pousser et vérifier les
   changements sur `main`.
2. Créer un tag/release GitHub `vX.Y.Z` correspondant exactement à la version
   du paquet, par exemple `pyproject.toml` version `0.1.5` et tag `v0.1.5`.
   La publication de la release démarre la chaîne. Un tag seul sans release
   publiée ne la démarre pas.
3. Le workflow vérifie que le tag sémantique correspond à `pyproject.toml` et
   aux versions/tag configurés dans le chart Helm, construit et publie le
   paquet PyPI, puis publie les images GHCR taguée `vX.Y.Z` et `latest`. Si
   PyPI échoue, GHCR ne publie pas.
4. Dans GitHub, ouvrir le package `agentic-ops` sous **Packages** et, si
   l'image doit être téléchargeable anonymement, régler sa visibilité à
   **Public**. GHCR peut créer le package en privé lors du premier push; la
   visibilité publique doit être activée explicitement par un propriétaire.
5. Consulter le workflow et vérifier le tag ainsi que les architectures
   publiées. Pour la candidate en préparation, le chart Helm vise
   `ghcr.io/nolll77/agentic-ops:v0.1.5`.

La publication n'est pas une transaction atomique entre deux registres : si
PyPI réussit et GHCR échoue, PyPI reste publié. Depuis l'exécution GitHub
Actions, utiliser **Re-run failed jobs** pour retenter le job GHCR sans tenter
de publier une seconde fois la même version PyPI.

Cette chaîne publie des artefacts, mais ne déploie pas automatiquement sur un
cluster Kubernetes. Un déploiement GitOps/Helm et son approbation restent une
opération distincte.

Le Dockerfile installe le projet depuis le checkout de la release avec
`uv pip install -e .`; il ne télécharge pas le paquet depuis PyPI. Les deux
artefacts sont donc construits depuis le même commit/tag, plutôt que de
reconstruire l'image à partir d'un téléchargement PyPI.

L'environnement GitHub `pypi` doit rester configuré comme Trusted Publisher
PyPI pour le workflow `publish.yml`. Le compte doit également autoriser ce
workflow à publier des packages sur GHCR.

## Publication réalisée

Le 2026-10-19, avant la coordination des workflows, l'ancien workflow GHCR a publié
`ghcr.io/nolll77/agentic-ops:v0.1.3` (run
[39246908384](https://github.com/nolll77/agentic-ops/actions/runs/39246908384)).
Le manifeste OCI, lisible sans authentification, référence `linux/amd64` et
`linux/arm64`; son digest est
`sha256:05a2f876cbe7d70bc60791e64660ad3ac427bf7a3e9cd39e7cfe6841b08ddc3a`.

La release `v0.1.4` ajoute l'inventaire local exact/frais, les
outils de snapshot SQLite et le benchmark synthétique décrits dans
[`INDUSTRIAL_PRODUCTION_BLUEPRINT.md`](./INDUSTRIAL_PRODUCTION_BLUEPRINT.md).
Les jobs de build, PyPI et GHCR ont réussi dans le
[run de publication `39254442273`](https://github.com/nolll77/agentic-ops/actions/runs/39254442273).
La candidate `v0.1.5` corrige l'interface d'authentification de la console et
des sondes LLM; elle ne provisionne pas les secrets Render.

## Publication manuelle locale (exception)

Cette procédure contourne la chaîne séquentielle PyPI → GHCR et ne doit être
utilisée que pour un cas exceptionnel. Pour publier depuis un poste, créer un
Personal Access Token GitHub Classic
avec `write:packages`, puis saisir le token à l'invite de `docker login`. Ne
mettre dans une commande, un fichier suivi par Git ou un message.

```sh
docker login ghcr.io -u nolll77
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --tag ghcr.io/nolll77/agentic-ops:v0.1.5 \
  --push .
```

Pour la première publication, régler le package à **Public** dans les
paramètres GitHub Packages si des téléchargements anonymes sont souhaités. La
publication d'une image ne qualifie pas un cluster distant et ne rend pas
l'état du conteneur persistant par elle-même.
