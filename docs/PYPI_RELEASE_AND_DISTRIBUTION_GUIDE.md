# Guide d'Ingénierie : Distribution PyPI, OIDC Trusted Publishing & Release Engineering

Ce document formalise l'architecture de distribution publique du package `agentic-ops`, la chaîne de sécurité logicielle OIDC (*OpenID Connect Trusted Publishing*) et les runbooks de publication pour les mainteneurs et exploitants.

```text
+--------------------------------------------------------------------------------------------------+
| AGENTIC-OPS — CHAÎNE D'APPROVISIONNEMENT LOGICIELLE & DISTRIBUTION PYPI (OIDC / SLSA)             |
+--------------------------------------------------------------------------------------------------+
|                                                                                                  |
| [Developpeur / Maintainer]                                                                       |
|        │                                                                                         |
|        ├──► 1. Bump version `pyproject.toml`                                                     |
|        ├──► 2. Synchronisation `uv lock`                                                         |
|        └──► 3. Git Tag / Workflow Dispatch (`origin/main`)                                       |
|                    │                                                                             |
|                    ▼                                                                             |
| [GitHub Actions Runner (ubuntu-latest)]                                                          |
|        │                                                                                         |
|        ├──► `actions/checkout@v4`                                                                |
|        ├──► `astral-sh/setup-uv@v5` (Installation ultra-rapide)                                  |
|        ├──► `uv build` ──► Generation des artefacts purs :                                      |
|        │                    ├── `dist/agentic_ops-X.Y.Z.tar.gz` (sdist)                          |
|        │                    └── `dist/agentic_ops-X.Y.Z-py3-none-any.whl` (wheel)                |
|        │                                                                                         |
|        ├──► Demande de JIT Token OIDC (Permission `id-token: write`)                             |
|        │           │                                                                             |
|        │           ▼                                                                             |
|        │    [GitHub OIDC Provider]                                                               |
|        │           │                                                                             |
|        │           ├── JWT éphémère (claims: repo, workflow, environment `pypi`)                 |
|        │           ▼                                                                             |
|        │    [PyPI Trusted Publisher Engine]                                                      |
|        │           │                                                                             |
|        │           ├── Validation cryptographique des claims (sans mot de passe ni API token)    |
|        │           └── Délivrance d'un token PyPI éphémère à portée restreinte (< 15 min)        |
|        │                                                                                         |
|        └──► `pypa/gh-action-pypi-publish@release/v1`                                             |
|                    │                                                                             |
|                    ├── Upload sdist & wheel                                                      |
|                    └── Signature & Attestation numérique SLSA de provenance                     |
|                                                                                                  |
|                    ▼                                                                             |
| [Registre Officiel PyPI : https://pypi.org/project/agentic-ops/]                                 |
|        │                                                                                         |
|        ▼                                                                                         |
| [Utilisateurs Finaux / Clusters MLOps Mondiaux]                                                  |
|        │                                                                                         |
|        ├──► `pip install agentic-ops`                                                            |
|        └──► `agentic-start --port 8000`                                                          |
|                                                                                                  |
+--------------------------------------------------------------------------------------------------+
```

---

## 1. Identité & Disponibilité du Package

* **Nom Officiel** : `agentic-ops`
* **URL du Registre** : [https://pypi.org/project/agentic-ops/](https://pypi.org/project/agentic-ops/)
* **Dernière version publiée** : `0.1.6`
* **Publication** : succès sur PyPI et GHCR via le [workflow `39265132313`](https://github.com/nolll77/agentic-ops/actions/runs/39265132313)
* **Licence** : `MIT`
* **Régistre Simple (Index)** : `https://pypi.org/simple/agentic-ops/`
* **Compatibilité Runtimes** : `Python >= 3.10` (testé et validé unitairement sur 3.10, 3.11, 3.12).
* **Empreinte** : Package agnostique pur Python (`py3-none-any.whl`), sans dépendance binaire compilée C/Rust non-portable.

---

## 2. Modes d'Installation & Consommation

### A. Installation via Gestionnaires de Paquets Standards

Tout utilisateur ou pipeline CI/CD peut installer la distribution officielle :

```bash
# Via pip standard
pip install agentic-ops

# Via uv (recommandé pour les déploiements rapides)
uv pip install agentic-ops

# Via poetry
poetry add agentic-ops
```

### B. Point d'Entrée CLI (Console & Serveur SRE)

Le package enregistre automatiquement l'exécutable système `agentic-ops` et l'alias de démarrage :

```bash
# Lancement de la plateforme complète (FastAPI, Console /console, Chat /chat, MCP /sse)
agentic-start --port 8000 --host 0.0.0.0

# Inspection des vitaux et de l'intégrité du Ledger WORM
agentic-ops audit
```

### C. Importation Modulaire en Bibliothèque Python

```python
from agentic_ops.adapters.llm_provider_registry import LLMProviderRegistry
from agentic_ops.core.orchestrator import Orchestrator
from agentic_ops.core.remediation_agent import RemediationAgent

# Résolution automatique de la topologie multi-LLM par rôle
remediation_adapter = LLMProviderRegistry.build_adapter_for_role("remediation")
orchestrator = Orchestrator(llm=remediation_adapter)
```

---

## 3. Sécurité de la Chaîne d'Approvisionnement (Trusted Publishing / OIDC)

### A. Problématique des Secrets Statiques

Historiquement, la publication de packages Python reposait sur des tokens d'API longue durée stockés dans les variables `ACTIONS_SECRETS` de GitHub. Ces secrets présentaient des risques majeurs :
1. **Fuite accidentelle** lors de l'exécution d'actions tierces ou de modifications de logs.
2. **Absence d'expiration** facilitant l'injection de dépendances corrompues (*Software Supply Chain Attack*).
3. **Périmètre excessif** accordant des droits d'écriture sur l'ensemble des dépôts du compte mainteneur.

### B. Standard OIDC (OpenID Connect)

`agentic-ops` implémente le standard moderne **Trusted Publishing** promu par la *Python Software Foundation* (PSF) :
* Aucun mot de passe ni token statique n'est configuré dans GitHub Secrets.
* Lors de chaque exécution du workflow `.github/workflows/publish.yml`, GitHub Actions génère un jeton cryptographique OIDC signé (`id-token: write`).
* PyPI valide l'empreinte cryptographique émise par GitHub, certifiant que l'appel provient exclusivement :
  * Du dépôt : `nolll77/agentic-ops`
  * Du workflow : `.github/workflows/publish.yml`
  * De l'environnement : `pypi`
* PyPI délivre un token éphémère d'une durée de vie inférieure à 15 minutes, restreint au téléversement de la version courante.
* Des attestations numériques de provenance SLSA (*Supply-chain Levels for Software Artifacts*) sont automatiquement générées et associées à la release.

---

## 4. Spécification du Workflow CI/CD (`publish.yml`)

Le workflow [`.github/workflows/publish.yml`](../.github/workflows/publish.yml)
est déclenché par la publication d'une release GitHub. Il vérifie que le tag
`vX.Y.Z`, `project.version`, `version`/`appVersion` du chart et `image.tag`
correspondent. Il exécute la suite de tests, construit le paquet une seule
fois, le publie sur PyPI via OIDC, puis publie l'image multi-architecture sur
GHCR à partir du même commit/tag. Le job GHCR dépend de la réussite PyPI. Le
Dockerfile installe le code du checkout (`uv pip install -e .`) : il ne
télécharge pas le paquet PyPI pour fabriquer l'image. La publication
d'artefacts ne déploie pas à elle seule le cluster Kubernetes.

---

## 5. Runbook Opérationnel : Publier une Nouvelle Version

Pour incrémenter et publier une nouvelle version d'`agentic-ops` (ex. `0.1.7`) :

1. **Incrémenter la version dans `pyproject.toml` et le chart Helm** :
   ```toml
   [project]
   name = "agentic-ops"
   version = "X.Y.Z"
   ```
   Aligner également `version` et `appVersion` dans `helm/agentic-ops/Chart.yaml`
   sur `X.Y.Z`, et `image.tag` dans `helm/agentic-ops/values.yaml` sur
   `vX.Y.Z`. Le workflow refuse la release si une valeur diverge.

2. **Mettre à jour le fichier de verrouillage** :
   ```bash
   uv lock
   ```

3. **Valider localement le build et la suite de tests** :
   ```bash
   pytest tests/
   uv build
   ```

4. **Commiter et pousser vers GitHub** :
   ```bash
   git add pyproject.toml uv.lock helm/agentic-ops/Chart.yaml helm/agentic-ops/values.yaml
   git commit -m "chore(release): bump version to X.Y.Z"
   git push origin main
   ```

5. **Créer et publier une Release GitHub** avec le tag `vX.Y.Z`. Un tag seul
   ne déclenche pas le workflow. La version doit correspondre exactement à
   `pyproject.toml`.

6. **Vérification post-déploiement** :
   ```bash
   python3 -m pip index versions agentic-ops
   docker buildx imagetools inspect ghcr.io/nolll77/agentic-ops:vX.Y.Z
   ```

Si PyPI réussit mais GHCR échoue, la publication PyPI ne peut pas être annulée.
Utiliser **Re-run failed jobs** dans GitHub Actions pour retenter GHCR sans
republier la version déjà présente sur PyPI.

---

## 6. Matrice d'Honnêteté Radicale : Théorie vs. Réalité du Projet

| Dimension | Théorie Idéale MLOps | Réalité de Déploiement `agentic-ops` | Justification SRE & Arbitrage |
| :--- | :--- | :--- | :--- |
| **Authentification PyPI** | OIDC Trusted Publishing certifié sans secret | **100% Conforme** (OIDC GitHub/PyPI actif) | Élimine les failles de fuite de tokens statiques dans GitHub Secrets. |
| **Génération de Build** | Compilation conteneurisée hermétique multi-arch | `uv build` local et runner standard `ubuntu-latest` | Suffisant et ultra-véloce car le package est un wheel pur Python (`none-any`). |
| **Déclenchement Release** | Tag sémantique `vX.Y.Z` déclenchant une pipeline CD | Release GitHub publiée avec tag correspondant à `project.version` | Un même commit source publie d'abord PyPI, puis GHCR si PyPI réussit. |
| **Vérification d'Index** | Monitoring temps réel des miroirs mondiaux pip | Test direct HTTP sur l'API JSON PyPI et commande `pip index` | Retour d'état immédiat sous 30 secondes sans complexité superflue. |
