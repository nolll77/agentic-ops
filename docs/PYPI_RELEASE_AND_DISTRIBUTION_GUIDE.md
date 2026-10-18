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
* **Version Active** : `0.1.0`
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

Le workflow de déploiement continu est défini dans [`.github/workflows/publish.yml`](file:///Users/nolll/Documents/car_acc/agentic-ops-core/.github/workflows/publish.yml) :

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]
  workflow_dispatch:

jobs:
  pypi-publish:
    name: Upload release to PyPI
    runs-on: ubuntu-latest
    environment:
      name: pypi
      url: https://pypi.org/p/agentic-ops
    permissions:
      id-token: write  # Requis pour l'échange de jeton OIDC avec PyPI
      contents: read

    steps:
    - uses: actions/checkout@v4

    - name: Install uv
      uses: astral-sh/setup-uv@v5

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: "3.11"

    - name: Build package
      run: |
        uv build

    - name: Publish package distributions to PyPI
      uses: pypa/gh-action-pypi-publish@release/v1
```

---

## 5. Runbook Opérationnel : Publier une Nouvelle Version

Pour incrémenter et publier une nouvelle version d'`agentic-ops` (ex: `0.1.1` ou `0.2.0`) :

1. **Incrémenter la version dans `pyproject.toml`** :
   ```toml
   [project]
   name = "agentic-ops"
   version = "0.1.1"
   ```

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
   git add pyproject.toml uv.lock
   git commit -m "chore(release): bump version to 0.1.1"
   git push origin main
   ```

5. **Déclencher le déploiement PyPI** :
   * **Option 1 (Automatique via GitHub Release)** : Créer une Release GitHub avec le tag `v0.1.1`.
   * **Option 2 (Manuelle via CLI)** :
     ```bash
     gh workflow run publish.yml
     ```

6. **Vérification post-déploiement** :
   ```bash
   python3 -m pip index versions agentic-ops
   ```

---

## 6. Matrice d'Honnêteté Radicale : Théorie vs. Réalité du Projet

| Dimension | Théorie Idéale MLOps | Réalité de Déploiement `agentic-ops` | Justification SRE & Arbitrage |
| :--- | :--- | :--- | :--- |
| **Authentification PyPI** | OIDC Trusted Publishing certifié sans secret | **100% Conforme** (OIDC GitHub/PyPI actif) | Élimine les failles de fuite de tokens statiques dans GitHub Secrets. |
| **Génération de Build** | Compilation conteneurisée hermétique multi-arch | `uv build` local et runner standard `ubuntu-latest` | Suffisant et ultra-véloce car le package est un wheel pur Python (`none-any`). |
| **Déclenchement Release** | Tag sémantique `vX.Y.Z` déclenchant une pipeline CD | Supporte à la fois `release: [published]` et `workflow_dispatch` | Permet le déploiement sur événement officiel ou à la demande par le mainteneur. |
| **Vérification d'Index** | Monitoring temps réel des miroirs mondiaux pip | Test direct HTTP sur l'API JSON PyPI et commande `pip index` | Retour d'état immédiat sous 30 secondes sans complexité superflue. |
