# 🧩 Annexes : Débats Conceptuels & Paradoxes MLOps Sous-jacents — v1

> [!IMPORTANT]
> **RÈGLE D'OR ABSOLUE — JAMAIS D'ÉCRASEMENT**
> Ce document est une **source vivante en append-only**. Chaque ingestion d'une nouvelle Catégorie dans `bible_ontologie_3.md` génère un ou plusieurs paradoxes à ajouter ici, à la suite des entrées existantes. Interdiction formelle d'utiliser `open(..., 'w')` sur ce fichier.

---

## Rôle de ce Document

Ce document capture les **paradoxes architecturaux et débats conceptuels MLOps profonds** qui se cachent derrière chaque catégorie de l'Ontologie. Il complète la `bible_ontologie_3.md` en portant la dimension méta : pourquoi chaque défaillance technique révèle une tension fondamentale de l'ingénierie ML.

**Principe fondateur (Règle 10 du Manifeste 2) :** Derrière chaque décision technique se cache un paradoxe d'architecture MLOps profond. Il est formellement interdit de considérer une catégorie comme "purement technique et sans débat".

---

## Documents Connexes

| Document | Rôle |
|---|---|
| [`bible_ontologie_3.md`](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/bible_ontologie_3.md) | Source primaire — catégories verbatim |
| [`mlops_failure_modes_taxonomy_3.md`](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy_3.md) | Matrice opérationnelle des risques |
| [`bi_observability_2.md`](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/bi_observability_2.md) | Dashboards & alertes |

---

## Format Obligatoire d'une Entrée de Paradoxe

> [!CAUTION]
> **Format du numéro : `### N. Paradoxe : [Titre] (Cat. X.Y)` — GRAVÉ EN DUR.**
> Ne jamais utiliser `1.`, `2.`, `3.` (liste Markdown auto-numérotée). Cette syntaxe se réinitialise à chaque bloc lors des appends successifs et produit des numéros incohérents. Le numéro est un entier fixe écrit directement dans le titre `###`.

```markdown
### 28. Paradoxe : [Titre du paradoxe] (Cat. X.Y)

**Panne technique de référence :** `ID-XXX` — Nom de la panne dans la matrice
**Catégorie Ontologique :** CATÉGORIE X (== PlanMaitre : Y)

**Le Paradoxe :**
Description du paradoxe de fond sous-jacent non débattu, en 2-5 phrases.

**La Tension Architecturale :**
Deux forces opposées qui créent le paradoxe (ex: Reproductibilité vs Performance).

**Mise en Conscience Requise :**
Ce que l'architecte MLOps doit internaliser pour éviter de tomber dans ce piège.
```

---

## Index des Paradoxes

| N° | Titre | Cat. Onto | Panne Réf. |
|---|---|---|---|
| *Aucun paradoxe documenté pour l'instant* | — | — | — |

*Dernier comptage : **0 paradoxes documentés***

---

## Paradoxes

> *Ce document est vide à ce stade. Les paradoxes seront ajoutés ici au fil des ingestions de catégories dans `bible_ontologie_3.md`.*

<!-- DÉBUT DES PARADOXES — NE PAS MODIFIER CETTE LIGNE -->

### 1. Paradoxe : L'Alert Fatigue vs Le Silence Critique (Cat. 8)

**Panne technique de référence :** `OBS-004` — Alert Fatigue
**Catégorie Ontologique :** CATÉGORIE 8 (== PlanMaitre : 8)

**Le Paradoxe :**
Pour ne rien rater, on alerte sur tout. Mais alerter sur tout conduit à ignorer les alertes, créant ainsi le risque même qu'on essayait d'éviter.

**La Tension Architecturale :**
Sensibilité (ne rater aucun vrai positif) vs Spécificité (ne pas spammer l'équipe).

**Mise en Conscience Requise :**
L'architecte MLOps doit traiter les alertes comme un budget cognitif limité, et implémenter du routage intelligent (Sévérité, Canal).

### 2. Paradoxe : Le Rollback Silencieux (Cat. 3.2)

**Panne technique de référence :** `GOV-001` — Demande de rollback V2 vers V1
**Catégorie Ontologique :** CATÉGORIE 3 (== PlanMaitre : 3)

**Le Paradoxe :**
En ingénierie logicielle, un rollback est un `git checkout`. En ML, un rollback nécessite de retrouver le code, la donnée, les hyperparamètres et l'environnement exacts.

**La Tension Architecturale :**
Versionnement Code (Git) vs Versionnement État ML (MLflow + DVC).

**Mise en Conscience Requise :**
Sans un ML Metadata Store centralisé, tout modèle déployé est orphelin et irrécupérable en cas de crise.

### 3. Paradoxe : La Reproductibilité Éphémère (Cat. Reproductibilité)

**Le Paradoxe :**
L'écosystème moderne (Docker, Kubernetes) est conçu pour être éphémère et stateless. Pourtant, la compliance ML exige une reproductibilité absolue d'un entraînement survenu il y a 2 ans (dépendances exactes, data exactes, code exact).

**La Tension Architecturale :**
Agilité Éphémère (Ops) vs Traçabilité Perpétuelle (Compliance).

**Mise en Conscience Requise :**
Un conteneur Docker n'est pas une capsule temporelle s'il dépend de paquets PyPI ou de repos GitHub publics qui peuvent être supprimés (Left-pad syndrome).

### 4. Paradoxe : Le Coût Caché du MLOps (FinOps)

**Le Paradoxe :**
Le modèle le plus performant (ex: Transformer massif) peut rendre le projet financièrement non-viable en production (coûts GPU, latence). Optimiser l'Accuracy détruit la rentabilité.

**La Tension Architecturale :**
Performance Prédictive (Data Science) vs ROI (Business).

**Mise en Conscience Requise :**
Le coût d'inférence doit être une métrique de validation au même titre que le F1-Score.
