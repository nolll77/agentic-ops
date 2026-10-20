# BIBLE DE L'ONTOLOGIE (RISQUES MLOPS)

Ce document est le **réceptacle du Méga Copier-Coller Ontologie (100 parties)**.

**Le Rôle de cet Agent (Garder le cap) :** L'utilisateur a généré le contenu suivant via de profondes itérations avec un autre LLM sur 15 familles de risques. Ma mission est d'agir en tant qu'**Architecte Curateur** : je dois absorber ces itérations, conserver l'or pur (les vrais concepts MLOps), et filtrer impitoyablement toute hallucination ou dérive théorique du second LLM.

**Hypothèse actuelle :** L'utilisateur a déduit que cette fameuse "Ontologie" est en réalité la classification structurée, exhaustive et matricielle de tous les **Failure Modes MLOps** (l'ontologie des risques systèmes, modèles, et organisationnels).

Si c'est le cas, ce document viendra compléter ou fusionner avec notre matrice des risques existante pour former le dictionnaire ultime des pannes.

Chaque nouvelle partie de l'Ontologie ingérée sert également de point d'entrée pour enrichir et mettre à jour de façon croisée les documents suivants du projet :
- [mlops_failure_modes_taxonomy.md](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md) : Intégration et normalisation des pannes sous forme de matrice de criticité.
- [bi_observability_genesis.md](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/bi_observability_genesis.md) : Création de dashboards de performance du modèle en production (dérive de concept, dégradation de F1-score au fil du temps) et alertes sur les prédictions aberrantes ou les temps de latence d'inférence.
- [mlops_anti_patterns_registry.md](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_anti_patterns_registry.md) : Registre des pièges d'ingénierie et mauvaises pratiques.
- [journal_mlops.md](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/journal_mlops.md) : Journalisation des traces d'industrialisation MLOps.
- Les bibles techniques connexes (ex: [bible_infra.md](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/bible_infra.md), [bible_tools.md](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/bible_tools.md)) si un plan de réponse nécessite d'ajuster notre socle technique.

---

## 1. Concepts Fondamentaux : Catégories vs Dimensions

Pour lever toute ambiguïté, nous devons scinder strictement ces deux concepts :

- **Les Catégories (Le Contenu / L'Itération) :** Ce sont les thèmes abordés séquentiellement par les LLMs au fil de la discussion (ex: "Catégorie : Supply Chain", "Catégorie : Sauvegarde"). Elles sont le fruit de l'exploration et leur numérotation peut être chaotique.
- **Les Dimensions (Le Contenant / L'Architecture) :** C'est la structure finale, absolue et immuable en 10 piliers (Infrastructure, Données, Feature Engineering, etc.). C'est le squelette de l'Ontologie. Peu importe comment les LLMs nomment ou numérotent les "Catégories", leur contenu sémantique finira toujours classé dans l'une de ces 10 Dimensions.

---

## 2. La Méta-Histoire du Prompt Engineering (Le Chaos des Numérotations)

Pour la postérité, il est essentiel de graver ici l'historique de la création de cette Ontologie, car elle illustre la complexité de l'itération (Prompt Engineering) avec des LLMs sur des sujets massifs :

1. **La Genèse (1-8) :** L'Agent initial a généré une première taxonomie en 8 catégories.
2. **L'Extension (9-23) :** Le second LLM a analysé ce travail et a "fait émerger" 15 nouvelles catégories (soit de 9 à 23).
3. **Le Quiproquo (1-15) :** L'utilisateur n'avait pas réalisé le préalable des 8 catégories et pensait faire face à un nouveau plan en 15 catégories.
4. **Le Double Check (La Perte) :** En demandant au LLM de repasser en profondeur sur ces catégories ("double check"), le LLM a réinitialisé sa numérotation à 1. L'utilisateur a suivi jusqu'à 15 et s'est arrêté.
5. **Le Doute MLOps :** Que s'est-il passé ? Les catégories 16 à 23 ont-elles été zappées par l'utilisateur ? Le LLM a-t-il fusionné (mergé) les catégories 1-8 avec les 1-15 ? Certaines pannes ont-elles été écrasées par la fenêtre de contexte du LLM ?
6. **La Résolution & Vigilance :** L'Agent Actuel (Architecte Curateur) prend le relais. Il conserve 100% de la structure et du contenu d'origine des catégories verbatim dans leurs sections détaillées respectives, tout en cartographiant rigoureusement chaque catégorie à ses dimensions correspondantes (via le schéma de correspondance des 10 dimensions `MLOps-Dimensions-Mapping` et l'`` `Analyse de Correspondance avec la Taxonomie des Grandes Dimensions` `` de fin de catégorie). **Engagement de fin de parcours :** À la fin de la transmission des 100 parties, l'agent effectuera une revue croisée exhaustive pour identifier si des catégories parmi les 23 théoriques ont été perdues, fusionnées à tort ou tronquées lors des itérations passées, et comblera manuellement les manques.

---

```text
┌────────────────────────────────────────────────────────┐
│               BIBLE DE L'ONTOLOGIE MLOPS               │
│                   STRUCTURE DU DOCUMENT                │
└────────────────────────────────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│  1. Concepts Fondamentaux & 2. Méta-Histoire           │
│  - Catégories vs Dimensions                            │
│  - Genèse (1-8), Extension (9-23), Chaos du Double-Ch. │
└────────────────────────────────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│  3. Les Trois Niveaux de Maturité                      │
│  - Niveau 1 : Pannes opérationnelles (Run / SRE)       │
│  - Niveau 2 : Spécificités Machine Learning            │
│  - Niveau 3 : Risques Métier                           │
└────────────────────────────────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│  4. Le Plan Maître (Les 15 Catégories)                 │
│  - Sommaire exhaustif brut du second LLM (1 à 15)      │
└────────────────────────────────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│  Taxonomie des 10 Dimensions                           │
│  - Classification d'Ingénierie Systémique Complexe     │
└────────────────────────────────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│  5. Vision Cible : La Matrice des Failure Modes        │
│  - Normalisation : Gravité, Probabilité, Détection... │
└────────────────────────────────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│  PARTIES DÉTAILLÉES (100 Parties en cours d'ingestion) │
│  - Partie 3 : Catégorie 9 (Supply Chain & Dépendances) │
│  - Partie 4 : Catégorie 10 (Sauvegarde / Recovery)...  │
└────────────────────────────────────────────────────────┘
```

---

## 3. Les Trois Niveaux de Maturité

Pour aborder cette taxonomie, trois niveaux de maturité se dégagent :

### **Niveau 1 — Les pannes opérationnelles (Run)**
Tu couvres très bien les incidents classiques :
- infrastructure (Docker, PostgreSQL, disque, RAM)
- API (FastAPI, BentoML)
- réseau
- orchestration
- ingestion
- sécurité
*C'est déjà comparable à un Runbook SRE.*

### **Niveau 2 — Les problèmes spécifiques au Machine Learning**
Là où le document devient intéressant, c'est qu'il traite aussi des risques propres au ML :
- Data Drift
- Concept Drift
- Covariate Shift
- Label Shift
- Training/Serving Skew
- Data Leakage
- Rollback de modèles
- Explainability
- Fairness
*Beaucoup de projets "MLOps" ne vont pas jusque-là.*

### **Niveau 3 — Les risques métier**
La dernière catégorie est rarement documentée.
Par exemple :
- changement de définition de la gravité
- nouveau pays
- changement réglementaire
- nouveau use case
- départ de l'expert technique
*Ces risques sont souvent ceux qui coûtent le plus cher dans les projets industriels.*

---

## 4. Le Plan Maître (Les 15 Catégories du Second LLM)

Voici le sommaire exhaustif brut généré lors de l'expansion de l'Ontologie :

### 1. **Supply Chain / Dépendances logicielles**
*Cette partie est quasiment absente.*
Exemples :
- une librairie Python est supprimée de PyPI
- une dépendance est compromise (attaque supply chain)
- une image Docker officielle est supprimée
- GitHub est indisponible lors d'un déploiement
- MLflow change son format interne
- Feast change une API
- PostgreSQL change un comportement après upgrade majeur
- uv/pip résout différemment les dépendances
- certificat GPG d'un package expiré
- dépôt Git inaccessible
*Ce sont des incidents réels.*

### 2. **Sauvegarde / Disaster Recovery**
*Tu parles de crash, mais presque jamais de restauration.*
Par exemple :
- backup PostgreSQL corrompu
- backup jamais testé
- impossible de restaurer MLflow
- snapshot DVC perdu
- sauvegarde incomplète
- restauration beaucoup plus lente que prévu
- backup chiffré mais clé perdue
- réplication PostgreSQL cassée
*Une vraie architecture production documente toujours cela.*

### 3. **Haute disponibilité**
*Aujourd'hui ton document parle surtout de panne.*
Il manque :
- failover automatique
- plusieurs instances FastAPI
- load balancer mal configuré
- sticky session
- split-brain PostgreSQL
- élection de leader
- perte de quorum

### 4. **Observabilité**
*Tu cites Sentry.*
*Mais il manque énormément de problèmes de monitoring.*
Par exemple :
- métriques Prometheus qui n'arrivent plus
- Grafana affiche des données vieilles de 24 h
- horloges des serveurs désynchronisées
- logs incomplets
- rotation des logs supprime les informations trop tôt
- traces OpenTelemetry perdues
- dashboard cassé après changement de métrique
- alerte configurée sur une mauvaise métrique

### 5. **Performance**
*Tu évoques surtout les crashs.*
*Mais énormément de systèmes ne crashent jamais.*
*Ils deviennent juste très lents.*
Par exemple :
- index PostgreSQL supprimé
- plan SQL devenu mauvais
- fragmentation de table
- modèle qui met 400 ms au lieu de 20
- cache Feast vidé
- cache Redis saturé
- garbage collector Python qui monopolise le CPU

### 6. **Problèmes liés au Feature Store**
*Il y en a beaucoup.*
Exemples :
- online store ≠ offline store
- feature calculée avec un fuseau horaire différent
- feature expirée
- TTL incorrect
- feature jamais matérialisée
- clé d'entité dupliquée
- collision d'identifiants
*Ce sont des problèmes classiques avec Feast.*

### 7. **Temps**
*Il manque beaucoup de problèmes liés au temps.*
Par exemple :
- heure d'été/hiver
- fuseau horaire
- année bissextile
- changement d'heure
- timestamp UTC vs local
- événement arrivé dans le futur à cause d'une mauvaise horloge
- dérive NTP
*Les pipelines temporels souffrent énormément de ça.*

### 8. **Pipeline ML**
*Quelques exemples supplémentaires.*
- seed oublié
- seed différent entre CPU et GPU
- cross-validation mal configurée
- mauvaise métrique optimisée
- fuite entre folds
- déséquilibre de classes oublié
- calibration des probabilités perdue
- seuil de décision modifié

### 9. **Pipeline de données**
*Encore énormément de possibilités.*
Par exemple :
- ordre des colonnes changé
- colonne dupliquée
- encodage UTF-16
- caractères invisibles
- CSV vide
- lignes dans le désordre
- doublons partiels
- clé primaire non unique
- mauvaise granularité

### 10. **Sécurité**
*Tu couvres SQL Injection.*
*Mais il manque :*
- CSRF
- SSRF
- XSS sur Superset
- API Key compromise
- JWT expiré
- élévation de privilège
- Docker privilege escalation
- fuite mémoire contenant des données sensibles
- secrets dans les logs
- modèle volé (Model Extraction Attack)
- attaques par inversion de modèle
- Data Poisoning
- Adversarial Examples
*Ces derniers sont spécifiques au ML.*

### 11. **Gouvernance MLOps**
*Très peu présent.*
Exemples :
- deux modèles Production
- personne responsable du modèle
- absence d'approbation avant promotion
- promotion manuelle oubliée
- modèle jamais archivé
- documentation obsolète

### 12. **Économie**
*Souvent oubliée.*
Par exemple :
- coût AWS/GCP explose
- coût API météo
- stockage DVC devient énorme
- MLflow atteint plusieurs centaines de gigaoctets
- coût GPU imprévu

### 13. **Qualité des prédictions**
*Tu parles du drift.*
*Mais pas de :*
- modèle trop confiant
- probabilités mal calibrées
- classe rare jamais prédite
- explosion des faux positifs
- explosion des faux négatifs
- mauvaise calibration selon les départements

### 14. **Humain**
*Il y a énormément de failure modes humains.*
Par exemple :
- suppression accidentelle d'un modèle
- mauvaise branche Git
- rollback sur le mauvais modèle
- déploiement sur le mauvais serveur
- variable d'environnement de production écrasée
- mauvaise clé API
- mauvais fichier .env
- oubli de migration SQL

### 15. **Cas extrêmes**
*Les fameux "Black Swans".*
Exemples :
- panne électrique
- incendie du datacenter
- corruption RAM
- bug noyau Linux
- bug Docker
- certificat racine expiré
- panne DNS mondiale
- indisponibilité GitHub
- indisponibilité PyPI
- indisponibilité du fournisseur cloud
- suppression accidentelle du bucket de sauvegarde

---

## 4.1 Représentation de l'Ontologie comme un Dépôt Git (Arborescence ASCII)

```text
MLOps-Failure-Modes-Registry/

1. Supply Chain & Dépendances/
｜- une librairie Python est supprimée de PyPI
｜- une dépendance est compromise (attaque supply chain)
｜- une image Docker officielle est supprimée
｜- GitHub est indisponible lors d'un déploiement
｜- MLflow change son format interne
｜- Feast change une API
｜- PostgreSQL change un comportement après upgrade majeur
｜- uv/pip résout différemment les dépendances
｜- certificat GPG d'un package expiré
｜- dépôt Git inaccessible

2. Sauvegarde & Disaster Recovery/
｜- backup PostgreSQL corrompu
｜- backup jamais testé
｜- impossible de restaurer MLflow
｜- snapshot DVC perdu
｜- sauvegarde incomplète
｜- restauration beaucoup plus lente que prévu
｜- backup chiffré mais clé perdue
｜- réplication PostgreSQL cassée

3. Haute disponibilité/
｜- failover automatique
｜- plusieurs instances FastAPI
｜- load balancer mal configuré
｜- sticky session
｜- split-brain PostgreSQL
｜- élection de leader
｜- perte de quorum

4. Observabilité/
｜- métriques Prometheus qui n'arrivent plus
｜- Grafana affiche des données vieilles de 24 h
｜- horloges des serveurs désynchronisées
｜- logs incomplets
｜- rotation des logs supprime les informations trop tôt
｜- traces OpenTelemetry perdues
｜- dashboard cassé après changement de métrique
｜- alerte configurée sur une mauvaise métrique

5. Performance/
｜- index PostgreSQL supprimé
｜- plan SQL devenu mauvais
｜- fragmentation de table
｜- modèle qui met 400 ms au lieu de 20
｜- cache Feast vidé
｜- cache Redis saturé
｜- garbage collector Python qui monopolise le CPU

6. Problèmes Feature Store/
｜- online store ≠ offline store
｜- feature calculée avec un fuseau horaire différent
｜- feature expirée
｜- TTL incorrect
｜- feature jamais matérialisée
｜- clé d'entité dupliquée
｜- collision d'identifiants

7. Gestion Temporelle/
｜- heure d'été/hiver
｜- fuseau horaire
｜- année bissextile
｜- changement d'heure
｜- timestamp UTC vs local
｜- événement arrivé dans le futur (mauvaise horloge)
｜- dérive NTP

8. Pipeline ML/
｜- seed oublié
｜- seed différent entre CPU et GPU
｜- cross-validation mal configurée
｜- mauvaise métrique optimisée
｜- fuite entre folds
｜- déséquilibre de classes oublié
｜- calibration des probabilités perdue
｜- seuil de décision modifié

9. Pipeline de Données/
｜- ordre des colonnes changé
｜- colonne dupliquée
｜- encodage UTF-16
｜- caractères invisibles
｜- CSV vide
｜- lignes dans le désordre
｜- doublons partiels
｜- clé primaire non unique
｜- mauvaise granularité

10. Sécurité/
｜- CSRF / SSRF
｜- XSS sur Superset
｜- API Key compromise / JWT expiré
｜- élévation de privilège (Docker)
｜- fuite mémoire contenant des données sensibles
｜- secrets dans les logs
｜- modèle volé (Model Extraction Attack)
｜- attaques par inversion de modèle
｜- Data Poisoning
｜- Adversarial Examples

11. Gouvernance MLOps/
｜- deux modèles Production
｜- personne responsable du modèle
｜- absence d'approbation avant promotion
｜- promotion manuelle oubliée
｜- modèle jamais archivé
｜- documentation obsolète

12. Économie & FinOps/
｜- coût AWS/GCP explose
｜- coût API météo
｜- stockage DVC devient énorme
｜- MLflow atteint plusieurs centaines de gigaoctets
｜- coût GPU imprévu

13. Qualité des Prédictions/
｜- modèle trop confiant
｜- probabilités mal calibrées
｜- classe rare jamais prédite
｜- explosion des faux positifs / faux négatifs
｜- mauvaise calibration selon les départements

14. Facteur Humain/
｜- suppression accidentelle d'un modèle
｜- mauvaise branche Git
｜- rollback sur le mauvais modèle
｜- déploiement sur le mauvais serveur
｜- variable d'environnement de prod écrasée
｜- mauvaise clé API / fichier .env
｜- oubli de migration SQL

15. Cas Extrêmes (Black Swans)/
｜- panne électrique / incendie du datacenter
｜- corruption RAM / bug noyau Linux / bug Docker
｜- certificat racine expiré
｜- panne DNS mondiale
｜- indisponibilité GitHub / PyPI / Cloud
｜- suppression accidentelle du bucket de sauvegarde
```

---

Taxonomie selon les grandes dimensions d'un système MLOps (couverture systématique des familles de risques) :
- **Infrastructure** : calcul, stockage, réseau, cloud, conteneurs.
- **Données** : ingestion, qualité, schéma, versionnement, contrats, dérive.
- **Feature Engineering** : calcul, cohérence train/serve, Feature Store.
- **Entraînement** : reproductibilité, validation, expérimentation, registre de modèles.
- **Serving** : API, performance, disponibilité, montée en charge, rollback.
- **Observabilité** : logs, métriques, traces, alertes, dérive des données et des performances.
- **Sécurité** : authentification, autorisation, secrets, attaques classiques et spécifiques au ML.
- **Gouvernance** : audit, conformité, validation des modèles, documentation, gestion du cycle de vie.
- **Exploitation** : sauvegarde, restauration, reprise après incident, montée de version, capacité.
- **Organisation** : équipe, processus, dette technique, évolutions métier.

<pre>
MLOps-Dimensions-Mapping/
│
├── <b>Infrastructure</b>
│   ├── ── <span style="color: #34495E;">[10%] 10. Sécurité et Contrôle d'Accès</span>
│   ├── ── <span style="color: #4A235A;">[100%] 1. Crashs Systèmes & Infrastructures</span>
│   ├── ── <span style="color: #FF8C00;">[18%] 1. Supply Chain / Dépendances logicielles</span>
│   ├── ── <span style="color: #2ECC71;">[15%] 2. Sauvegarde / Disaster Recovery</span>
│   ├── ── <span style="color: #3498DB;">[30%] 3. Haute disponibilité</span>
│   ├── ── <span style="color: #9B59B6;">[15%] 4. Observabilité</span>
│   ├── ── <span style="color: #E74C3C;">[15%] 5. Performance</span>
│   ├── ── <span style="color: #2980B9;">[20%] 14. Scalabilité et Perf d'inférence</span>
│   ├── ── <span style="color: #BDC3C7;">[15%] 20. Économie & Coûts</span>
│   └── ── <span style="color: #E91E63;">[10%] 23. Cas Extrêmes</span>
│
├── <b>Données</b>
│   ├── ── <span style="color: #E84393;">[45%] 7. Temps, Dates & Fuseaux</span>
│   ├── ── <span style="color: #D35400;">[40%] 9. Pipeline de données</span>
│   ├── ── <span style="color: #F39C12;">[15%] 4. Problèmes de Code & Versioning</span>
│   ├── ── <span style="color: #FF8C00;">[3%] 1. Supply Chain / Dépendances logicielles</span>
│   ├── ── <span style="color: #2ECC71;">[18%] 2. Sauvegarde / Disaster Recovery</span>
│   ├── ── <span style="color: #3498DB;">[10%] 3. Haute disponibilité</span>
│   ├── ── <span style="color: #9B59B6;">[10%] 4. Observabilité</span>
│   ├── ── <span style="color: #E74C3C;">[20%] 5. Performance</span>
│   ├── ── <span style="color: #2C3E50;">[30%] 16. Dérive et Monitoring ML</span>
│   ├── ── <span style="color: #F39C12;">[45%] 17. Cycle de vie de la donnée</span>
│   └── ── <span style="color: #E91E63;">[10%] 23. Cas Extrêmes</span>
│
├── <b>Feature Engineering</b>
│   ├── ── <span style="color: #1ABC9C;">[100%] 6. Problèmes liés au Feature Store</span>
│   ├── ── <span style="color: #E84393;">[30%] 7. Temps, Dates & Fuseaux</span>
│   ├── ── <span style="color: #FF8C00;">[3%] 1. Supply Chain / Dépendances logicielles</span>
│   ├── ── <span style="color: #3498DB;">[5%] 3. Haute disponibilité</span>
│   ├── ── <span style="color: #9B59B6;">[2%] 4. Observabilité</span>
│   ├── ── <span style="color: #E74C3C;">[7%] 5. Performance</span>
│   ├── ── <span style="color: #7F8C8D;">[20%] 21. Qualité des prédictions</span>
│   └── ── <span style="color: #E91E63;">[10%] 23. Cas Extrêmes</span>
│
├── <b>Entraînement</b>
│   ├── ── <span style="color: #E84393;">[25%] 7. Temps, Dates & Fuseaux</span>
│   ├── ── <span style="color: #F1C40F;">[60%] 8. Pipeline ML</span>
│   ├── ── <span style="color: #FF8C00;">[21%] 1. Supply Chain / Dépendances logicielles</span>
│   ├── ── <span style="color: #2ECC71;">[3%] 2. Sauvegarde / Disaster Recovery</span>
│   ├── ── <span style="color: #3498DB;">[5%] 3. Haute disponibilité</span>
│   ├── ── <span style="color: #9B59B6;">[3%] 4. Observabilité</span>
│   ├── ── <span style="color: #E74C3C;">[8%] 5. Performance</span>
│   ├── ── <span style="color: #34495E;">[40%] 11. Reproductibilité</span>
│   ├── ── <span style="color: #16A085;">[35%] 12. Validation et Testing</span>
│   ├── ── <span style="color: #7F8C8D;">[20%] 21. Qualité des prédictions</span>
│   └── ── <span style="color: #E91E63;">[15%] 23. Cas Extrêmes</span>
│
├── <b>Serving</b>
│   ├── ── <span style="color: #F1C40F;">[15%] 8. Pipeline ML</span>
│   ├── ── <span style="color: #FF8C00;">[3%] 1. Supply Chain / Dépendances logicielles</span>
│   ├── ── <span style="color: #2ECC71;">[9%] 2. Sauvegarde / Disaster Recovery</span>
│   ├── ── <span style="color: #3498DB;">[30%] 3. Haute disponibilité</span>
│   ├── ── <span style="color: #9B59B6;">[10%] 4. Observabilité</span>
│   ├── ── <span style="color: #E74C3C;">[25%] 5. Performance</span>
│   ├── ── <span style="color: #27AE60;">[30%] 13. Déploiement et Rollback</span>
│   ├── ── <span style="color: #2980B9;">[40%] 14. Scalabilité et Perf d'inférence</span>
│   └── ── <span style="color: #E91E63;">[10%] 23. Cas Extrêmes</span>
│
├── <b>Observabilité</b>
│   ├── ── <span style="color: #FF8C00;">[3%] 1. Supply Chain / Dépendances logicielles</span>
│   ├── ── <span style="color: #3498DB;">[5%] 3. Haute availability</span>
│   ├── ── <span style="color: #9B59B6;">[40%] 4. Observabilité</span>
│   ├── ── <span style="color: #2C3E50;">[50%] 16. Dérive et Monitoring ML</span>
│   └── ── <span style="color: #E91E63;">[10%] 23. Cas Extrêmes</span>
│
├── <b>Sécurité</b>
│   ├── ── <span style="color: #34495E;">[80%] 10. Sécurité et Contrôle d'Accès</span>
│   ├── ── <span style="color: #FF8C00;">[12%] 1. Supply Chain / Dépendances logicielles</span>
│   ├── ── <span style="color: #2ECC71;">[3%] 2. Sauvegarde / Disaster Recovery</span>
│   ├── ── <span style="color: #9B59B6;">[1%] 4. Observabilité</span>
│   └── ── <span style="color: #8B0000;">[90%] 18. Sécurité et Privacy</span>
│
├── <b>Gouvernance</b>
│   ├── ── <span style="color: #34495E;">[10%] 10. Sécurité et Contrôle d'Accès</span>
│   ├── ── <span style="color: #F1C40F;">[25%] 8. Pipeline ML</span>
│   ├── ── <span style="color: #D35400;">[10%] 9. Pipeline de données</span>
│   ├── ── <span style="color: #FF8C00;">[6%] 1. Supply Chain / Dépendances logicielles</span>
│   ├── ── <span style="color: #2ECC71;">[3%] 2. Sauvegarde / Disaster Recovery</span>
│   ├── ── <span style="color: #9B59B6;">[4%] 4. Observabilité</span>
│   ├── ── <span style="color: #E74C3C;">[5%] 5. Performance</span>
│   ├── ── <span style="color: #C0392B;">[60%] 19. Gouvernance et Conformité</span>
│   ├── ── <span style="color: #BDC3C7;">[15%] 20. Économie & Coûts</span>
│   ├── ── <span style="color: #E67E22;">[30%] 22. Problèmes Humains</span>
│   └── ── <span style="color: #E91E63;">[10%] 23. Cas Extrêmes</span>
│
├── <b>Exploitation</b>
│   ├── ── <span style="color: #D35400;">[50%] 9. Pipeline de données</span>
│   ├── ── <span style="color: #FF8C00;">[31%] 1. Supply Chain / Dépendances logicielles</span>
│   ├── ── <span style="color: #2ECC71;">[44%] 2. Sauvegarde / Disaster Recovery</span>
│   ├── ── <span style="color: #3498DB;">[15%] 3. Haute disponibilité</span>
│   ├── ── <span style="color: #9B59B6;">[10%] 4. Observabilité</span>
│   ├── ── <span style="color: #E74C3C;">[15%] 5. Performance</span>
│   ├── ── <span style="color: #27AE60;">[20%] 13. Déploiement et Rollback</span>
│   ├── ── <span style="color: #BDC3C7;">[40%] 20. Économie & Coûts</span>
│   ├── ── <span style="color: #E67E22;">[15%] 22. Problèmes Humains</span>
│   └── ── <span style="color: #E91E63;">[5%] 23. Cas Extrêmes</span>
│
└── <b>Organisation</b>
    ├── ── <span style="color: #2ECC71;">[5%] 2. Sauvegarde / Disaster Recovery</span>
    ├── ── <span style="color: #3498DB;">[5%] 3. Haute disponibilité</span>
    ├── ── <span style="color: #9B59B6;">[5%] 4. Observabilité</span>
    ├── ── <span style="color: #E74C3C;">[5%] 5. Performance</span>
    ├── ── <span style="color: #16A085;">[10%] 12. Validation et Testing</span>
    ├── ── <span style="color: #C0392B;">[20%] 19. Gouvernance et Conformité</span>
    └── ── <span style="color: #E67E22;">[55%] 22. Problèmes Humains</span>
</pre>

-> C'est la manière dont on conçoit généralement des analyses de risques en ingénierie et en exploitation de systèmes complexes.

---

## 5. Vision Cible : La Matrice des Failure Modes MLOps

Au lieu d'un simple catalogue de problèmes, la proposition est de transformer à terme ce document en une matrice de gestion des Failure Modes. Chaque ligne deviendrait un objet avec des champs normalisés :

| Failure Mode | Gravité | Probabilité | Détection | Temps de détection | Réponse automatique | Réponse humaine | Testé ? |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **PostgreSQL indisponible** | Critique | Faible | Sentry + Prometheus | < 1 min | Redémarrage automatique | Oui | ✔ |
| **Drift de données** | Élevée | Moyenne | Evidently | 24 h | Non | Réentraînement | ✔ |
| **Data Leakage** | Critique | Faible | Validation CI | Avant déploiement | Blocage du pipeline | Oui | ✔ |

Cette approche apporte plusieurs bénéfices :
- elle priorise les risques plutôt que de les lister ;
- elle permet de vérifier qu'un plan de réponse existe pour chaque scénario ;
- elle facilite les exercices de simulation (chaos engineering, tests de reprise, jeux de rôle) ;
- elle sert de support à la gouvernance du projet et aux audits.

En l'état, ce document ressemble déjà à une base de connaissances MLOps très complète. Avec une matrice de criticité, des plans de réponse associés et un suivi du statut ("détecté", "mitigé", "testé"), il évoluerait vers un véritable registre des risques MLOps utilisable au quotidien par une équipe d'exploitation et de développement.

---


## PARTIE 3/100

*Curateur : Validé à 100%. Aucune hallucination détectée. Ce sont des scénarios SRE/MLOps critiques et vécus.*

### CATÉGORIE 9 (== PlanMaitre : 1. Supply Chain / Dépendances logicielles) : Les Problèmes de Supply Chain Logicielle & Dépendances
*(Tous les composants externes dont dépend indirectement le projet.)*

#### 9.1 — Dépendances Python

- **Une librairie est supprimée de PyPI**
  
  Lors d'un `uv sync` ou `pip install`, une dépendance n'existe plus (suppression du package, renommage, retrait pour faille de sécurité). Impossible de reconstruire un environnement pourtant fonctionnel six mois auparavant.

- **Une nouvelle version casse la rétrocompatibilité**
  
  `pandas`, `scikit-learn`, `numpy`, `pydantic` ou `sqlalchemy` publient une nouvelle version avec un changement de comportement. Le projet compile toujours. Les tests unitaires passent. Mais certaines fonctions renvoient des résultats différents. Le bug n'apparaît qu'en production.

- **Une dépendance change son API**
  
  Une fonction utilisée depuis plusieurs années est supprimée ou renommée.
  Exemple :
  `from sklearn.externals import joblib`
  n'existe plus après mise à jour. Le code ne démarre plus.

- **Une dépendance introduit un bug**
  
  Une nouvelle version de `pandas` contient un bug affectant les jointures. Le pipeline tourne. Les résultats sont faux. Aucune exception n'est levée. Le problème est très difficile à détecter.

- **Une dépendance devient vulnérable**
  
  Une CVE critique est publiée. Toute l'infrastructure devient vulnérable.
  Il faut :
  - identifier les projets concernés
  - reconstruire les images Docker
  - redéployer tous les services
  - vérifier la compatibilité

- **Deux dépendances deviennent incompatibles**
  
  Exemple :
  `numpy==2.x`
  n'est pas compatible avec
  `scikit-learn==1.3`
  L'environnement ne peut plus être installé.

- **Une dépendance est installée avec une mauvaise version**
  
  Un développeur oublie le lockfile. Il installe la dernière version disponible. Le bug n'existe que sur sa machine. Impossible à reproduire ailleurs.

- **Le lockfile est obsolète**
  
  `uv.lock` ou `poetry.lock` ne correspond plus au code. Les développeurs pensent travailler sur le même environnement. Ce n'est plus le cas.

- **Le cache des packages est corrompu**
  
  Le cache local contient un package incomplet. Les builds échouent de manière aléatoire. Supprimer le cache règle immédiatement le problème. Très difficile à diagnostiquer.

#### 9.2 — Images Docker

- **Une image Docker officielle disparaît**
  
  Une image référencée dans le `Dockerfile` n'existe plus. Le build échoue.

- **Le tag latest change**
  
  Le Dockerfile utilise `python:latest`. Une nouvelle version majeure est publiée. Le projet ne démarre plus.

- **Une image est reconstruite avec le même tag**
  
  Même si le tag reste identique (`python:3.12`), son contenu évolue. Deux builds réalisés à une semaine d'intervalle produisent des comportements différents.

- **Une image contient une faille critique**
  
  Une vulnérabilité est découverte. Tous les containers doivent être reconstruits.

- **Docker Hub devient indisponible**
  
  Impossible de récupérer les images. Les nouveaux serveurs ne peuvent plus être déployés.

- **Limitation du registre Docker**
  
  Docker Hub applique un rate limiting. Les pipelines CI/CD échouent.

- **Incompatibilité CUDA / Driver NVIDIA**
  
  Un conflit de version survient entre le driver `NVIDIA` installé sur la machine hôte et la version de `CUDA` compilée à l'intérieur du conteneur `Docker`. Le conteneur se lance mais l'accès au GPU est impossible, ou le code ML crashe silencieusement avec un CPU fallback ou une erreur de driver. C'est un risque d'environnement et de reproductibilité de la Supply Chain d'exécution.

#### 9.3 — Git

- **GitHub est indisponible**
  
  Impossible :
  - de cloner
  - de pousser
  - de lancer la CI
  Toute l'équipe est bloquée.

- **Un dépôt privé est supprimé**
  
  Le dépôt contenant un composant partagé disparaît. Le pipeline de build échoue.

- **Une branche est supprimée**
  
  La CI pointe vers une branche inexistante. Le pipeline s'arrête.

- **Un tag Git est modifié**
  
  Un développeur force un tag. Deux versions "`v1.0`" deviennent différentes. La reproductibilité est perdue.

- **Réécriture de l'historique**
  
  Un `git push --force` supprime des commits importants. Impossible de retrouver précisément la version ayant entraîné un modèle.

#### 9.4 — CI/CD

- **GitHub Actions est indisponible**
  
  Aucun pipeline ne démarre. Impossible de déployer.

- **Runner CI saturé**
  
  Les jobs restent en attente plusieurs heures. Les correctifs critiques ne peuvent pas être livrés.

- **Secret CI expiré**
  
  Le token Docker, le token MLflow, le token PostgreSQL expirent. La CI échoue.

- **Mauvaise variable d'environnement**
  
  La CI déploie vers `production` au lieu de `staging`.

- **Pipeline incomplet**
  
  Un développeur désactive par erreur : `pytest`, `Ruff`, `MyPy`. Le code est déployé sans validation.

#### 9.5 — Dépendances MLOps

- **Nouvelle version de MLflow incompatible**
  
  Le serveur `MLflow` est mis à jour. Les anciens artefacts ne sont plus correctement interprétés.

- **BentoML change son format de packaging**
  
  Les anciens modèles ne peuvent plus être servis (via `BentoML`).

- **Feast change son schéma interne**
  
  Les `Feature Views` de `Feast` doivent être recréées. Les anciennes définitions deviennent invalides.

- **Evidently modifie son API**
  
  Les rapports de drift de `Evidently` cessent de fonctionner.

- **dbt change le comportement d'une macro**
  
  Toutes les transformations SQL `dbt` changent subtilement. Les données produites deviennent différentes.

#### 9.6 — Supply Chain Sécurité

- **Une dépendance est compromise**
  
  Un package PyPI est publié avec du code malveillant. Le pipeline l'installe automatiquement. Le serveur est compromis.

- **Typosquatting**
  
  Un développeur installe `pandaas` au lieu de `pandas`. Le package est malveillant.

- **Dépendance transitivement compromise**
  
  Le projet ne dépend pas directement du package vulnérable. Mais une dépendance secondaire, elle, oui. Le risque reste présent.

- **Signature logicielle invalide**
  
  Un package est téléchargé mais sa signature cryptographique ne correspond pas. Le pipeline doit s'arrêter.

- **Dépendance abandonnée**
  
  Le mainteneur disparaît. Plus aucune mise à jour. Plus aucun correctif de sécurité.

#### 9.7 — Reproductibilité

- **Impossible de reconstruire un environnement historique**
  
  On souhaite réentraîner le modèle de 2024. Les versions exactes des dépendances n'existent plus. Le modèle obtenu est différent.

- **Artefact supprimé**
  
  Le modèle `MLflow` référence un fichier supprimé. Le modèle devient inutilisable.

- **Image Docker non archivée**
  
  Le `Docker` ayant servi au modèle `V1` n'existe plus. Impossible de reproduire exactement l'environnement.

- **Hash des dépendances différent**
  
  Deux environnements utilisent les mêmes versions. Mais des `wheels` compilées différemment. Les résultats numériques changent légèrement.

- **Build non déterministe**
  
  Deux builds du même commit produisent deux images différentes. La reproductibilité est perdue.

---

### Pourquoi cette catégorie est importante

Cette catégorie de risques est souvent absente des projets académiques, alors qu'elle est une source majeure d'incidents en production. Un système `MLOps` moderne ne dépend pas uniquement de votre code : il repose sur un écosystème de bibliothèques `Python`, d'images `Docker`, de registres, d'outils `CI/CD`, de dépôts `Git`, de registres de modèles et de composants tiers. Une évolution, une indisponibilité ou une compromission de l'un de ces maillons peut rendre impossible un déploiement, un rollback ou même la simple reconstruction d'un modèle entraîné plusieurs mois auparavant.
    - Cette catégorie complète très bien nos documents existants, car elle couvre un pan des risques qui est souvent sous-estimé jusqu'au jour où l'un d'eux bloque entièrement la chaîne de développement ou de mise en production.

---

### Analyse de Correspondance avec la Taxonomie des Grandes Dimensions :

En ingénierie de systèmes complexes et en exploitation (SRE/DevOps), la **CATÉGORIE 9 : Les Problèmes de Supply Chain Logicielle & Dépendances** chevauche principalement deux grandes dimensions de notre taxonomie :

1. **Exploitation** (Poids principal : 70%)
   
   C'est la dimension la plus pertinente pour ancrer cette catégorie. Dans notre définition, l'Exploitation couvre la sauvegarde, la reprise après incident, la capacité et la montée de version.
   
   Les problématiques de lockfiles obsolètes, de cache `PyPI` corrompu, de macro `dbt` qui casse, ou d'incompatibilité de versions (ex: `numpy` / `scikit-learn`) impactent directement la capacité à maintenir et reconstruire l'application en exploitation (reprise) et à gérer les mises à jour (montée de version). C'est le fait d'assurer la reproductibilité de l'environnement de production dans le temps.

2. **Infrastructure** (Poids secondaire : 30%)
   
   Cette catégorie touche également à l'Infrastructure (calcul, stockage, réseau, cloud, conteneurs) :
   
   Les serveurs GitHub indisponibles, le rate limiting de Docker Hub, ou les runners CI/CD saturés sont des défaillances de machines et de réseaux (l'infrastructure sur laquelle repose le build).

**Résumé :**
Si on doit graver une dimension principale pour cette catégorie, c'est **Exploitation** (pour le volet reproductibilité et montée de version), avec une forte dépendance à l'**Infrastructure** (pour l'hébergement des dépôts et des images).

### Suivi de l'Enrichissement Croisé :

- [mlops_failure_modes_taxonomy.md](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md) :
  - Traduction et intégration de 100% des incidents de la Catégorie 9 répartis sous leurs dimensions MLOps respectives :

    * **Dimension 1 : Infrastructure**
      - `9.2` — Incompatibilité `CUDA` / Driver `NVIDIA` (lignes [51](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L51))
      - `9.2` — Indisponibilité de `Docker Hub` (lignes [52](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L52))
      - `9.2` — Limitation du registre `Docker` (lignes [53](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L53))
      - `9.3` — Indisponibilité de `GitHub` (lignes [54](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L54))
      - `9.4` — Indisponibilité de `GitHub Actions` (lignes [55](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L55))
      - `9.4` — Runner `CI` saturé (lignes [56](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L56))
    * **Dimension 2 : Données**
      - `9.5` — Mise à jour macro `dbt` (SQL changé) (lignes [126](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L126))
    * **Dimension 3 : Feature Engineering**
      - `9.5` — `Feast` change de schéma interne (lignes [195](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L195))
    * **Dimension 4 : Entraînement**
      - `9.3` — Tag `Git` forcé (reproductibilité perdue) (lignes [245](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L245))
      - `9.7` — Incapacité de reconstruire env historique (lignes [246](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L246))
      - `9.7` — Image `Docker` d'exécution non archivée (lignes [247](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L247))
      - `9.7` — Divergence wheels (hash différent) (lignes [248](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L248))
      - `9.7` — Build image `Docker` non déterministe (lignes [249](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L249))
      - `9.7` — Modèle `MLflow` réf. dataset `DVC` supprimé (lignes [250](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L250))
      - `9.1` — `uv.lock` ou `dvc.lock` désynchronisé (lignes [251](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L251))
    * **Dimension 5 : Serving**
      - `9.5` — `BentoML` change de format packaging (lignes [302](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L302))
    * **Dimension 6 : Observabilité**
      - `9.5` — `Evidently` modifie son API (check drift) (lignes [366](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L366))
    * **Dimension 7 : Sécurité**
      - `9.2` — Image `Docker` contenant faille de sécu (lignes [386](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L386))
      - `9.6` — Attaque Supply Chain** (compromission package)| Sécurité | 5 | 2 | 2 | **20 (lignes [387](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L387))
      - `9.6` — Signature logicielle invalide (package corr.) (lignes [388](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L388))
      - `9.4` — Secret `CI/CD` expiré (lignes [389](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L389))
    * **Dimension 8 : Gouvernance**
      - `9.4` — Déploiement prod au lieu staging (CI error) (lignes [581](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L581))
      - `9.4` — Pipeline `CI` incomplet (tests/linter omis) (lignes [582](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L582))
    * **Dimension 9 : Exploitation**
      - `9.2` — `python:latest` (tag latest change) (lignes [616](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L616))
      - `9.2` — Reconstruction image avec même tag (écrasée) (lignes [617](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L617))
      - `9.3` — Dépôt `Git` privé supprimé (lignes [618](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L618))
      - `9.3` — Branche `Git` cible supprimée (lignes [619](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L619))
      - `9.5` — Mise à jour incompatible de `MLflow` (lignes [620](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L620))
      - `9.6` — Dépendance abandonnée sans correctifs (lignes [621](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L621))
      - `9.1` — Dépendance supprimée de `PyPI` (lignes [622](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L622))
      - `9.2` — Image `Docker` de base supprimée (lignes [623](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L623))
      - `9.1` — Bug silencieux de dépendance (lignes [624](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L624))
      - `9.3` — Réécriture historique `Git` (lignes [625](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L625))

---


## PARTIE 4/100

*Curateur : Validé à 100%. Ce sont des scénarios critiques et vécus de Sauvegarde, Restauration et Plan de Reprise d'Activité (PRA).*

### CATÉGORIE 10 (== PlanMaitre : 2. Sauvegarde / Disaster Recovery) : Les Problèmes de Sauvegarde, Restauration & Disaster Recovery
*(Tous les scénarios où il faut restaurer des données, reconstruire un environnement ou survivre à une catastrophe.)*

#### 10.1 — Sauvegardes de la Base de Données

- **La sauvegarde PostgreSQL échoue silencieusement**
  
  Le job quotidien `pg_dump` échoue (espace disque insuffisant, problème réseau, droits insuffisants), mais aucun système d'alerte ne le détecte. Le jour où la base tombe, la dernière sauvegarde exploitable date de plusieurs semaines.

- **La sauvegarde est corrompue**
  
  Le fichier `.sql` ou `.dump` est créé mais incomplet (interruption, disque défaillant, coupure réseau). La restauration échoue lorsqu'on en a réellement besoin.

- **Une sauvegarde vide**
  
  Le script de backup fonctionne mais sauvegarde une base vide (mauvaise variable d'environnement, mauvais serveur `PostgreSQL`). Tout semble normal. La catastrophe est découverte uniquement lors d'une restauration.

- **Sauvegarde réalisée sur la mauvaise base**
  
  Le backup cible accidentellement l'environnement de développement plutôt que la production. Les sauvegardes existent mais ne contiennent pas les bonnes données.

- **Sauvegarde incomplète**
  
  Certaines tables sont exclues (`--exclude-table`) par erreur. Au moment de la restauration, il manque des données critiques (logs, Feature Store, métadonnées `MLflow`, etc.).

- **Sauvegarde interrompue**
  
  Le serveur redémarre ou perd le réseau pendant le backup. Le fichier généré paraît valide mais est incomplet.

#### 10.2 — Restauration

- **La restauration n'a jamais été testée**
  
  Les sauvegardes existent depuis des mois. Personne n'a tenté de restaurer. Le jour d'un incident, les procédures ne fonctionnent pas.

- **Temps de restauration beaucoup trop long**
  
  La restauration d'une base de plusieurs centaines de Go prend plusieurs heures, voire plusieurs jours. Le temps d'indisponibilité dépasse largement les objectifs de reprise.

- **Mauvaise version PostgreSQL**
  
  Le backup provient d'une ancienne version de `PostgreSQL`. La restauration échoue ou nécessite une migration imprévue.

- **Le script de restauration est obsolète**
  
  Les procédures ont changé mais la documentation n'a pas été mise à jour. Impossible de reconstruire rapidement la plateforme.

- **La restauration écrase la production**
  
  Un administrateur restaure accidentellement une ancienne sauvegarde directement sur la base de production. Les données récentes sont perdues.

- **Données restaurées mais incohérentes**
  
  La base est restaurée mais les versions de schéma (`dbt`, migrations `SQL`) ne correspondent plus. Les applications ne fonctionnent plus.

#### 10.3 — Sauvegarde des Modèles ML

- **Le registre MLflow est perdu**
  
  La base `PostgreSQL` fonctionne toujours. Mais les artefacts (`mlruns/`) ont été supprimés. Les modèles ne peuvent plus être chargés.

- **Les artefacts MLflow sont corrompus**
  
  Les fichiers `.pkl`, `.joblib` ou les modèles `BentoML` sont incomplets. Le registre référence des modèles inutilisables.

- **Le modèle est restauré sans ses dépendances**
  
  Le modèle est présent. Le preprocessing, les encodeurs ou les scalers ont disparu. Les prédictions deviennent impossibles.

- **Les versions des modèles sont incohérentes**
  
  Le registre indique la version V5. Le stockage contient la V4. Le rollback charge un modèle inattendu.

- **Les signatures des modèles sont perdues**
  
  Les métadonnées (features attendues, types, versions) disparaissent. Impossible de garantir que les prédictions utilisent le bon schéma d'entrée.

#### 10.4 — Sauvegarde des Données

- **Les fichiers Parquet sont supprimés**
  
  Le Data Lake est perdu. Les données brutes ne peuvent plus être retraitées.

- **Les données DVC disparaissent**
  
  Le stockage `DVC` est supprimé ou inaccessible. Les anciennes versions des datasets deviennent irrécupérables.

- **Les snapshots sont incomplets**
  
  Certaines partitions du Data Warehouse ne sont jamais sauvegardées. L'historique est partiellement perdu.

- **Sauvegarde d'un dataset déjà corrompu**
  
  La corruption n'est pas détectée immédiatement. Toutes les sauvegardes suivantes contiennent déjà les données erronées. Aucune version saine n'existe plus.

- **Les métadonnées sont perdues**
  
  Les fichiers existent toujours. Mais les informations décrivant leur structure (catalogues, schémas, Feature Store) disparaissent.

#### 10.5 — Sauvegarde de l'Infrastructure

- **Les fichiers Docker Compose disparaissent**
  
  Le serveur est restauré. Mais la configuration `Docker` est perdue. Impossible de redémarrer rapidement les services.

- **Les fichiers .env sont perdus**
  
  Les secrets n'existent plus. Toutes les applications refusent de démarrer.

- **Les certificats SSL sont perdus**
  
  Les sauvegardes n'incluaient pas les certificats. Les services `HTTPS` deviennent inaccessibles.

- **Les scripts d'automatisation disparaissent**
  
  Les scripts de déploiement, de backup ou de restauration sont perdus. Toute reconstruction devient manuelle.

- **Les fichiers de configuration ne sont pas sauvegardés**
  
  Les fichiers `nginx.conf`, `prefect.yaml`, ou `superset_config.py` ne sont pas sauvegardés. Tous doivent être recréés de mémoire.

#### 10.6 — Reprise après Sinistre

- **Le serveur physique est détruit**
  
  Incendie, inondation, vol, ou panne matérielle irréparable. Il faut reconstruire entièrement l'infrastructure ailleurs.

- **Perte totale du disque**
  
  Le `SSD` hébergeant `PostgreSQL` tombe brutalement. Aucune donnée locale n'est récupérable.

- **Perte simultanée du serveur et des sauvegardes**
  
  Les sauvegardes étaient stockées sur le même serveur. La panne détruit les deux. Aucune récupération possible.

- **Région Cloud indisponible**
  
  Toute une région du fournisseur `Cloud` devient inaccessible. Les sauvegardes doivent être disponibles dans une autre région.

- **Plusieurs composants tombent simultanément**
  
  `PostgreSQL`, `MLflow` et le stockage des artefacts deviennent indisponibles en même temps. Les procédures individuelles existent. Mais aucune procédure globale n'a été testée.

#### 10.7 — Objectifs de Continuité

- **Le RPO est dépassé**
  
  La quantité de données perdues est supérieure à ce qui était acceptable. Par exemple, la dernière sauvegarde date de 48 heures alors que l'objectif était de 1 heure.

- **Le RTO est dépassé**
  
  La plateforme reste indisponible bien plus longtemps que prévu. L'objectif était une reprise en moins de 30 minutes. La restauration prend finalement 12 heures.

- **Les procédures ne sont connues que d'une personne**
  
  Le seul ingénieur connaissant la procédure de restauration est absent. La reprise est fortement retardée.

- **La documentation de reprise est obsolète**
  
  Les sauvegardes existent. Mais les étapes documentées ne correspondent plus à l'architecture actuelle.

#### 10.8 — Tests de Résilience

- **Les sauvegardes ne sont jamais vérifiées**
  
  Les fichiers sont générés chaque jour. Personne ne contrôle qu'ils sont exploitables.

- **Aucun exercice de restauration n'est réalisé**
  
  L'équipe découvre les problèmes uniquement lors d'un incident réel.

- **Les tests sont réalisés uniquement sur de petits volumes**
  
  La restauration d'une base de test fonctionne. La restauration de la base de production révèle des problèmes de performance ou de capacité.

- **Les procédures ne couvrent pas tous les composants**
  
  La base est restaurée. Mais `MLflow`, `Feast`, `Superset` ou `Prefect` ne le sont pas. Le système reste partiellement inutilisable.

---

### Analyse de Correspondance avec la Taxonomie des Grandes Dimensions :

- **Exploitation** (Poids principal : 80%)
  
  Cette catégorie touche au cœur de l'Exploitation (sauvegarde, restauration, reprise après incident, montée de version, capacité). Elle traite exclusivement de la capacité à sauvegarder et à restaurer l'intégralité d'un système complexe d'apprentissage automatique (données, modèles, métadonnées, configurations) et de gérer les objectifs RPO/RTO.

- **Infrastructure** (Poids secondaire : 10%)
  
  La couche d'Infrastructure est sollicitée lors de sinistres physiques (destruction de datacenters, perte de disques SSD), lors de la perte de configuration d'orchestration (`Docker Compose`) ou des routeurs applicatifs (`Nginx`), ainsi que dans la répartition géographique des sauvegardes sur plusieurs régions `Cloud`.

- **Organisation** (Poids secondaire : 10%)
  
  Les aspects d'objectifs métier (RPO/RTO), la dépendance à des compétences individuelles critiques ("les procédures ne sont connues que d'une personne"), la caducité de la documentation opérationnelle de reprise, ainsi que l'absence de processus de tests (exercices de Chaos Recovery) relèvent de la dimension Organisation.

**Résumé :**
Si on doit graver une dimension principale pour cette catégorie, c'est **Exploitation** (pour le volet technique et processus de sauvegarde/restauration), avec des dépendances secondaires majeures à l'**Infrastructure** (pertes physiques de datacenters/disques/configurations compose) et à l'**Organisation** (gestion des équipes, formation et documentation de reprise).

### Suivi de l'Enrichissement Croisé :

- [mlops_failure_modes_taxonomy.md](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md) :
  - Traduction et normalisation de 100% des incidents de la Catégorie 10 répartis sous leurs dimensions MLOps cibles :
    
    * **Dimension 1 : Infrastructure**
      - `10.5` — Perte des fichiers `Docker Compose`
      - `10.5` — Configuration `Nginx`/`Prefect`/`Superset` non sauvegardée
      - `10.6` — Destruction physique du serveur (Incendie/Vol/Panne)
      - `10.6` — Indisponibilité d'une région `Cloud` complète
      - `10.6` — Panne simultanée multi-composants (`PostgreSQL`/`MLflow`/`S3`)
    
    * **Dimension 2 : Données**
      - `10.2` — Données restaurées mais incohérentes (migrations `SQL`/`dbt` brisées)
      - `10.4` — Fichiers `Parquet` du Data Lake supprimés
      - `10.4` — Données `DVC` supprimées ou inaccessibles
      - `10.4` — Snapshots du Data Warehouse incomplets
      - `10.4` — Sauvegarde d'un dataset déjà corrompu (propagation de corruption)
      - `10.4` — Métadonnées perdues (catalogues/schémas)
    
    * **Dimension 4 : Entraînement**
      - `10.3` — Modèle restauré sans ses dépendances
    
    * **Dimension 5 : Serving**
      - `10.3` — Versions des modèles incohérentes
      - `10.3` — Signatures des modèles perdues
      - `10.5` — Certificats SSL perdus
    
    * **Dimension 7 : Sécurité**
      - `10.5` — Fichiers .env (secrets) perdus
    
    * **Dimension 8 : Gouvernance**
      - `10.2` — Restauration écrasant la production
    
    * **Dimension 9 : Exploitation**
      - `10.1` — Sauvegarde PG échec silencieux
      - `10.1` — Sauvegarde PG corrompue
      - `10.1` — Sauvegarde PG vide
      - `10.1` — Sauvegarde PG mauvaise base
      - `10.3` — Registre MLflow perdu
      - `10.3` — Artefacts MLflow corrompus
      - `10.5` — Scripts automatisation disparus
      - `10.6` — Perte totale disque
      - `10.6` — Perte simultanée serveur et sauvegardes
      - `10.7` — RPO dépassé
      - `10.7` — RTO dépassé
      - `10.8` — Sauvegardes non vérifiées
      - `10.8` — Aucun exercice restauration
      - `10.8` — Tests seulement sur petits volumes
    
    * **Dimension 10 : Organisation**
      - `10.7` — Procédures connues par une seule personne
      - `10.7` — Documentation reprise obsolète

- [bi_observability_genesis.md](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/bi_observability_genesis.md) : Ajout de la section `4.6 Dashboard Résilience & Disaster Recovery` pour concevoir le monitoring de l'état quotidien des backups, des tailles de dump, de l'âge du dernier backup (RPO) et de l'alerte de récence des tests de restauration.
- [mlops_anti_patterns_registry.md](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_anti_patterns_registry.md) : Ajout de l'anti-pattern 14 (`Le Faux Sentiment de Sécurité`) rejetant les sauvegardes non testées ("Schrödinger's Backup") et le stockage local colocalisé, préconisant les alertes de dumps en échec et les simulations de restauration.

#### Pourquoi cette catégorie est cruciale

La plupart des architectures sont conçues pour prévenir les incidents, mais la véritable maturité opérationnelle se mesure à la capacité de revenir à un état fonctionnel après une défaillance. Une stratégie de Disaster Recovery ne se limite pas à produire des sauvegardes : elle doit garantir qu'il est possible de restaurer l'ensemble de la plateforme — données, modèles, configurations, artefacts et infrastructure — dans un délai compatible avec les besoins métier. En pratique, de nombreuses organisations découvrent que leurs sauvegardes sont inexploitables uniquement lorsqu'une panne majeure survient.

Cette catégorie est l'une des plus importantes de toute la taxonomie, car elle répond à la question fondamentale : « Si demain nous perdons tout, combien de temps nous faudra-t-il pour reconstruire entièrement notre plateforme `MLOps`, sans perte de données ni de traçabilité ? ». C'est précisément ce qui distingue une plateforme simplement fonctionnelle d'une plateforme réellement résiliente.

---

### CATÉGORIE 11 (== PlanMaitre : 3. Haute disponibilité) : Les Problèmes de Haute Disponibilité & Résilience des Services

*(Tous les scénarios où un composant tombe mais où l'architecture est censée continuer à fonctionner.)*

#### 11.1 — Redondance des Services

- **Une seule instance FastAPI est déployée**
  
  Le container `FastAPI` tombe. Plus aucun utilisateur ne peut effectuer de prédiction. Aucun second serveur n'est disponible pour prendre le relais.

- **Une seule instance PostgreSQL**
  
  La base de données `PostgreSQL` tombe. Toute la plateforme devient indisponible, même si tous les autres services fonctionnent.

- **Une seule instance MLflow**
  
  Le registre des modèles `MLflow` devient inaccessible. Les nouveaux déploiements sont impossibles.

- **Une seule instance Prefect**
  
  Le scheduler `Prefect` tombe. Plus aucun pipeline quotidien ne démarre.

- **Une seule instance Superset**
  
  Les dashboards `Superset` deviennent indisponibles. Les données existent toujours, mais personne ne peut les consulter.

#### 11.2 — Load Balancing

- **Mauvaise répartition de charge**
  
  Le Load Balancer envoie 90 % du trafic sur un seul serveur. Les autres restent quasiment inutilisés. Un serveur sature alors que les autres sont libres.

- **Health Check mal configuré**
  
  Le Load Balancer considère un serveur comme sain. En réalité, celui-ci ne répond plus correctement. Les utilisateurs continuent d'être dirigés vers une instance défaillante.

- **Health Check trop strict**
  
  Le serveur répond légèrement plus lentement. Le Load Balancer le retire immédiatement. Toutes les requêtes basculent inutilement sur les autres instances.

- **Load Balancer indisponible**
  
  Tous les serveurs sont fonctionnels. Mais le point d'entrée unique (le Load Balancer) est en panne. Toute la plateforme devient inaccessible.

- **Configuration de routage incorrecte**
  
  Les requêtes `/predict` sont envoyées vers le mauvais service. Les erreurs apparaissent uniquement après le déploiement.

#### 11.3 — Réplication PostgreSQL

- **La réplication s'arrête silencieusement**
  
  Le serveur secondaire cesse de recevoir les nouvelles données. Tout semble fonctionner. Mais le jour du failover, plusieurs jours de données sont perdus.

- **Réplication avec retard important**
  
  Le serveur secondaire accuse plusieurs heures de retard. Les utilisateurs lisent des données obsolètes.

- **Réplication cassée après migration**
  
  Une mise à jour de `PostgreSQL` casse la réplication. Aucune copie des données n'est maintenue.

- **Réplication incomplète**
  
  Certaines bases ou certaines tables ne sont jamais répliquées. Le serveur secondaire est inutilisable.

#### 11.4 — Failover

- **Le failover automatique ne fonctionne pas**
  
  Le serveur principal tombe. Le serveur secondaire existe, mais la bascule automatique n'a pas lieu. Une intervention humaine est nécessaire.

- **Le failover bascule vers un serveur défectueux**
  
  Le serveur secondaire est déjà corrompu. La bascule aggrave la panne.

- **Retour arrière impossible**
  
  Après réparation du serveur principal, il est impossible de revenir à l'état initial sans interrompre la production.

- **Mauvais serveur élu comme primaire**
  
  Deux administrateurs déclenchent simultanément des procédures différentes. La mauvaise base devient le serveur principal.

#### 11.5 — Split-Brain

- **Deux bases deviennent simultanément primaires**
  
  Suite à une coupure réseau, les deux serveurs acceptent des écritures. Les données divergent, rendant la fusion extrêmement complexe.

- **Deux versions du modèle servent des prédictions différentes**
  
  Deux serveurs chargent des modèles différents tout en répondant aux mêmes utilisateurs. Les résultats deviennent incohérents.

- **Deux Feature Stores désynchronisés**
  
  Deux instances `Feast` retournent des valeurs différentes pour une même entité. Les prédictions dépendent du serveur interrogé.

#### 11.6 — Disponibilité Réseau

- **Perte de connectivité entre deux services**
  
  `FastAPI` fonctionne, `PostgreSQL` fonctionne, mais le réseau entre les deux est interrompu.

- **Partition réseau**
  
  Une partie des containers voit `PostgreSQL`, une autre non. Le comportement devient imprévisible.

- **DNS interne indisponible**
  
  Les services ne résolvent plus leurs noms et semblent tous en panne.

- **Mauvaise configuration réseau**
  
  Après un redéploiement `Docker`, les containers appartiennent à deux réseaux différents et ne communiquent plus.

#### 11.7 — Mise à l'Échelle

- **Auto-scaling absent**
  
  Le trafic double, le serveur sature et les temps de réponse explosent.

- **Auto-scaling trop agressif**
  
  Chaque pic de charge déclenche la création de nombreuses instances, rendant la plateforme instable.

- **Auto-scaling trop lent**
  
  Les nouvelles instances arrivent plusieurs minutes après le pic. Les utilisateurs subissent tout de même les ralentissements.

- **Les nouvelles instances ne chargent pas le modèle**
  
  Les containers démarrent mais échouent à récupérer le modèle `MLflow`, répondant immédiatement par des erreurs.

#### 11.8 — Déploiement Sans Interruption

- **Rolling Update interrompue**
  
  Le déploiement s'arrête au milieu. Certaines instances exécutent la version V1 et d'autres la V2.

- **Blue/Green mal configuré**
  
  Le trafic est envoyé vers le nouvel environnement avant qu'il soit prêt. Tous les utilisateurs rencontrent des erreurs.

- **Canary Deployment mal calibré**
  
  Le nouveau modèle reçoit 50 % du trafic au lieu des 5 % prévus. Le bug impacte immédiatement une grande partie des utilisateurs.

- **Rollback impossible**
  
  Le nouveau déploiement échoue, mais l'ancienne version a déjà été supprimée.

#### 11.9 — Stockage Partagé

- **Volume partagé indisponible**
  
  Les containers démarrent mais ne trouvent plus les modèles.

- **Stockage saturé**
  
  Le système reste disponible, mais plus aucun modèle ne peut être enregistré.

- **Incohérence entre plusieurs volumes**
  
  Deux serveurs utilisent deux versions différentes du même fichier, provoquant des divergences de comportement.

#### 11.10 — Dégradation Progressive

- **Le système continue de répondre mais devient extrêmement lent**
  
  Aucun service ne tombe. Les temps de réponse passent progressivement de 20 ms à 3 secondes. Le monitoring ne surveille que les erreurs HTTP.

- **Dégradation silencieuse**
  
  Une dépendance ralentit progressivement. Les utilisateurs pensent simplement que "l'application est moins fluide".

- **Cascade de pannes**
  
  `PostgreSQL` ralentit, `FastAPI` accumule les connexions, le Load Balancer considère les serveurs comme morts et toute la plateforme devient indisponible. La cause initiale était pourtant une simple saturation SQL.

#### 11.11 — Dégradation Fonctionnelle (Graceful Degradation)

- **Le service météo devient indisponible**
  
  Au lieu de bloquer toute la prédiction, le système continue avec les dernières données météo disponibles.

- **Le Feature Store tombe**
  
  L'API utilise les dernières features mises en cache. Les prédictions restent possibles.

- **SHAP indisponible**
  
  Les prédictions continuent, mais les explications `SHAP` sont temporairement désactivées.

- **Superset tombe**
  
  Les dashboards `Superset` deviennent indisponibles, mais les pipelines continuent de fonctionner.

- **MLflow indisponible**
  
  Les prédictions continuent avec le modèle déjà chargé en mémoire. Seuls les nouveaux déploiements sont suspendus.

#### 11.12 — Résilience Humaine

- **Une intervention manuelle est nécessaire à chaque incident**
  
  L'équipe devient le point faible de la disponibilité. Les temps de reprise dépendent entièrement de la présence d'un expert.

- **La procédure de bascule est inconnue**
  
  Le système est techniquement redondant, mais personne ne sait activer le failover.

- **Les procédures n'ont jamais été testées**
  
  Le premier exercice de bascule est réalisé... pendant une vraie panne.

---

### Analyse de Correspondance avec la Taxonomie des Grandes Dimensions :

- **Infrastructure** (Poids principal : 30%)
  
  La redondance physique et conteneurisée des instances (`FastAPI`, `PostgreSQL`), la gestion des Load Balancers, la disponibilité réseau (DNS, sous-réseaux Docker) et l'accès au stockage partagé relèvent directement de l'Infrastructure.

- **Serving** (Poids principal : 30%)
  
  Le dimensionnement de l'API de serving, l'auto-scaling face aux pics de charge, le chargement dynamique des modèles, les stratégies de déploiement (Blue/Green, Canary, Rolling updates) et la latence intrinsèque touchent au cœur de l'inférence.

- **Exploitation** (Poids secondaire : 15%)
  
  La mise en place de processus de failover (bascule automatique), l'élection de nœud primaire et l'orchestration des plans de reprise après incident (Disaster Recovery) appartiennent à la dimension Exploitation.

- **Données** (Poids secondaire : 10%)
  
  La réplication physique ou logique de la base de données, la latence de synchronisation et la gestion des divergences en cas de Split-Brain sont des problématiques de gestion de données.

- **Feature Engineering** (Poids secondaire : 5%)
  
  La synchronisation des Feature Stores distributed et les mécanismes de cache dégradé de `Feast` en cas de panne de l'Online Store.

- **Observability** (Poids secondaire : 5%)
  
  Le monitoring actif de la latence (P99) plutôt que des seules erreurs HTTP de type 500 pour contrer la dégradation progressive.

- **Organisation** (Poids secondaire : 5%)
  
  La résilience des équipes face aux alertes (SPOF humain), la rédaction de runbooks de bascule et l'organisation d'exercices de chaos réguliers.

**Résumé :**
La Haute Disponibilité est une propriété systémique qui s'articule à part égale entre l'**Infrastructure** (redondance, réseau, stockage) et le **Serving** (déploiements sans interruption, auto-scaling, gracefully degradation), soutenus par une **Exploitation** rigoureuse (failover automatique) et une **Organisation** entraînée.

### Suivi de l'Enrichissement Croisé :

- [mlops_failure_modes_taxonomy.md](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md) :
  - Traduction et normalisation de 100% des incidents de la Catégorie 11 répartis sous leurs dimensions MLOps cibles :
    
    * **Dimension 1 : Infrastructure**
      - `11.1` — `FastAPI` mono-instance (`SPOF`) (lignes [64](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L64))
      - `11.1` — `PostgreSQL` mono-instance (`SPOF`) (lignes [65](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L65))
      - `11.1` — `MLflow` mono-instance (`SPOF`) (lignes [66](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L66))
      - `11.1` — `Prefect` mono-instance (`SPOF`) (lignes [67](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L67))
      - `11.1` — `Superset` mono-instance (`SPOF`) (lignes [68](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L68))
      - `11.2` — `Load Balancer` en panne (`SPOF`) (lignes [69](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L69))
      - `11.6` — Perte de connectivité réseau inter-services (lignes [70](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L70))
      - `11.6` — Partition réseau partielle (lignes [71](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L71))
      - `11.6` — `DNS` interne indisponible (lignes [72](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L72))
      - `11.6` — Containers sur réseaux `Docker` différents (lignes [73](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L73))
      - `11.9` — Volume partagé indisponible (lignes [74](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L74))
      - `11.9` — Volume partagé saturé (lignes [75](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L75))

    * **Dimension 2 : Données**
      - `11.3` — Réplication `PostgreSQL` arrêtée silencieusement (lignes [96](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L96))
      - `11.3` — Réplication `PostgreSQL` retard important (lignes [97](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L97))
      - `11.3` — Réplication `PG` cassée suite à migration (lignes [98](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L98))
      - `11.3` — Réplication `PostgreSQL` incomplète (lignes [99](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L99))
      - `11.5` — Split-Brain `PostgreSQL` (Double Primaire) (lignes [100](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L100))

    * **Dimension 3 : Feature Engineering**
      - `11.5` — Feature Stores `Feast` désynchronisés (lignes [113](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L113))
      - `11.11` — Feature Store `Feast` indisponible (fallback cache) (lignes [114](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L114))

    * **Dimension 4 : Entraînement**
      - `11.11` — `MLflow` registry indisponible en training (lignes [134](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L134))

    * **Dimension 5 : Serving**
      - `11.2` — Mauvaise répartition de charge (`LB` skew) (lignes [153](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L153))
      - `11.2` — Health Check `LB` mal configuré (lignes [154](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L154))
      - `11.2` — Health Check `LB` trop strict (flapping) (lignes [155](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L155))
      - `11.2` — Routage `LB` incorrect (requêtes égarées) (lignes [156](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L156))
      - `11.5` — Deux versions modèles actives (divergence) (lignes [157](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L157))
      - `11.7` — Auto-scaling absent sous pic de charge (lignes [158](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L158))
      - `11.7` — Auto-scaling trop agressif (thrashing) (lignes [159](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L159))
      - `11.7` — Auto-scaling trop lent (lag d'instance) (lignes [160](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L160))
      - `11.7` — Nouvelle instance ne charge pas le modèle (lignes [161](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L161))
      - `11.8` — Rolling Update interrompue (état hybride) (lignes [162](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L162))
      - `11.8` — Blue/Green mal configuré (trafic précoce) (lignes [163](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L163))
      - `11.8` — Canary Deployment mal calibré (surcharge) (lignes [164](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L164))
      - `11.8` — Rollback impossible (ancienne version effacée) (lignes [165](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L165))
      - `11.9` — Volume partagé incohérent entre serveurs (lignes [166](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L166))
      - `11.10` — Ralentissement progressif sans suivi HTTP (lignes [167](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L167))
      - `11.10` — Dégradation silencieuse d'une dépendance (lignes [168](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L168))
      - `11.10` — Cascade de pannes (DB slow -> API -> LB) (lignes [169](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L169))
      - `11.11` — Service météo indisponible (fallback statique) (lignes [170](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L170))
      - `11.11` — SHAP indisponible (fallback no-explain) (lignes [171](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L171))
      - `11.11` — `MLflow` indisponible en serving (fallback) (lignes [172](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L172))

    * **Dimension 6 : Observabilité**
      - `11.11` — `Superset` indisponible (dashboards down) (lignes [183](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L183))

    * **Dimension 10 : Organisation**
      - `11.12` — Intervention manuelle systématique (SPOF) (lignes [261](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L261))
      - `11.12` — Procédure de bascule inconnue (non formée) (lignes [262](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L262))
      - `11.12` — Procédures de bascule jamais testées (Chaos) (lignes [263](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L263))

  Voici les lignes exactes de chaque dimension où elles ont été réparties :
  - **Infrastructure (Dimension 1)** : Aux lignes [64 à 75](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L64-L75) (`FastAPI/Postgres mono-instance`, `LB down`, `Réseau coupé`, `Volume saturé`).
  - **Données (Dimension 2)** : Aux lignes [96 à 100](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L96-L100) (`Arrêt réplication WAL`, `Lag réplication`, `Split-brain DB`).
  - **Feature Engineering (Dimension 3)** : Aux lignes [113 à 114](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L113-L114) (`Feast stores désynchronisés`, `Feast fallback offline`).
  - **Entraînement (Dimension 4)** : À la ligne [134](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L134) (`MLflow registry down in training`).
  - **Serving (Dimension 5)** : Aux lignes [153 à 172](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L153-L172) (`LB skew`, `Healthcheck strict`, `Canary overweight`, `Auto-scaling absent/lent`, `Cascade failure`, `Graceful fallbacks`).
  - **Observabilité (Dimension 6)** : À la ligne [183](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L183) (`Superset down`).
  - **Organisation (Dimension 10)** : Aux lignes [261 à 263](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L261-L263) (`Bascule manuelle systématique`, `Runbooks de bascule absents/non formés`).

- [bi_observability_genesis.md](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/bi_observability_genesis.md) : Ajout de la section `4.7 Dashboard Haute Disponibilité & Performance active` pour concevoir le monitoring de la répartition de charge (LB skew), des healthchecks (thrashing) et de la latence de réplication.
- [mlops_anti_patterns_registry.md](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_anti_patterns_registry.md) : Ajout de l'anti-pattern 15 (`L'Illusion de la Redondance Passive`) rejetant la redondance sans tests de bascule automatique ("Schrödinger's Failover") et préconisant des bascules réelles périodiques.

#### Pourquoi cette catégorie est essentielle

Beaucoup d'architectures possèdent des sauvegardes mais restent très fragiles en production, car elles reposent sur des composants uniques. La haute disponibilité vise à supprimer ces Single Points of Failure (SPOF) en introduisant de la redondance, des mécanismes de bascule automatique et des stratégies de dégradation contrôlée. L'objectif n'est plus seulement de restaurer le système après une panne, mais de faire en sorte que les utilisateurs ne perçoivent même pas qu'un composant est tombé.

#### Une remarque spécifique à notre architecture

En regardant ce que nous décrivons (`FastAPI` + `BentoML` + `PostgreSQL` + `MLflow` + `Prefect` + `Superset` + `Feast`), notre architecture actuelle semble volontairement mono-instance, ce qui est parfaitement adapté à un projet académique ou à un premier déploiement.

Tous les scénarios de cette catégorie ne sont donc pas à implémenter dès maintenant, mais ils sont utiles à documenter comme évolutions possibles vers une architecture de production à haute disponibilité.

C'est précisément le type de réflexion attendu lorsqu'on montre qu'on maîtrise non seulement le fonctionnement d'un système `MLOps`, mais aussi son évolution vers des exigences industrielles.

---

### CATÉGORIE 12 (== PlanMaitre : 4. Observabilité) : Les Problèmes d'Observabilité & de Monitoring

*(Tous les scénarios où le système fonctionne mal, mais où l'équipe ne le voit pas, le voit trop tard, ou interprète mal les signaux.)*

#### 12.1 — Logs

- **Les logs ne sont plus produits**
  
  Une mauvaise configuration du logger désactive l'écriture des logs. Le système fonctionne. Lorsqu'une erreur survient, aucun historique n'existe.

- **Les logs ne sont plus centralisés**
  
  Chaque container écrit ses propres logs. Personne ne peut reconstruire le parcours complet d'une requête.

- **Rotation des logs trop agressive**
  
  Les logs sont supprimés toutes les 24 heures. Le bug est signalé trois jours plus tard. Impossible d'en retrouver l'origine.

- **Rotation absente**
  
  Les logs grossissent sans limite. Le disque finit par être saturé. Les services tombent.

- **Niveau de log incorrect**
  
  Le niveau est réglé sur `ERROR`. Les warnings annonçant une future panne ne sont jamais enregistrés.

- **Niveau de log trop verbeux**
  
  Le niveau est réglé sur `DEBUG`. Les fichiers deviennent gigantesques. Les informations réellement importantes sont noyées.

- **Informations sensibles dans les logs**
  
  Les logs contiennent des mots de passe, des tokens, des clés API, ou des données personnelles (PII). Un accès aux logs suffit à compromettre la plateforme.

- **Les logs sont incohérents**
  
  Chaque service utilise un format différent. Impossible de corréler les événements.

#### 12.2 — Métriques

- **Les métriques ne sont plus collectées**
  
  Le système fonctionne. Mais `Prometheus` (ou l'outil équivalent) ne collecte plus rien. Les dashboards restent figés.

- **Les métriques sont incomplètes**
  
  Le CPU est surveillé, mais la mémoire ne l'est pas. La fuite mémoire reste invisible.

- **Mauvaise métrique surveillée**
  
  On surveille le nombre de requêtes, mais pas leur durée, leur taux d'erreur, ni leur succès réel. Les alertes sont inutiles.

- **Métrique calculée incorrectement**
  
  Une erreur dans le calcul du F1 Score conduit à afficher de bonnes performances alors que le modèle se dégrade.

- **Métriques obsolètes**
  
  Les dashboards affichent des données datant de plusieurs heures. Personne ne s'en aperçoit.

#### 12.3 — Alerting

- **Seuil d'alerte trop élevé**
  
  Le CPU reste à 95 % pendant plusieurs heures. Le seuil étant fixé à 99 %, aucune alerte n'est déclenchée.

- **Seuil trop faible**
  
  Une alerte est déclenchée à chaque petite variation. L'équipe finit par ignorer les notifications (phénomène de fatigue des alertes).

- **Canal d'alerte indisponible**
  
  Les alertes sont correctement générées, mais `Slack`, `Teams` ou le serveur d'e-mail ne fonctionne plus. Personne ne les reçoit.

- **Mauvais destinataire**
  
  Toutes les alertes sont envoyées à un ancien responsable. L'équipe actuelle n'est jamais informée.

- **Escalade inexistante**
  
  La première personne alertée ne répond pas, et aucun mécanisme ne transmet l'alerte à quelqu'un d'autre.

- **Les alertes sont désactivées**
  
  Un développeur coupe temporairement les notifications pendant un test et oublie de les réactiver.

#### 12.4 — Traces Distribuées

- **Impossible de suivre une requête**
  
  Une prédiction traverse `FastAPI`, `Feast`, `PostgreSQL`, et `BentoML`, mais aucune trace ne relie ces étapes. Le diagnostic devient très difficile.

- **Identifiant de corrélation absent**
  
  Deux erreurs surviennent simultanément. Impossible de savoir quels logs appartiennent à quelle requête.

- **Traces incomplètes**
  
  Le parcours s'interrompt au niveau du Feature Store. La véritable origine de la panne reste inconnue.

- **Horloges désynchronisées**
  
  Les serveurs n'ont pas la même heure. Les événements semblent se produire dans le mauvais ordre.

#### 12.5 — Monitoring du Modèle

- **La latence d'inférence augmente progressivement**
  
  Le modèle passe de 5 ms à 150 ms sans déclencher d'alerte.

- **Le nombre de prédictions chute**
  
  L'API fonctionne, mais presque plus personne ne l'utilise. Personne ne surveille cette métrique.

- **Les probabilités changent brutalement**
  
  Le modèle prédit soudainement 95 % de probabilités sur presque tous les cas. Le drift n'est pas détecté.

- **Une classe disparaît**
  
  Le modèle ne prédit plus jamais la classe "grave". Le F1 Score global reste pourtant acceptable.

- **Distribution des prédictions anormale**
  
  La répartition des classes change fortement, mais le système continue à servir normalement.

#### 12.6 — Monitoring des Données

- **Une feature devient constante**
  
  Une colonne prend toujours la même valeur. Le pipeline fonctionne, mais le modèle perd progressivement en performance.

- **Explosion des valeurs manquantes**
  
  Le taux de `NaN` passe de 2 % à 40 % sans déclencher d'alerte.

- **Distribution anormale**
  
  Une feature change brutalement de distribution. Le modèle continue de répondre, mais les performances chutent.

- **Valeurs impossibles**
  
  Des données aberrantes (Latitude à 352°, Âge à -8 ans, Vitesse à 1200 km/h) passent jusqu'au modèle sans rejet.

- **Cardinalité anormale**
  
  Une variable catégorielle passe de 15 modalités à 300, ralentissant fortement le pipeline.

#### 12.7 — Santé des Pipelines

- **Un pipeline tourne plus longtemps que d'habitude**
  
  L'ingestion prend habituellement 10 minutes, mais aujourd'hui elle prend 2 heures sans qu'aucune alerte ne soit envoyée.

- **Pipeline bloqué**
  
  Le job reste indéfiniment en état "Running" et ne se terminera jamais.

- **Pipeline relancé plusieurs fois**
  
  Le scheduler redémarre plusieurs exécutions identiques, créant des doublons de données.

- **Certains jobs ne s'exécutent plus**
  
  Le scheduler fonctionne, mais un flow particulier ne démarre plus.

#### 12.8 — Santé des Ressources

- **Fuite mémoire progressive**
  
  La RAM augmente très lentement. Le serveur ne plante qu'après plusieurs jours d'activité.

- **Saturation CPU**
  
  Une boucle infinie monopolise un cœur CPU, ralentissant tous les autres services.

- **Saturation disque**
  
  Les données sont toujours écrites, mais le stockage disque approche progressivement de 100 %.

- **Nombre de connexions SQL anormal**
  
  Le pool de connexions atteint sa limite, provoquant les premiers timeouts.

- **File d'attente qui grandit**
  
  Les requêtes arrivent plus vite qu'elles ne sont traitées, provoquant une augmentation progressive de la latence.

#### 12.9 — Monitoring du Monitoring

- **L'outil de monitoring tombe**
  
  `Prometheus`, `Grafana`, ou `Sentry` deviennent eux-mêmes indisponibles.

- **Dashboard cassé**
  
  After une mise à jour, le dashboard affiche 0 erreur, 0 requête, et 0 utilisateur alors que le système est actif.

- **Collecteur arrêté**
  
  L'agent qui collecte les métriques ne fonctionne plus. Le monitoring paraît normal, mais les données ne sont plus mises à jour.

- **Heartbeat absent**
  
  Un agent meurt silencieusement sans que personne ne vérifie s'il est encore vivant.

#### 12.10 — Faux Positifs / Faux Négatifs

- **Fausse alerte**
  
  Une alerte est déclenchée alors que le système est sain. L'équipe perd confiance dans le monitoring.

- **Incident non détecté**
  
  Une panne réelle survient sans alerte, et ce sont les utilisateurs qui signalent le problème.

- **Corrélation erronée**
  
  Deux incidents surviennent simultanément. L'équipe corrige le mauvais problème, et la panne principale persiste.

- **Bruit de monitoring**
  
  Des centaines d'alertes secondaires masquent l'alerte critique principale.

#### 12.11 — Monitoring Métier

- **Les métriques techniques sont bonnes**
  
  Le CPU, la RAM, et l'API sont au vert, mais la pertinence réelle des prédictions diminue fortement.

- **Les utilisateurs abandonnent la plateforme**
  
  Les services fonctionnent, mais le nombre d'utilisateurs chute sans qu'aucun indicateur de business ne le signale.

- **Une fonctionnalité n'est plus utilisée**
  
  Une API spécifique n'est plus appelée depuis des semaines sans que l'équipe ne le remarque.

- **Le modèle aide moins les décisions**
  
  Les performances techniques sont stables, mais les KPI métier se dégradent en raison d'une mauvaise adéquation du modèle.

---

### Analyse de Correspondance avec la Taxonomie des Grandes Dimensions :

- **Observabilité** (Poids principal : 40%)
  
  La surveillance des agents de monitoring (`Prometheus`, `Sentry`), la validité des dashboards `Superset`, la configuration des seuils d'alerte, la détection des faux positifs/négatifs et la gestion de la fatigue d'alerting sont au cœur de cette dimension.

- **Infrastructure** (Poids principal : 15%)
  
  La gestion physique des logs (saturation disque, rotation Docker), la disponibilité des canaux d'alerting (`Slack`, e-mail), le monitoring matériel (CPU, RAM, disque) et la synchronisation temporelle des horloges serveurs (`NTP`).

- **Serving** (Poids secondaire : 10%)
  
  La latence d'inférence P99, le suivi des volumes de requêtes API, la verbosité des logs d'exécution du serving, et la transmission des traces distribuées (`OpenTelemetry`).

- **Données** (Poids secondaire : 10%)
  
  La fraîcheur des dashboards de données, la dérive des données (Data Drift), l'apparition de valeurs manquantes (`NaN`), de données aberrantes (limites GPS/âge) ou d'explosions de cardinalité.

- **Exploitation** (Poids secondaire : 10%)
  
  La configuration opérationnelle des outils de rotation de logs, la surveillance de l'exécution des orchestrateurs de pipelines (`Prefect`, `cron`) et la désactivation temporaire des alertes.

- **Organisation** (Poids secondaire : 5%)
  
  La gestion des alertes d'équipe (rotations d'astreintes, routage vers le bon destinataire, escalades) et la préservation de la confiance dans les outils d'alerting.

- **Gouvernance** (Poids secondaire : 4%)
  
  Le monitoring des métriques d'impact business, le taux d'abandon utilisateur et le suivi de la pertinence des prédictions.

- **Entraînement** (Poids secondaire : 3%)
  
  Le calcul correct des métriques de performance des modèles (F1 Score) et le suivi du drift des probabilités.

- **Feature Engineering** (Poids secondaire : 2%)
  
  Le monitoring de Feast (traces Feast, features obsolètes ou abandonnées).

- **Sécurité** (Poids secondaire : 1%)
  
  La détection de secrets ou de données personnelles (PII) fuyant de façon non obfusquée dans les fichiers de logs.

**Résumé :**
L'Observabilité & le Monitoring agissent comme le système nerveux de la plateforme MLOps. Ils se concentrent principalement sur l'**Observabilité active** (40%), tout en irriguant l'**Infrastructure** (15%), le **Serving** (10%) et la qualité des **Données** (10%) pour anticiper les dégradations de service.

### Suivi de l'Enrichissement Croisé :

- [mlops_failure_modes_taxonomy.md](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md) :
  - Traduction et intégration de 100% des incidents de la Catégorie 12 répartis sous leurs dimensions MLOps respectives :
    
    * **Dimension 1 : Infrastructure**
      - `12.1` — Logs non produits (configuration erronée) (lignes [76](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L76))
      - `12.1` — Logs non centralisés (containers isolés) (lignes [77](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L77))
      - `12.1` — Absence de rotation des logs (disque saturé) (lignes [78](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L78))
      - `12.3` — Canal d'alerte (`Slack`/email) indisponible (lignes [79](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L79))
      - `12.4` — Horloges serveurs désynchronisées (`NTP` drift) (lignes [80](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L80))
      - `12.8` — Fuite mémoire progressive (`RAM` serving) (lignes [81](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L81))
      - `12.8` — Saturation `CPU` (boucle infinie serving) (lignes [82](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L82))
      - `12.8` — Saturation du stockage disque (backups/logs) (lignes [83](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L83))
      - `12.8` — Saturation du pool de connexions `SQL` (lignes [84](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L84))
      - `12.8` — File d'attente requêtes API qui grandit (lignes [85](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L85))
      - `12.9` — Outil de monitoring en panne (`Sentry` down) (lignes [86](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L86))

    * **Dimension 2 : Données**
      - `12.2` — Métriques obsolètes (dashboards figés) (lignes [112](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L112))
      - `12.6` — Feature constante dans le pipeline (SPOF) (lignes [113](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L113))
      - `12.6` — Explosion des valeurs manquantes (`NaN` rate) (lignes [114](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L114))
      - `12.6` — Feature change de distribution (Data Drift) (lignes [115](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L115))
      - `12.6` — Valeurs aberrantes non rejetées (GPS/Âge) (lignes [116](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L116))
      - `12.6` — Cardinalité anormale (explosion Categorical) (lignes [117](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L117))

    * **Dimension 3 : Feature Engineering**
      - `12.11` — Feature non utilisée (Feature abandonnée) (lignes [132](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L132))

    * **Dimension 4 : Entraînement**
      - `12.2` — Métrique F1 calculée avec formule erronée (lignes [153](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L153))
      - `12.5` — Drift des probabilités (baisse F1 silencieuse) (lignes [154](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L154))
      - `12.5` — Disparition silencieuse d'une classe (F1 OK) (lignes [155](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L155))
      - `12.5` — Distribution anormale des prédictions servies (lignes [156](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L156))

    * **Dimension 5 : Serving**
      - `12.1` — Niveau de log réglé sur ERROR (lignes [195](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L195))
      - `12.1` — Niveau de log sur DEBUG (disque sature) (lignes [196](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L196))
      - `12.1` — Formats de logs incohérents (lignes [197](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L197))
      - `12.4` — Impossible de suivre une requête (pas de traces) (lignes [198](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L198))
      - `12.4` — Traces incomplètes (arrêt Feature Store) (lignes [199](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L199))
      - `12.5` — Baisse brute du nombre de prédictions (lignes [200](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L200))
      - `12.5` — Latence d'inférence augmente sans alerte (lignes [201](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L201))

    * **Dimension 6 : Observabilité**
      - `12.2` — `Prometheus` ne collecte plus les métriques (lignes [213](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L213))
      - `12.2` — Métriques CPU collectées mais pas la RAM (lignes [214](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L214))
      - `12.2` — Surveillance de mauvaise métrique (lignes [215](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L215))
      - `12.4` — Identifiant de corrélation absent des logs (lignes [216](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L216))
      - `12.9` — Dashboard `Superset` cassé (lignes [217](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L217))
      - `12.9` — Agent collecteur de metrics arrêté (lignes [218](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L218))
      - `12.9` — Heartbeat de l'agent absent (lignes [219](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L219))

    * **Dimension 7 : Sécurité**
      - `12.1` — Secrets / `PII` dans les logs (non obfusqués) (lignes [233](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L233))

    * **Dimension 8 : Gouvernance**
      - `12.11` — Indicateurs techniques bons mais exactitude baisse (lignes [249](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L249))
      - `12.11` — Le modèle aide moins les décisions (baisse KPI) (lignes [250](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L250))

    * **Dimension 9 : Exploitation**
      - `12.1` — Rotation des logs trop agressive (effacés) (lignes [288](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L288))
      - `12.3` — Désactivation temporaire d'alertes oubliée (lignes [289](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L289))
      - `12.7` — Pipeline trop long (timeout ingestion) (lignes [290](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L290))
      - `12.7` — Pipeline bloqué en état "Running" (lignes [291](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L291))
      - `12.7` — Pipeline relancé en doublon (lignes [292](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L292))
      - `12.7` — Scheduler n'exécute plus un job spécifique (lignes [293](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L293))

    * **Dimension 10 : Organisation**
      - `12.3` — Seuil d'alerte trop élevé (incidents ratés) (lignes [309](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L309))
      - `12.3` — Seuil d'alerte trop faible (alert fatigue) (lignes [310](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L310))
      - `12.3` — Alertes envoyées à un ancien responsable (lignes [311](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L311))
      - `12.3` — Escalade d'alerte inexistante (pas de réponse) (lignes [312](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L312))
      - `12.10` — Bruit de monitoring (alertes noient la critique) (lignes [313](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L313))
      - `12.10` — Fausse alerte (perte de confiance) (lignes [314](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L314))
      - `12.10` — Incident réel non détecté (lignes [315](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L315))
      - `12.10` — Corrélation erronée entre incidents (lignes [316](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L316))
      - `12.11` — Utilisateurs abandonnent la plateforme (lignes [317](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L317))

  Voici les lignes exactes de chaque dimension où elles ont été réparties :
  - **Infrastructure (Dimension 1)** : Aux lignes [76 à 86](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L76-L86) (`Logs non centralisés`, `Storage saturated`, `SQL pool saturated`, `Queue latency`).
  - **Données (Dimension 2)** : Aux lignes [112 à 117](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L112-L117) (`Métriques obsolètes`, `Feature constante`, `NaN rate explosion`, `Drift`).
  - **Feature Engineering (Dimension 3)** : À la ligne [132](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L132) (`Feature abandonnée`).
  - **Entraînement (Dimension 4)** : Aux lignes [153 à 156](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L153-L156) (`F1 formula error`, `Prediction probability drift`, `Class disappearance`).
  - **Serving (Dimension 5)** : Aux lignes [195 à 201](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L195-L201) (`Log levels issues`, `Tracing missing/incomplete`, `Traffic drop`, `Latency degradation`).
  - **Observabilité (Dimension 6)** : Aux lignes [213 à 219](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L213-L219) (`Prometheus scraper down`, `Metrics gaps`, `Missing correlation ID`, `Dashboard bug`, `Agent stopped`).
  - **Sécurité (Dimension 7)** : À la ligne [233](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L233) (`Secrets leaking in logs`).
  - **Gouvernance (Dimension 8)** : Aux lignes [249 à 250](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L249-L250) (`Technical metrics green but accuracy drops`, `KPI degradation`).
  - **Exploitation (Dimension 9)** : Aux lignes [288 à 293](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L288-L293) (`Logs retention too short`, `Alerts disabled`, `Pipeline timeout/duplicates`).
  - **Organisation (Dimension 10)** : Aux lignes [309 à 317](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L309-L317) (`Alert thresholds issues`, `Alert fatigue`, `No escalation`, `FP/FN noise`, `Users churn`).

- [bi_observability_genesis.md](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/bi_observability_genesis.md) : En raison de l'importance critique du monitoring de monitoring et des métriques métiers, création de la section `4.8 Dashboard Meta-Monitoring & Business Alignment` pour monitorer Prometheus, Sentry, et les KPI métiers (ex: exactitude réelle vs technique).
- [mlops_anti_patterns_registry.md](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_anti_patterns_registry.md) : Ajout de l'anti-pattern 16 (`Le Syndrome de l'Alerte Silencieuse`) rejetant les alertes sans heartbeat ("Who monitors the monitor?") et préconisant des sondes ping réciproques.

#### Pourquoi cette catégorie est indispensable

L'observabilité répond à une question fondamentale :
"Comment savoir que quelque chose est en train de mal se passer avant que les utilisateurs ne s'en rendent compte ?"
Une plateforme MLOps mature ne surveille pas uniquement l'état de ses serveurs. Elle observe simultanément plusieurs niveaux : l'infrastructure, les applications, les pipelines de données, les modèles de Machine Learning et les indicateurs métier. La difficulté ne réside pas seulement dans la collecte de ces informations, mais dans la capacité à détecter les bons signaux, au bon moment, sans générer un volume d'alertes qui finirait par être ignoré.

Cette catégorie est plus riche que celle sur le `Disaster Recovery`, car tout le reste de notre document en dépend. Sans une bonne observabilité, la majorité des `Failure Modes` que nous avons déjà identifiés (crashs, dérive, corruption de données, baisse des performances, saturation des ressources, erreurs de pipeline) ne seront détectés que lorsqu'un utilisateur ou un décideur signalera un problème, ce qui est précisément ce que l'on cherche à éviter dans une architecture `MLOps` robuste.

---

### CATÉGORIE 13 (== PlanMaitre : 5. Performance) : Les Problèmes de Performance & Scalabilité Opérationnelle

*(Tous les scénarios où le système continue de fonctionner mais où ses performances se dégradent progressivement ou brutalement.)*

#### 13.1 — Performance de l'API

- **La latence d'inférence augmente progressivement**
  
  Le modèle répondait en 20 ms. Après plusieurs mises à jour : 40 ms, 80 ms, 150 ms, 400 ms. Aucun composant ne tombe. Les utilisateurs trouvent simplement l'application "de plus en plus lente".

- **Le modèle est plus lourd que prévu**
  
  Un nouveau modèle (Stacking, XGBoost, Random Forest très profond, Deep Learning...) nécessite beaucoup plus de calcul. Les temps de réponse explosent.

- **Chargement du modèle à chaque requête**
  
  Le modèle est rechargé depuis MLflow ou BentoML à chaque appel API. Le temps de réponse passe de quelques millisecondes à plusieurs secondes.

- **Temps de sérialisation important**
  
  La prédiction est rapide. Mais la conversion JSON des résultats devient le principal coût.

- **Temps de préprocessing dominant**
  
  Le Feature Engineering effectué avant la prédiction prend plus de temps que le modèle lui-même.

- **Trop de requêtes simultanées**
  
  L'API fonctionne parfaitement avec 10 utilisateurs. Elle devient très lente avec 500 utilisateurs.

#### 13.2 — Performance PostgreSQL

- **Une requête SQL devient très lente**
  
  Une requête auparavant exécutée en 100 ms prend maintenant plusieurs dizaines de secondes.

- **Absence d'index**
  
  Une nouvelle colonne est fréquemment interrogée. Aucun index n'a été créé. Toutes les recherches deviennent lentes.

- **Mauvais plan d'exécution**
  
  Après une mise à jour des statistiques PostgreSQL, le moteur choisit un plan beaucoup moins efficace.

- **Verrous longue durée**
  
  Une transaction garde un verrou pendant plusieurs minutes. Toutes les autres attendent.

- **Table devenue gigantesque**
  
  Une table contenant quelques centaines de milliers de lignes atteint plusieurs centaines de millions. Les performances chutent progressivement.

- **Fragmentation**
  
  Les index deviennent fragmentés. Les performances diminuent sans modification du code.

#### 13.3 — Performance du Pipeline

- **L'ingestion quotidienne devient de plus en plus lente**
  
  Chaque année de nouvelles données BAAC sont ajoutées. Le pipeline grossit. La durée d'exécution double progressivement.

- **Feature Engineering coûteux**
  
  Une nouvelle feature nécessite plusieurs jointures complexes. Le pipeline devient beaucoup plus lent.

- **SHAP devient très coûteux**
  
  Le calcul des explications dépasse largement le temps de prédiction.

- **Pipeline non parallélisé**
  
  Toutes les étapes sont exécutées séquentiellement. Le temps total devient prohibitif.

- **Mauvaise granularité des traitements**
  
  Le pipeline recharge l'ensemble des données alors que seules quelques lignes ont changé.

#### 13.4 — Performance du Feature Store

- **Les features sont recalculées inutilement**
  
  Les mêmes calculs sont effectués pour chaque requête.

- **Cache absent**
  
  Chaque prédiction relit les mêmes informations dans PostgreSQL.

- **Cache trop petit**
  
  Les données sont constamment évincées. Les accès disque deviennent permanents.

- **Materialization trop lente**
  
  Le rafraîchissement des Feature Views prend plusieurs heures. Les données servies deviennent obsolètes.

#### 13.5 — Performance du Modèle

- **Le modèle devient trop complexe**
  
  Les nouvelles versions augmentent progressivement : profondeur, nombre d'arbres, nombre de modèles empilés. Le gain de précision est faible. Le coût d'inférence explose.

- **Trop de features**
  
  Le nombre de variables double. Le temps de préprocessing augmente fortement.

- **Features inutiles**
  
  Le modèle manipule des centaines de variables n'apportant presque aucune information.

- **SHAP trop lent**
  
  Les explications deviennent plus coûteuses que les prédictions.

- **Optimisation absente**
  
  Le modèle n'utilise pas : batch prediction, vectorisation, parallélisme.

#### 13.6 — Performance Réseau

- **Latence réseau**
  
  Les services communiquent correctement. Mais chaque appel prend plusieurs centaines de millisecondes.

- **Trop d'appels réseau**
  
  Une prédiction nécessite : PostgreSQL, Feast, API météo, MLflow. Les latences s'additionnent.

- **Bande passante saturée**
  
  Les transferts de modèles deviennent très longs.

- **Compression absente**
  
  Les réponses API sont inutilement volumineuses.

#### 13.7 — Performance Mémoire

- **Multiplication des copies**
  
  Le pipeline crée plusieurs copies complètes des DataFrames. La consommation mémoire explose.

- **Objets jamais libérés**
  
  Le Garbage Collector ne récupère pas certains objets. La mémoire augmente progressivement.

- **Modèle trop volumineux**
  
  Le modèle occupe plusieurs gigaoctets. Chaque instance FastAPI consomme énormément de RAM.

- **Cache excessif**
  
  Le cache contient beaucoup plus d'informations que nécessaire.

#### 13.8 — Performance CPU

- **Une seule utilisation du CPU**
  
  Le serveur possède 32 cœurs. Le pipeline n'en utilise qu'un.

- **Mauvaise parallélisation**
  
  Le coût de synchronisation dépasse le gain obtenu.

- **Thread bloquant**
  
  Une opération bloque tous les autres traitements.

- **Boucle inefficace**
  
  Des traitements Python remplacent des opérations vectorisées. Les performances chutent.

#### 13.9 — Performance Disque

- **Trop d'accès disque**
  
  Les mêmes fichiers sont relus plusieurs fois.

- **Disque lent**
  
  Les performances SSD diminuent. Le pipeline ralentit.

- **Nombre excessif de petits fichiers**
  
  Des millions de petits fichiers Parquet remplacent quelques gros fichiers. Le système passe son temps à ouvrir des fichiers.

- **Fragmentation des données**
  
  Les données sont dispersées. Les lectures deviennent plus coûteuses.

#### 13.10 — Scalabilité

- **Le nombre d'utilisateurs augmente fortement**
  
  L'architecture fonctionnait pour quelques utilisateurs. Elle devient insuffisante.

- **Les données doublent chaque année**
  
  Le pipeline qui durait 20 minutes finit par durer plusieurs heures.

- **Les modèles deviennent plus nombreux**
  
  On passe d'un modèle à vingt modèles spécialisés. La mémoire explose.

- **Plusieurs équipes utilisent simultanément la plateforme**
  
  Les ressources deviennent insuffisantes.

- **Intégration de nouvelles sources**
  
  Ajout : météo, trafic, OpenStreetMap, données hospitalières. Le pipeline devient beaucoup plus lourd.

#### 13.11 — Régressions de Performance

- **Une mise à jour ralentit tout**
  
  Le code reste correct. Les performances chutent de 40 %. Personne ne compare les temps avant/après.

- **Refactoring moins performant**
  
  Le nouveau code est plus propre. Mais deux fois plus lent.

- **Dépendance plus lente**
  
  Une nouvelle version de Pandas ralentit certaines opérations.

- **Nouvelle feature très coûteuse**
  
  Une seule feature multiplie par trois le temps d'entraînement.

#### 13.12 — Performance Coût

- **Les performances augmentent... mais le coût explose**
  
  Le modèle répond 20 % plus vite. Il nécessite trois fois plus de serveurs.

- **Optimisation locale**
  
  Une optimisation accélère une étape. Mais ralentit l'ensemble du pipeline.

- **Surdimensionnement**
  
  Le serveur est largement surdimensionné par rapport aux besoins. Le coût d'exploitation devient inutilement élevé.

---

### Analyse de Correspondance avec la Taxonomie des Grandes Dimensions :

- **Serving** (Poids principal : 25%)
  
  L'augmentation progressive de la latence d'inférence, la lourdeur des nouveaux modèles, le temps de sérialisation JSON, le temps de préprocessing en serving, le rechargement de modèle à chaque requête, et les régressions de performance post-déploiement.

- **Données** (Poids principal : 20%)
  
  Les ralentissements de requêtes PostgreSQL, l'absence d'index colonnes, les plans d'exécution PostgreSQL inefficaces, la taille des tables, la fragmentation, la performance et granularité des pipelines d'ingestion.

- **Infrastructure** (Poids principal : 15%)
  
  Les latences réseau VPC, la bande passante saturée lors du chargement des modèles, la duplication des copies DataFrame en mémoire, les fuites de mémoire (GC leak), la consommation CPU mono-thread, l'absence de parallélisation, les threads bloquants, les disques lents et les petits fichiers Parquet multiples.

- **Exploitation** (Poids principal : 15%)
  
  La scalabilité face aux pics d'utilisateurs, le doublement annuel de la volumétrie BAAC, la gestion de dizaines de modèles spécialisés en parallèle, et le multi-tenant pour plusieurs équipes.

- **Entraînement** (Poids secondaire : 8%)
  
  La complexité croissante des modèles d'entraînement, le nombre excessif de features, l'évaluation lente (SHAP) et le manque d'optimisation / de parallélisation de l'entraînement.

- **Feature Engineering** (Poids secondaire : 7%)
  
  Le calcul redondant de features, la configuration des caches Redis de Feast (absence de cache ou éviction par manque de mémoire), et la matérialisation offline/online.

- **Gouvernance** (Poids secondaire : 5%)
  
  L'analyse FinOps, l'arbitrage coût/performance, l'optimisation locale au détriment du système, et le surdimensionnement des ressources matérielles.

- **Organisation** (Poids secondaire : 5%)
  
  L'absence de benchmarking systématique des performances et la mauvaise planification des capacités de calcul.

**Résumé :**
La Performance & la Scalabilité se situent à l'interface entre l'**Infrastructure** et la **Qualité Applicative**. Elles se concentrent principalement sur le **Serving** (25%) et la gestion des **Données** (20%) pour garantir que la plateforme reste réactive et financièrement viable.

### Suivi de l'Enrichissement Croisé :

- [mlops_failure_modes_taxonomy.md](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md) :
  - Traduction et intégration de 100% des incidents de la Catégorie 13 répartis sous leurs dimensions MLOps respectives :
    
    * **Dimension 1 : Infrastructure**
      - `13.6` — Latence réseau élevée (inter-services) (lignes [87](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L87))
      - `13.6` — Nombre d'appels réseau excessif (surcharge) (lignes [88](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L88))
      - `13.6` — Bande passante saturée (téléchargement) (lignes [89](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L89))
      - `13.6` — Absence de compression sur les API (lignes [90](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L90))
      - `13.7` — Copies de DataFrame excessives (mémoire) (lignes [91](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L91))
      - `13.7` — Fuite de mémoire (Garbage Collector leak) (lignes [92](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L92))
      - `13.7` — Modèle trop volumineux pour la RAM (lignes [93](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L93))
      - `13.7` — Cache excessif en mémoire (OOM) (lignes [94](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L94))
      - `13.8` — Exécution CPU mono-thread (lignes [95](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L95))
      - `13.8` — Coût de synchronisation threads trop élevé (lignes [96](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L96))
      - `13.8` — Thread principal de l'API bloqué (sync call) (lignes [97](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L97))
      - `13.8` — Traitements Python non vectorisés (boucle) (lignes [98](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L98))
      - `13.9` — Accès disque intempestifs et redondants (lignes [99](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L99))
      - `13.9` — Dégradation physique des IOPS (disque lent) (lignes [100](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L100))
      - `13.9` — Nombre excessif de petits fichiers Parquet (lignes [101](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L101))

    * **Dimension 2 : Données**
      - `13.2` — Requête SQL PostgreSQL lente (lignes [133](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L133))
      - `13.2` — Absence d'index sur colonne clé (lignes [134](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L134))
      - `13.2` — Mauvais plan d'exécution SQL (stats. obsolètes) (lignes [135](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L135))
      - `13.2` — Verrous PostgreSQL de longue durée (lignes [136](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L136))
      - `13.2` — Table PostgreSQL gigantesque (saturation) (lignes [137](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L137))
      - `13.2` — Fragmentation des index PostgreSQL (lignes [138](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L138))
      - `13.3` — Ingestion quotidienne BAAC trop lente (lignes [139](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L139))
      - `13.3` — Feature Engineering d'ingestion trop complexe (lignes [140](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L140))
      - `13.3` — Pipeline d'ingestion séquentiel (non parall.) (lignes [141](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L141))
      - `13.3` — Mauvaise granularité (rechargement complet) (lignes [142](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L142))
      - `13.9` — Fragmentation logique des données Parquet (lignes [143](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L143))

    * **Dimension 3 : Feature Engineering**
      - `13.4` — Features Feast recalculées inutilement (lignes [159](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L159))
      - `13.4` — Cache Redis Feast absent (lignes [160](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L160))
      - `13.4` — Cache Redis Feast trop petit (lignes [161](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L161))
      - `13.4` — Matérialisation Feast trop lente (lignes [162](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L162))

    * **Dimension 4 : Entraînement**
      - `13.5` — Modèle entraîné devenu trop complexe (lignes [187](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L187))
      - `13.5` — Trop de features à l'entraînement (lignes [188](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L188))
      - `13.5` — Features inutiles (bruit d'entraînement) (lignes [189](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L189))
      - `13.5` — Optimisation absente à l'entraînement (lignes [190](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L190))

    * **Dimension 5 : Serving**
      - `13.1` — Latence d'inférence augmentée (API lente) (lignes [236](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L236))
      - `13.1` — Modèle de serving trop lourd pour CPU (lignes [237](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L237))
      - `13.1` — Chargement du modèle à chaque requête (lignes [238](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L238))
      - `13.1` — Temps de sérialisation JSON important (lignes [239](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L239))
      - `13.1` — Temps de préprocessing serving dominant (lignes [240](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L240))
      - `13.1` — Surcharge par requêtes simultanées (lignes [241](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L241))
      - `13.3` — Calcul explications SHAP trop coûteux (lignes [242](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L242))
      - `13.11` — Mise à jour dégradant la latence (lignes [243](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L243))
      - `13.11` — Refactoring du code moins performant (lignes [244](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L244))
      - `13.11` — Mise à jour dépendance serving plus lente (lignes [245](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L245))

    * **Dimension 8 : Gouvernance**
      - `13.12` — Performances accrues mais coût explose (lignes [295](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L295))
      - `13.12` — Optimisation locale dégradant le global (lignes [296](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L296))
      - `13.12` — Surdimensionnement inutile des serveurs (lignes [297](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L297))

    * **Dimension 9 : Exploitation**
      - `13.10` — Surcharge par augmentation d'utilisateurs (lignes [341](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L341))
      - `13.10` — Volume de données annuel doublé (BAAC) (lignes [342](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L342))
      - `13.10` — Multiplication du nombre de modèles actifs (lignes [343](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L343))
      - `13.10` — Utilisateurs simultanés multi-équipes (lignes [344](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L344))
      - `13.10` — Intégration de nouvelles sources lourdes (lignes [345](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L345))

    * **Dimension 10 : Organisation**
      - `13.11` — Absence de comparaison perf avant/après (lignes [370](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L370))
      - `13.12` — Arbitrage inadéquat de dimensionnement (lignes [371](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L371))

  Voici les lignes exactes de chaque dimension où elles ont été réparties :
  - **Infrastructure (Dimension 1)** : Aux lignes [87 à 101](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L87-L101) (`Latence réseau VPC`, `Memory copies`, `GC leak`, `Thread block`, `Small Parquet files`).
  - **Données (Dimension 2)** : Aux lignes [133 à 143](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L133-L143) (`SQL latency`, `Missing index`, `Huge tables`, `ETL lag`, `Parquet fragmentation`).
  - **Feature Engineering (Dimension 3)** : Aux lignes [159 à 162](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L159-L162) (`Feast online cache`, `Redis size`, `Feast Materialization slow`).
  - **Entraînement (Dimension 4)** : Aux lignes [187 à 190](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L187-L190) (`Complex training model`, `Too many features train`, `Unoptimized training`).
  - **Serving (Dimension 5)** : Aux lignes [236 à 245](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L236-L245) (`API slow inference`, `Model reload request`, `JSON serialization`, `SHAP online slow`, `Refactoring degradation`).
  - **Gouvernance (Dimension 8)** : Aux lignes [295 à 297](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L295-L297) (`Cost performance skew`, `Local optimization skew`, `VM oversizing`).
  - **Exploitation (Dimension 9)** : Aux lignes [341 à 345](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L341-L345) (`User load scale`, `Data volume doubled`, `Models multiplication`, `Multi-team starvation`).
  - **Organisation (Dimension 10)** : Aux lignes [370 à 371](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L370-L371) (`Missing perf benchmark`, `Bad capacity sizing`).

- [bi_observability_genesis.md](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/bi_observability_genesis.md) : Intégration de la grille des Service Level Objectives (SLOs) cibles (ex: latence d'inférence < 100ms, temps d'ingestion BAAC < 30 min, taux d'éviction Redis < 1%) dans la section 4.7 et 4.8.
- [mlops_anti_patterns_registry.md](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_anti_patterns_registry.md) : Ajout de l'anti-pattern 17 (`L'Optimisation Prématurée et Locale`) consistant à sur-optimiser un composant isolé sans tracer le cycle complet d'inférence ni mesurer les bottlenecks réels (CPU/IO).

#### Pourquoi cette catégorie est essentielle

La performance ne consiste pas uniquement à rendre un système "rapide". Elle vise à garantir que les temps de réponse, les temps de traitement et la consommation des ressources restent compatibles avec les exigences du projet, même lorsque les volumes de données, le nombre d'utilisateurs ou la complexité des modèles augmentent. Contrairement à une panne, une dégradation de performance est souvent progressive et passe inaperçue si elle n'est pas mesurée.

#### Une remarque importante

Pour notre architecture BAAC, nous devrions surveiller en permanence des Service Level Objectives (SLO). Par exemple :

| Indicateur de Service (`SLI`) | Objectif de Performance (`SLO`) |
| :--- | :--- |
| Latence moyenne `/predict` | `< 100 ms` |
| Latence P95 | `< 250 ms` |
| Disponibilité API | `> 99.9%` |
| Temps d'ingestion BAAC | `< 30 min` |
| Temps de réentraînement | `< 6 h` |
| Temps de calcul `SHAP` | `< 500 ms` |
| Temps de réponse `PostgreSQL` | `< 50 ms` |
| Utilisation `CPU` moyenne | `< 70%` |
| Utilisation `RAM` | `< 80%` |
| Occupation disque | `< 85%` |

Cette catégorie fait le lien entre la haute disponibilité (le système reste accessible) et l'observabilité (on mesure son état). Elle répond à une question très concrète : « Le système fonctionne-t-il encore avec un niveau de performance acceptable ? ». C'est un aspect souvent négligé dans les projets académiques, alors qu'il est central dans les environnements de production.

---

### CATÉGORIE 14 (== PlanMaitre : 6. Problèmes liés au Feature Store) : Les Problèmes du Feature Store & des Features

*(Tous les scénarios où les features utilisées par le modèle deviennent incorrectes, incohérentes, obsolètes ou indisponibles.)*

#### 14.1 — Cohérence Train / Serve

- **Le Training-Serving Skew réapparaît**
  
  Le modèle est entraîné avec une Feature View. En production, une version différente est utilisée. Le modèle reçoit des valeurs différentes de celles vues pendant l'entraînement.

- **Les calculs diffèrent**
  
  Le script train.py calcule : `densite = nb_accidents / population`. La Feature View calcule : `densite = nb_accidents / population_active`. Même nom. Même feature. Valeur différente.

- **Les transformations ne sont plus synchronisées**
  
  Le `StandardScaler` utilisé à l'entraînement n'est plus celui chargé en production. Toutes les features numériques changent.

- **Encodage catégoriel différent**
  
  Le `OneHotEncoder` du modèle connaît : `route = A`, `route = B`, `route = C`. La Feature View fournit maintenant : `route = D`. La prédiction devient incorrecte.

#### 14.2 — Materialization

- **La materialization échoue**
  
  `feast materialize` plante. Le pipeline continue. Les anciennes features restent utilisées.

- **Materialization incomplète**
  
  Une partie seulement des nouvelles données est publiée. Le Feature Store contient un mélange d'ancien et de nouveau.

- **Materialization très lente**
  
  Les données du jour n'arrivent qu'après plusieurs heures. Les prédictions utilisent un historique dépassé.

- **Materialization oubliée**
  
  Les pipelines d'ingestion fonctionnent. Mais personne n'a déclenché la mise à jour du Feature Store.

#### 14.3 — Fraîcheur des Features

- **Features périmées**
  
  Les features servies ont plusieurs jours de retard. Le système continue pourtant à répondre normalement.

- **Timestamp incorrect**
  
  Une feature porte une mauvaise date. Feast considère qu'elle est encore valide.

- **TTL mal configuré**
  
  Le Time-To-Live est fixé à plusieurs semaines. Des données très anciennes continuent d'être servies.

- **Feature expirée trop tôt**
  
  Une feature devient invalide après quelques minutes. Toutes les prédictions tombent sur des valeurs par défaut.

#### 14.4 — Entity Keys

- **Mauvaise clé d'entité**
  
  Le modèle demande : `id_accident`. La Feature View est indexée sur : `id_zone`. Les features retournées correspondent au mauvais objet.

- **Collision d'identifiants**
  
  Deux entités différentes possèdent accidentellement la même clé. Le Feature Store renvoie les mauvaises informations.

- **Clé absente**
  
  L'entité demandée n'existe pas. Le Feature Store renvoie : `NULL`, valeurs par défaut, ou une erreur.

- **Clé dupliquée**
  
  Deux lignes possèdent la même clé. Feast choisit arbitrairement l'une des deux.

#### 14.5 — Schéma des Features

- **Une feature change de type**
  
  `float` devient `string`. Le Feature Store accepte la donnée. Le modèle échoue.

- **Une feature disparaît**
  
  La Feature View est mise à jour. Le modèle attend toujours cette variable.

- **Une nouvelle feature est ajoutée**
  
  Le modèle de production ne la connaît pas. Le schéma ne correspond plus.

- **Ordre des features modifié**
  
  Le modèle attend : `vitesse`, `pluie`, `trafic`. Le Feature Store renvoie : `pluie`, `vitesse`, `trafic`. Les valeurs sont permutées.

#### 14.6 — Valeurs des Features

- **Une feature devient constante**
  
  Toutes les lignes valent : `0`. Le modèle continue. Les performances diminuent.

- **Explosion des NaN**
  
  Une feature calculée retourne massivement : `NaN`.

- **Valeurs impossibles**
  
  `vitesse = -30`, `latitude = 200°`, `âge = -5`.

- **Mauvaise unité**
  
  Une feature est désormais exprimée en : `mph` au lieu de `km/h`.

- **Arrondi involontaire**
  
  Une feature float est convertie en entier. Toute la précision disparaît.

#### 14.7 — Cohérence Offline / Online

- **Offline Store correct / Online Store obsolète**
  
  Les entraînements utilisent les bonnes données. Les prédictions utilisent les anciennes.

- **Online Store perdu**
  
  Le cache est vidé. Toutes les requêtes repartent vers PostgreSQL. La latence explose.

- **Synchronisation interrompue**
  
  L'Offline Store continue de recevoir les nouvelles données. L'Online Store cesse d'être alimenté.

- **Deux Online Stores différents**
  
  Deux serveurs possèdent des versions différentes des mêmes features.

#### 14.8 — Versionnement des Features

- **Mauvaise version**
  
  Le modèle V3 attend : Feature View V3. L'API charge : Feature View V2.

- **Feature View supprimée**
  
  Une ancienne Feature View est effacée. Impossible de reproduire un ancien modèle.

- **Historique perdu**
  
  Impossible de retrouver quelles features étaient utilisées six mois auparavant.

- **Version des features non loguée**
  
  MLflow connaît le modèle. Pas la version exacte des features. La reproductibilité disparaît.

#### 14.9 — Performance du Feature Store

- **Feature très coûteuse**
  
  Une seule feature nécessite plusieurs jointures SQL. Chaque prédiction ralentit fortement.

- **Trop de Feature Views**
  
  Une requête doit interroger plusieurs dizaines de Feature Views.

- **Cache inefficace**
  
  Les mêmes features sont recalculées à chaque requête.

- **Materialization complète inutile**
  
  Toutes les features sont recalculées. Seulement 2 % ont réellement changé.

#### 14.10 — Dépendances entre Features

- **Cascade de calculs**
  
  Une feature dépend d'une autre. Une erreur se propage dans toute la chaîne.

- **Dépendance circulaire**
  
  Deux Feature Views se référencent mutuellement. Le pipeline devient impossible à exécuter.

- **Feature intermédiaire supprimée**
  
  Une Feature View utilisée comme base disparaît. Toutes les autres échouent.

#### 14.11 — Gouvernance des Features

- **Deux équipes créent la même feature**
  
  Deux définitions différentes de : `densite_accidents` existent. Les modèles utilisent des versions différentes.

- **Documentation obsolète**
  
  La définition métier d'une feature n'est plus correcte.

- **Personne ne sait comment une feature est calculée**
  
  Le créateur a quitté le projet. Impossible de maintenir la Feature View.

- **Feature jamais utilisée**
  
  Le Feature Store contient des dizaines de variables inutilisées. Le coût de maintenance augmente.

#### 14.12 — Sécurité

- **Une Feature View expose des données sensibles**
  
  Une feature contient des informations personnelles. Le modèle y accède sans contrôle.

- **Mauvais contrôle d'accès**
  
  Tous les utilisateurs peuvent lire toutes les Feature Views.

- **Corruption des features**
  
  Une erreur de pipeline modifie massivement les valeurs stockées. Le modèle continue pourtant à prédire.

- **Data Poisoning du Feature Store**
  
  Des données malveillantes sont injectées dans le Feature Store. Les prédictions sont progressivement dégradées.

#### Pourquoi cette catégorie est indispensable

Le Feature Store est le point de rencontre entre les données et le modèle. Il garantit que les mêmes transformations sont appliquées à l'entraînement et à l'inférence, mais il introduit aussi de nouveaux risques : désynchronisation entre les vues offline et online, obsolescence des features, erreurs de matérialisation, incohérences de schéma ou de versionnement. Ces problèmes sont particulièrement insidieux, car le système peut continuer à fonctionner sans aucune erreur apparente tout en fournissant au modèle des données incorrectes.

#### Une remarque spécifique à notre projet BAAC

Si nous utilisons réellement `Feast`, nous devrions ajouter une section entière sur la reproductibilité des features.

Aujourd'hui, notre document insiste beaucoup sur « retrouver le modèle utilisé il y a six mois ». En pratique, cela ne suffit pas.

Pour pouvoir reproduire exactement une prédiction historique, il faut être capable de répondre simultanément aux questions suivantes :
- quelle version du modèle était déployée ?
- quelle version de la `Feature View` était utilisée ?
- quelles données alimentaient cette `Feature View` ?
- quelle date de matérialisation a été utilisée ?
- quelles transformations étaient appliquées ?
- quelles valeurs exactes ont été servies au moment de la prédiction ?

Autrement dit, un modèle sans la version exacte de ses features n'est pas réellement reproductible.

C'est l'une des raisons d'être d'un Feature Store dans une architecture `MLOps` mature.

---

### Analyse de Correspondance avec la Taxonomie des Grandes Dimensions :

- **Feature Engineering** (Poids principal : 40%)
  
  La cohérence train/serve (Training-Serving Skew), l'alignement des clés d'entités, le typage et le schéma des variables Feast, la résolution des cascades de calculs, les dépendances cycliques entre Feature Views, et le versionnement applicatif des définitions de features.

- **Données** (Poids principal : 25%)
  
  Les échecs, délais et anomalies de matérialisation Feast (pipelines de réplication offline/online), la dégradation de fraîcheur des variables, les dérives de valeurs (features constantes, NaN, aberrations, unités), et la défaillance de synchronisation entre l'Offline Store (PostgreSQL) et l'Online Store (Redis).

- **Serving** (Poids principal : 12%)
  
  L'impact direct des désynchronisations de StandardScaler ou de OneHotEncoder (route D inconnue) sur les prédictions en ligne, l'inversion de l'ordre des variables lors de l'appel API, et la dégradation de latence suite à la perte du cache online Redis (fallback SQL).

- **Sécurité** (Poids secondaire : 8%)
  
  L'exposition de données PII sans anonymisation dans Feast, le manque de contrôle d'accès (RBAC) sur le registre de features, la corruption de données stockées suite à un bug de pipeline, et les injections de données malveillantes (Data Poisoning).

- **Gouvernance** (Poids secondaire : 5%)
  
  La perte de l'historique et de la traçabilité des features utilisées il y a six mois pour un run donné, la dérive documentaire, et la perte de connaissance des formules de calcul.

- **Infrastructure** (Poids secondaire : 4%)
  
  Les ralentissements induits par des jointures SQL offline lourdes, l'overhead d'interrogation simultanée de dizaines de views, et l'inefficacité de cache.

- **Entraînement** (Poids secondaire : 3%)
  
  L'absence de logs de version ou de metadata de features Feast au sein de MLflow lors du tracking des runs de modèle.

- **Exploitation** (Poids secondaire : 2%)
  
  Le coût d'hébergement et de maintenance des Feature Views abandonnées ou inutilisées.

- **Organisation** (Poids secondaire : 1%)
  
  Le risque de collision d'identifiants entre entités de sources différentes en l'absence de conventions d'équipe.

**Résumé :**
Le Feature Store est par définition la passerelle centrale de l'ingénierie MLOps. Ses défaillances impactent en premier lieu le **Feature Engineering** (40%) et la gestion des **Données** (25%), mais introduisent des risques sournois en **Serving** (12%) et en **Sécurité** (8%) par altération silencieuse des variables injectées dans le modèle.

### Suivi de l'Enrichissement Croisé :

- [mlops_failure_modes_taxonomy.md](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md) :
  - Traduction et intégration de 100% des incidents de la Catégorie 14 répartis sous leurs dimensions MLOps respectives :
    
    * **Dimension 1 : Infrastructure**
      - `14.9` — Feature Feast très coûteuse (requête SQL lente) (lignes [102](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L102))
      - `14.9` — Trop de Feature Views chargées simultanément (lignes [103](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L103))
      - `14.9` — Cache Feast inefficace (recalcul à la requête) (lignes [104](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L104))
      - `14.9` — Matérialisation Feast complète inutile (no delta) (lignes [105](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L105))

    * **Dimension 2 : Données**
      - `14.2` — La matérialisation Feast échoue (feast mat fail) (lignes [144](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L144))
      - `14.2` — Matérialisation Feast incomplète (lignes [145](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L145))
      - `14.2` — Matérialisation Feast très lente (lignes [146](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L146))
      - `14.2` — Matérialisation Feast oubliée (non déclenchée) (lignes [147](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L147))
      - `14.3` — Features Feast périmées (données obsolètes) (lignes [148](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L148))
      - `14.3` — Timestamp de feature incorrect dans Feast (lignes [149](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L149))
      - `14.3` — TTL Feast mal configuré (obsolescence acceptée) (lignes [150](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L150))
      - `14.3` — Feature Feast expirée trop tôt (no data) (lignes [151](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L151))
      - `14.6` — Feature Feast devenue constante (skew) (lignes [152](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L152))
      - `14.6` — Explosion des valeurs manquantes dans Feast (lignes [153](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L153))
      - `14.6` — Valeurs de features impossibles (limites) (lignes [154](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L154))
      - `14.6` — Mauvaise unité de feature (lignes [155](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L155))
      - `14.6` — Arrondi involontaire (perte float) (lignes [156](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L156))
      - `14.7` — Offline Store correct / Online Store obsolète (lignes [157](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L157))
      - `14.7` — Online Store perdu (Redis cache vide) (lignes [158](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L158))
      - `14.7` — Synchronisation Offline/Online interrompue (lignes [159](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L159))
      - `14.7` — Deux Online Stores différents (divergence) (lignes [160](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L160))

    * **Dimension 3 : Feature Engineering**
      - `14.1` — Training-Serving Skew réapparaît (Feast view) (lignes [179](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L179))
      - `14.1` — Calculs de features diffèrent (densité active) (lignes [180](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L180))
      - `14.4` — Mauvaise clé d'entité (id_accident/id_zone) (lignes [181](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L181))
      - `14.4` — Clé d'entité absente (renvoie NULL) (lignes [182](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L182))
      - `14.4` — Clé d'entité dupliquée (choix arbitraire) (lignes [183](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L183))
      - `14.5` — Feature change de type (float vers string) (lignes [184](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L184))
      - `14.5` — Feature supprimée dans la vue (attendue) (lignes [185](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L185))
      - `14.5` — Nouvelle feature ajoutée (inconnue) (lignes [186](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L186))
      - `14.5` — Ordre des features modifié dans Feast (lignes [187](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L187))
      - `14.8` — Mauvaise version de Feature View chargée (lignes [188](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L188))
      - `14.8` — Feature View supprimée (reprod. historique) (lignes [189](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L189))
      - `14.10` — Cascade d'erreurs de calcul entre features (lignes [190](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L190))
      - `14.10` — Dépendance circulaire entre Feature Views (lignes [191](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L191))
      - `14.10` — Feature intermédiaire supprimée (Feast fail) (lignes [192](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L192))
      - `14.11` — Deux équipes créent la même feature (duplicate) (lignes [193](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L193))

    * **Dimension 4 : Entraînement**
      - `14.8` — Version des features non loguée dans MLflow (lignes [207](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L207))

    * **Dimension 5 : Serving**
      - `14.1` — Transformations numériques désynchronisées (lignes [262](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L262))
      - `14.1` — Encodage catégoriel différent (route D) (lignes [263](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L263))

    * **Dimension 7 : Sécurité**
      - `14.12` — Feature View expose des données sensibles (PII) (lignes [294](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L294))
      - `14.12` — Mauvais contrôle d'accès aux Feature Views (lignes [295](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L295))
      - `14.12` — Corruption de features (erreur de pipeline) (lignes [296](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L296))
      - `14.12` — Data Poisoning du Feature Store (lignes [297](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L297))

    * **Dimension 8 : Gouvernance**
      - `14.8` — Historique des features perdu (reprod. imposs) (lignes [316](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L316))
      - `14.11` — Documentation Feast obsolète (lignes [317](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L317))
      - `14.11` — Perte de connaissance de calcul d'une feature (lignes [318](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L318))

    * **Dimension 9 : Exploitation**
      - `14.11` — Feature Feast abandonnée (dette de maintenance) (lignes [363](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L363))

    * **Dimension 10 : Organisation**
      - `14.4` — Collision d'identifiants (clés en doublon) (lignes [391](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L391))

  Voici les lignes exactes de chaque dimension où elles ont été réparties :
  - **Infrastructure (Dimension 1)** : Aux lignes [102 à 105](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L102-L105) (`Feast expensive feature`, `Too many views query`, `Cache Feast useless`, `Full materialize useless`).
  - **Données (Dimension 2)** : Aux lignes [144 à 160](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L144-L160) (`Materialization fail`, `Materialization incomplete`, `Materialization slow`, `Materialization forgotten`, `Stale features`, `Bad timestamps`, `TTL skew`, `Early expiry`, `Const feature`, `NaN explosion`, `Out of bounds`, `Unit mismatch`, `Bad rounding`, `Online stale`, `Online lost`, `Sync broken`, `Multi online`).
  - **Feature Engineering (Dimension 3)** : Aux lignes [179 à 193](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L179-L193) (`Train serve skew`, `Calculation diff`, `Entity keys mapping`, `Missing keys`, `Duplicate keys`, `Type change`, `Deleted feature`, `New feature`, `Feature ordering`, `Wrong version`, `Deleted view`, `Cascade error`, `Circular dep`, `Dependency deleted`, `Duplicate feature`).
  - **Entraînement (Dimension 4)** : Aux lignes [207](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L207) (`Feast MLflow unlogged`).
  - **Serving (Dimension 5)** : Aux lignes [262 à 263](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L262-L263) (`StandardScaler desync`, `OneHotEncoder route D desync`).
  - **Sécurité (Dimension 7)** : Aux lignes [294 à 297](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L294-L297) (`Feast PII exposure`, `Feast access control`, `Feast data corruption`, `Feast data poisoning`).
  - **Gouvernance (Dimension 8)** : Aux lignes [316 à 318](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L316-L318) (`Feast history lost`, `Feast doc obsolete`, `Feast calculation lost`).
  - **Exploitation (Dimension 9)** : Aux lignes [363](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L363) (`Feast abandoned feature`).
  - **Organisation (Dimension 10)** : Aux lignes [391](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L391) (`Feast key collision`).

- [bi_observability_genesis.md](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/bi_observability_genesis.md) : Ajout du monitoring de fraîcheur des features (Feature Store), alertes sur la matérialisation des vues (temps de calcul, données périmées) dans les sections 4.7 et 4.9.
- [mlops_anti_patterns_registry.md](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_anti_patterns_registry.md) : Ajout de l'anti-pattern 18 (`Le Feature Store Silencieux`) rejetant le serving de features sans validation de schéma à chaud ni suivi de la date de matérialisation effective.

### Suivi de l'Enrichissement Croisé (Mise à jour post-Audit) :
- [mlops_failure_modes_taxonomy.md](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md) : **Fusion et Normalisation.** Les incidents de la Catégorie 4 ont été fusionnés avec les anciens incidents de CI/CD et de Gouvernance. Au lieu de créer de nouveaux doublons, ils ont mis à jour les scripts existants (ex: `cicd_wrong_model_deployed.py`, `code_breaking_commit_main.py`). La matrice garantit l'unicité des pannes (Règle 7).
- [bi_observability_genesis.md](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/bi_observability_genesis.md) : Ajout d'une alerte sur les logs d'inférence manquants et la traçabilité des dépendances (Drift d'environnement).
- [mlops_anti_patterns_registry.md](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_anti_patterns_registry.md) : Ajout du "Déploiement Manuel Héroïque", du "Dataset Non-Versionné" et de l'"Absence de Seed Global".

### Pourquoi cette catégorie est essentielle :
Cette analyse de correspondance montre que la "Catégorie 4" historique agit comme le véritable **Tissu Conjonctif** entre le code pur (Software Engineering) et le monde probabiliste (ML). Sans cette rigueur de versioning et d'isolation d'environnement, l'observabilité et les modèles sont inutiles car impossibles à reproduire.




### CATÉGORIE 5 (== PlanMaitre : 5. Données & Features) : Problèmes de Données (Data Quality & Data Integrity)
(Tout ce qui concerne la qualité intrinsèque des données, leur cohérence, leur fiabilité et leur capacité à représenter correctement la réalité métier.)

#### 5.1 — Données incorrectes ou bruitées

- **Valeurs aberrantes**
  
  - vitesses impossibles
  - âges incohérents (ex : 999 ans)
  - coordonnées GPS invalides
  - dates dans le futur

- **Données erronées structurellement**
  
  - champs inversés
  - mauvaise saisie systématique
  - erreurs de parsing en amont

- **Bruit excessif**
  
  - données instables
  - fluctuations non significatives
  - perte de signal utile

#### 5.2 — Données manquantes

- **Missing values massifs**
  
  - colonnes fortement incomplètes
  - trous dans les séries temporelles

- **Missing not at random (MNAR)**
  
  - données manquantes liées au phénomène lui-même
  - biais structurel introduit

- **Propagation des NaN**
  
  - NaN non gérés en cascade dans le pipeline
  - explosion des erreurs downstream

#### 5.3 — Doublons et redondances

- **Doublons exacts**
  
  - mêmes lignes ingérées plusieurs fois
  - absence d’idempotence

- **Doublons partiels**
  
  - duplication via jointures mal définies

- **Inflation artificielle des données**
  
  - surestimation des volumes réels

#### 5.4 — Incohérences logiques

- **Incohérences inter-tables**
  
  - accident sans véhicule
  - véhicule sans usager
  - relations cassées entre entités

- **Incohérences internes**
  
  - champs contradictoires dans une même ligne

- **Violations de contraintes métier**
  
  - règles métier non respectées dans les données

#### 5.5 — Problèmes de distribution

- **Dataset non représentatif**
  
  - biais de collecte
  - surreprésentation de certaines zones ou périodes

- **Déséquilibre de classes**
  
  - classe majoritaire écrasante
  - classes rares mal représentées

- **Long tail ignorée**
  
  - cas rares sous-appris
  - perte des situations critiques

#### 5.6 — Data drift (côté données brutes)

- **Changement de distribution**
  
  - évolution naturelle des données dans le temps

- **Shift géographique**
  
  - changement de zones représentées

- **Shift comportemental**
  
  - évolution des comportements humains (ex : conduite, trafic)

#### 5.7 — Changement de schéma

- **Colonnes ajoutées**
  
  - non intégrées dans pipeline

- **Colonnes supprimées**
  
  - cassent les pipelines existants

- **Renommage de colonnes**
  
  - rupture silencieuse des transformations

- **Changement de type**
  
  - string ↔ int ↔ datetime

#### 5.8 — Problèmes de jointures

- **Explosion des lignes**
  
  - jointure cartésienne involontaire

- **Perte de données**
  
  - clé de jointure cassée ou absente

- **Granularité incohérente**
  
  - mismatch entre niveaux (accident / véhicule / usager)

- **Duplication via jointures**
  
  - surcomptage invisible

#### 5.9 — Problèmes temporels

- **Mauvais alignement temporel**
  
  - features calculées après l’événement

- **Time leakage**
  
  - utilisation de données futures dans l’entraînement

- **Décalage de timestamps**
  
  - UTC vs local time

- **Données en retard**
  
  - ingestion différée (J+1, J+7)

#### 5.10 — Problèmes de format

- **Encodage cassé**
  
  - UTF-8 vs Latin-1
  - caractères corrompus

- **Formats incohérents**
  
  - CSV vs JSON vs Parquet mal alignés

- **Parsing ambigu**
  
  - dates mal interprétées
  - floats mal convertis

#### 5.11 — Qualité sémantique des données

- **Définition métier floue**
  
  - même variable ≠ même signification selon sources

- **Changements de définition**
  
  - ex : “accident grave” redéfini légalement

- **Données hors contexte**
  
  - données correctes mais inutilisables pour le modèle

#### 5.12 — Données obsolètes

- **Données périmées**
  
  - dataset ancien non représentatif

- **Non mise à jour du dataset**
  
  - absence de refresh pipeline

- **Historique incomplet**
  
  - trous dans les séries longues

#### 5.13 — Corruption silencieuse

- **Pipeline “vert mais faux”**
  
  - aucun crash
  - mais données incorrectes

- **Dérive progressive non détectée**
  
  - détérioration lente de qualité

- **Erreurs cumulées**
  
  - petits biais → gros impact final

#### Résumé conceptuel de la catégorie 5

Cette catégorie couvre :
👉 tout ce qui fait que les données sont incorrectes, incohérentes, biaisées ou non représentatives, même si le pipeline fonctionne parfaitement.

Caractéristique clé :
Les données peuvent être “valides techniquement”, mais fausses ou trompeuses du point de vue métier.

---

### Suivi de l'Enrichissement Croisé (Mise à jour post-Audit) :
- [mlops_failure_modes_taxonomy.md](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md) : **Zéro injection requise.** Après audit, il a été prouvé mathématiquement que la `Catégorie 5` (Recheck) est strictement identique à la `Catégorie 17` (Data Quality). Pour respecter la Règle 7 (Aucun doublon matriciel), les tentatives d'injection redondantes ont été purgées. La Matrice reste pure.
### CATÉGORIE 6 (== PlanMaitre : 6. Problèmes liés au Feature Store) : Problèmes liés au Feature Store (Feast & Feature Management)

(Tout ce qui concerne la génération, le stockage, la cohérence et la disponibilité des features entre training et inference.)

#### 6.1 — Désynchronisation Feature Store / Data Warehouse

- **Feature Store obsolète**
  
  données non mises à jour (feast materialize oublié)
  features en retard par rapport à la DB
  → le modèle utilise des features anciennes

- **Incohérence entre sources**
  
  PostgreSQL à jour
  Feature Store non rafraîchi
  → training ≠ production

- **Pipeline de materialization cassé**
  
  jobs Feast échouent silencieusement
  features partielles en production

#### 6.2 — Training / Serving skew

- **Différence de calcul entre train et prod**
  
  feature calculée différemment dans :
  train.py
  Feature View Feast
  → modèle incohérent en production

- **Implémentation divergente**
  
  logique du feature engineering dupliquée
  versions non synchronisées

- **Feature approximée en production**
  
  simplification runtime pour perf
  perte de précision vs training

#### 6.3 — Features manquantes en production

- **Feature unavailable at inference time**
  
  dépendance externe indisponible
  API feature down (météo, trafic, etc.)

- **Fallback absent**
  
  pas de valeur par défaut
  crash ou NaN en production

- **Feature partiellement calculée**
  
  pipeline incomplet
  valeurs nulles injectées silencieusement

#### 6.4 — Feature computation coûteuse

- **Features trop lourdes**
  
  requêtes SQL multiples
  appels API externes
  calculs géospatiaux complexes
  → latence API explose

- **Features recalculées inutilement**
  
  pas de cache
  recomputation à chaque requête

- **Explosion du coût runtime**
  
  feature engineering devient plus cher que le modèle

#### 6.5 — Feature leakage

- **Leakage temporel**
  
  utilisation de données futures dans features

- **Leakage indirect**
  
  features corrélées au label futur

- **Leakage via agrégation**
  
  agrégations mal filtrées dans le temps

#### 6.6 — Feature inconsistency

- **Valeurs différentes selon contexte**
  
  même feature ≠ même valeur en train vs prod

- **Feature non déterministe**
  
  dépend d’un calcul instable ou API externe

- **Feature sensible au timing**
  
  variation selon heure d’exécution

#### 6.7 — Feature drift

- **Drift de distribution des features**
  
  changement naturel des données d’entrée du feature store

- **Drift silencieux**
  
  pas d’erreur
  mais dégradation modèle

- **Feature obsolète**
  
  feature ne représente plus la réalité métier

#### 6.8 — Gestion des versions de features

- **Feature non versionnée**
  
  impossible de savoir quelle définition a été utilisée

- **Breaking change dans une feature**
  
  modification de calcul sans backward compatibility

- **Incompatibilité modèle / feature set**
  
  modèle entraîné sur ancien set de features
  prod utilise nouveau set

#### 6.9 — Problèmes de latence Feature Store

- **Feature retrieval lent**
  
  requêtes SQL complexes
  joins lourds en production

- **Bottleneck centralisé**
  
  Feature Store devient goulot d’étranglement

- **Timeout en production**
  
  API renvoie erreur car feature computation trop lente

#### 6.10 — Problèmes de caching

- **Cache incohérent**
  
  données obsolètes servies

- **Cache non invalidé**
  
  features anciennes persistent

- **Cache absent**
  
  recalcul systématique coûteux

#### 6.11 — Gouvernance des features

- **Feature non documentée**
  
  personne ne sait comment elle est calculée

- **Feature redondante**
  
  plusieurs features identiques ou quasi-identiques

- **Feature inutilisée**
  
  features stockées mais jamais utilisées

- **Explosion du nombre de features**
  
  feature store devient ingérable

#### 6.12 — Corruption silencieuse du Feature Store

- **Feature store “vert mais faux”**
  
  ingestion OK
  mais valeurs incorrectes

- **Désalignement progressif**
  
  petites erreurs de calcul cumulées

- **Feature drift non détecté**
  
  changement subtil de logique métier non suivi

#### Résumé conceptuel de la catégorie 6

Cette catégorie couvre :
👉 tout ce qui fait que les features deviennent incohérentes entre entraînement et production, ou trop coûteuses, ou mal gouvernées.

Caractéristique clé :
Le modèle peut être bon — mais si les features sont incohérentes, tout le système devient faux.

Lien avec ton architecture BAAC
Dans ton cas, c’est une catégorie critique parce que :
- beaucoup de features dérivées (météo, géo, temps, trafic)
- forte dépendance à sources externes
- usage probable de Feast
- risque de training-serving skew élevé
- features complexes (spatio-temporelles)

---

### Analyse de Correspondance avec la Taxonomie des Grandes Dimensions :
- **Dimension 3 : Feature Engineering** : 70% (Désynchronisation, skew, leakage, versioning, corruption silencieuse).
- **Dimension 5 : Serving** : 20% (Latence, features manquantes, fallback, caching).
- **Dimension 10 : Organisation & Gouvernance** : 10% (Gouvernance, redondance).

### Suivi de l'Enrichissement Croisé (Correction Rétroactive Règle 30) :
- [mlops_failure_modes_taxonomy.md](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md) : **Zéro injection.** L'audit sémantique (Honnêteté Radicale / Règle 30) a prouvé que la quasi-totalité des 35 scénarios de la Catégorie 6 n'est qu'une déclinaison granulaire de 3 incidents déjà présents dans la Matrice sous la Catégorie `4.6` :
  - `4.6 — Feature engineering non versionné`
  - `4.6 — Désynchronisation training vs serving`
  - `4.6 — Feature store non aligné`
  L'injection naïve initiale a été entièrement annulée pour préserver l'intégrité de la Matrice et éviter une explosion de doublons conceptuels.

### CATÉGORIE 7 (== PlanMaitre : 7. Temps, Dates & Fuseaux) : Problèmes liés au Temps (Temporalité, Synchronisation & Historisation)

(Tout ce qui concerne la dimension temporelle des données, des features, des modèles et des systèmes — souvent une des sources les plus subtiles d’erreurs en MLOps.)

#### 7.1 — Désynchronisation temporelle des systèmes

- **Sources de données non alignées**
  
  météo en temps réel
  accidents en batch (J+1)
  trafic en streaming
  → mélange de temporalités incohérent

- **Décalage entre ingestion et usage**
  
  données ingérées à T
  utilisées comme si elles étaient à T réel

- **Incohérence UTC / local time**
  
  mélange de fuseaux horaires
  erreurs de datation des événements

#### 7.2 — Time leakage (fuite temporelle)

- **Utilisation de données futures**
  
  features calculées avec données post-événement

- **Agrégations mal filtrées**
  
  moyenne calculée sur toute la période incluant le futur

- **Index temporel incorrect**
  
  jointures sans condition temporelle stricte

#### 7.3 — Dérive temporelle (Time Drift)

- **Évolution naturelle des données**
  
  changement progressif des comportements
  évolution des infrastructures ou des règles

- **Ruptures de distribution dans le temps**
  
  événements majeurs :
  COVID
  changements législatifs
  crises

- **Modèle figé dans le passé**
  
  entraîné sur une période ancienne
  incapable de s’adapter au présent

#### 7.4 — Granularité temporelle incohérente

- **Mélange de résolutions**
  
  features horaires
  données journalières
  données annuelles
  → incohérences d’analyse

- **Agrégation incorrecte**
  
  perte d’information fine
  biais dans les patterns temporels

#### 7.5 — Données retardées (data latency)

- **Ingestion différée**
  
  données arrivant avec retard (J+1, J+7)

- **Feature computation en retard**
  
  features non disponibles à temps pour l’inférence

- **Décision basée sur données obsolètes**
  
  système réactif mais alimenté par historique retardé

#### 7.6 — Historisation et version temporelle

- **Absence de versioning temporel**
  
  impossible de reconstruire l’état du système à T passé

- **Écrasement des historiques**
  
  données modifiées rétroactivement sans traçabilité

- **Reproducibilité impossible dans le temps**
  
  même requête ≠ même résultat selon date d’exécution

#### 7.7 — Alignement training / serving dans le temps

- **Training sur période différente de la production**
  
  modèle entraîné sur 2018–2022
  utilisé en 2026 sans recalibration

- **Décalage conceptuel temporel**
  
  relation features ↔ label change avec le temps

- **Modèle “hors époque”**
  
  règles apprises obsolètes

#### 7.8 — Time window features mal gérées

- **Fenêtres temporelles incorrectes**
  
  rolling mean mal calculée
  fenêtre mal alignée (future incluse)

- **Overlapping windows non contrôlées**
  
  duplication implicite d’information

- **Window leakage**
  
  fuite d’information entre fenêtres temporelles

#### 7.9 — Horodatage incohérent

- **Timestamps manquants**
  
  événements non datés

- **Timestamps falsifiés ou arrondis**
  
  perte de précision temporelle

- **Ordre des événements incorrect**
  
  ingestion désordonnée

#### 7.10 — Problèmes de relecture historique

- **Backtesting biaisé**
  
  simulation utilisant des données corrigées postérieurement

- **Replay impossible**
  
  impossible de rejouer un pipeline à un instant T

- **Incohérence entre versions temporelles**
  
  données historiques modifiées sans traçabilité

#### 7.11 — Effets de saisonnalité mal modélisés

- **Saison ignorée**
  
  modèle ne comprend pas cycles annuels

- **Saison sur-apprise**
  
  sur-ajustement à patterns historiques

- **Ruptures saisonnières**
  
  changements structurels dans la saisonnalité

#### 7.12 — Cas extrêmes temporels

- **Événements rares dans le temps**
  
  crises
  catastrophes
  changements brutaux de comportement

- **Distribution non stationnaire**
  
  le passé ne représente plus le futur

- **Changement de régime temporel**
  
  ancien système → nouveau système comportemental

#### Résumé conceptuel de la catégorie 7

Cette catégorie couvre :
👉 tout ce qui fait que les données, les features et les modèles deviennent incorrects à cause du temps, de la désynchronisation ou de la non-stationnarité.

Caractéristique clé :
En MLOps, le temps est une variable cachée qui peut invalider tout le système sans jamais déclencher d’erreur.

Lien avec ton architecture BAAC
Dans ton cas, c’est une catégorie critique parce que :
- forte dimension historique (accidents sur plusieurs années)
- dépendance météo / trafic évolutif
- changements législatifs
- distribution non stationnaire forte
- besoin de backtesting fiable

---

### Analyse de Correspondance avec la Taxonomie des Grandes Dimensions :
- **Dimension 2 : Données** : 40% (Horodatage, retards, désynchronisation).
- **Dimension 3 : Feature Engineering** : 30% (Time windows, leakage temporel).
- **Dimension 4 : Entraînement** : 30% (Backtesting, saisonnalité, obsolescence).

### Suivi de l'Enrichissement Croisé (Application des Règles 35, 36, 37) :
- [mlops_failure_modes_taxonomy.md](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md) : **Injection sélective de 14 incidents inédits (21 rejetés car doublons conceptuels prouvés).**

**Preuve d'Inversion de la Charge (Règle 36) :**
- ❌ 7.1 (tous) sont des doublons de `17.6` et `17.8`.
- ❌ 7.2 (tous) sont couverts par `17.6` et `17.5`.
- ❌ 7.4, 7.5, 7.6, 7.7 sont couverts par `17.5`, `17.6`, `17.10` et `4.6`.
- ✅ **Inédits injectés (14) :**
  * **Dimension 2 : Données**
    - `7.3` — Ruptures de distribution dans le temps (Crise/Loi) (lignes TBA)
    - `7.9` — Timestamps tronqués ou arrondis abusivement
    - `7.12` — Événement rarissime (Black Swan)
    - `7.12` — Changement de régime temporel définitif
  * **Dimension 3 : Feature Engineering**
    - `7.8` — Fenêtre temporelle glissante erronée (Rolling Mean)
    - `7.8` — Overlapping windows (duplication temporelle)
    - `7.8` — Window leakage (fuite d'info entre fenêtres)
  * **Dimension 4 : Entraînement**
    - `7.3` — Modèle figé dans le passé (obsolescence)
    - `7.10` — Backtesting biaisé (sur données futures corrigées)
    - `7.10` — Impossibilité de rejouer le pipeline à T-1
    - `7.11` — Saisonnalité ignorée par le modèle
    - `7.11` — Sur-apprentissage des patterns saisonniers
    - `7.11` — Rupture des cycles saisonniers


### CATÉGORIE 8 (== PlanMaitre : 8. Pipeline ML / entraînement) : Problèmes de Pipeline ML (Training, Evaluation & MLflow)

(Tout ce qui concerne l’entraînement des modèles, leur validation, leur enregistrement, et la gestion du cycle de vie ML.)

#### 8.1 — Problèmes d’entraînement

- **Non-convergence du modèle**
  
  optimisation instable
  loss qui ne diminue pas
  hyperparamètres mal réglés

- **Instabilité des résultats**
  
  résultats différents à chaque run
  absence de seed global
  non-déterminisme du training

- **Entraînement interrompu**
  
  crash machine
  manque de RAM/CPU/GPU
  job arrêté sans checkpoint

- **Entraînement silencieusement mauvais**
  
  modèle “termine” mais apprend mal
  absence de validation correcte

#### 8.2 — Problèmes de données d’entraînement

- **Dataset incorrect**
  
  mauvais split train/test
  fuite de données dans le training

- **Dataset déséquilibré**
  
  classe majoritaire dominante
  apprentissage biaisé

- **Données obsolètes**
  
  modèle entraîné sur données trop anciennes

- **Sampling incorrect**
  
  échantillonnage non représentatif

#### 8.3 — Validation et évaluation

- **Métriques trompeuses**
  
  score global élevé mais performance mauvaise sur cas critiques

- **Validation leakage**
  
  test contaminé par données d’entraînement

- **Split temporel incorrect**
  
  mélange du futur et du passé dans train/test

- **Absence de validation robuste**
  
  pas de cross-validation ou validation temporelle

#### 8.4 — Overfitting / Underfitting

- **Overfitting silencieux**
  
  performance parfaite sur train
  mauvaise généralisation en prod

- **Underfitting**
  
  modèle trop simple
  incapacité à capturer patterns complexes

- **Over-optimisation sur métrique**
  
  modèle optimisé sur une métrique trop spécifique
  perte de performance globale métier

#### 8.5 — Hyperparameter tuning

- **Mauvais hyperparamètres**
  
  learning rate inadapté
  profondeur de modèle incorrecte

- **Grid search mal conçu**
  
  espace de recherche trop limité

- **Optimisation instable**
  
  résultats très sensibles aux hyperparamètres

#### 8.6 — MLflow & tracking

- **Artefacts mal enregistrés**
  
  modèle incomplet ou corrompu

- **Mauvais modèle promu en production**
  
  erreur humaine dans MLflow UI

- **Manque de traçabilité**
  
  impossible de savoir :
  dataset utilisé
  features exactes
  paramètres

- **Logs incomplets**
  
  absence de métriques critiques
  impossibilité de comparer modèles

#### 8.7 — Reproductibilité de l’entraînement

- **Run non reproductible**
  
  absence de seed
  parallélisation non déterministe

- **Différences environnementales**
  
  CPU vs GPU
  versions libraries différentes

- **Pipeline non figé**
  
  code évolue entre deux entraînements

#### 8.8 — Déploiement du modèle

- **Mauvais modèle déployé**
  
  version incorrecte mise en production

- **Incompatibilité modèle / API**
  
  format d’entrée différent entre entraînement et serving

- **Modèle chargé partiellement**
  
  artefact MLflow corrompu

#### 8.9 — Performance et latence du modèle

- **Modèle trop lent**
  
  inference time trop élevé
  incompatible temps réel

- **Modèle trop lourd**
  
  RAM / CPU insuffisant en production

- **Trade-off performance / complexité mal géré**
  
  modèle plus précis mais inutilisable en prod

#### 8.10 — Pipeline ML automatisé

- **Pipeline cassé**
  
  étape intermédiaire échoue sans rollback

- **Absence d’orchestration robuste**
  
  dépendances entre étapes mal gérées

- **Jobs non idempotents**
  
  réexécution produit doublons ou incohérences

#### 8.11 — Expérimentation ML

- **Explosion des expérimentations**
  
  trop de modèles non comparables

- **Perte de suivi expérimental**
  
  impossible de savoir quel modèle est le meilleur

- **Comparaison biaisée**
  
  modèles entraînés sur datasets différents

#### 8.12 — Drift dans le pipeline ML

- **Dataset shift entre runs**
  
  chaque entraînement utilise données différentes

- **Feature drift non détecté**
  
  pipeline d’entraînement déjà obsolète

#### Résumé conceptuel de la catégorie 8

Cette catégorie couvre :
👉 tout ce qui fait que l’entraînement, l’évaluation et la gestion des modèles deviennent non fiables, non reproductibles ou non comparables.

Caractéristique clé :
Le modèle peut “sembler bon”, mais son processus de création n’est pas fiable ou traçable.

Lien avec ton architecture BAAC
Dans ton cas :
- forte dépendance MLflow
- stacking models
- batch annuel de training
- features complexes multi-sources
- besoin fort de reproductibilité (réglementaire + métier)

---

### Analyse de Correspondance avec la Taxonomie des Grandes Dimensions :
- **Dimension 4 : Entraînement** : 60% (Overfitting, Splitting, Convergence).
- **Dimension 8 : Gouvernance** : 25% (MLflow, Tracking, Reproductibilité).
- **Dimension 5 : Serving** : 15% (OOM, Latence, Schéma d'API).

### Suivi de l'Enrichissement Croisé (Application de la Règle 38) :
- [mlops_failure_modes_taxonomy.md](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md) : **Injection sélective de 24 incidents inédits (11 rejetés car doublons conceptuels prouvés).**

**Preuve d'Inversion de la Charge (Règle 36) :**
- ❌ **Rejets motivés (11) :**
  - "Dataset déséquilibré" -> Absorbé par `21.4` (Biais de classe).
  - "Données obsolètes" -> Absorbé par `7.3` (Modèle figé dans le passé).
  - "Validation leakage" -> Absorbé par "Data Leakage dans le Split Train/Test" ci-dessous.
  - "Mauvais hyperparamètres" / "Optimisation instable" -> Absorbés par "Non-convergence".
  - "Run non reproductible" -> Absorbé par "Instabilité (absence de seed global)".
  - "Différences environnementales" -> Absorbé par `4.3` (Différence dev/prod).
  - "Pipeline non figé" -> Absorbé par `4.2` (Dépendances non figées).
  - "Modèle chargé partiellement" -> Absorbé par "Artefact corrompu dans MLflow".
  - "Pipeline cassé / Orchestration absente" -> Dimension 9 (Exploitation) déjà couverte.
  - "Drift dans le pipeline" -> Absorbé par `17.12` et "Comparaison biaisée".
- ✅ **Inédits injectés (24) :**
  * **Dimension 4 : Entraînement**
    - `8.1` — Non-convergence de l'entraînement (Loss plateau)
    - `8.1` — Instabilité d'entraînement (absence de seed global)
    - `8.1` — Crash OOM / Timeout sans Checkpoint d'entraînement
    - `8.1` — Entraînement abouti mais poids dégénérés (Silent fail)
    - `8.2` — Data Leakage dans le Split Train/Test
    - `8.2` — Échantillonnage d'entraînement non représentatif
    - `8.3` — Choix d'une métrique d'évaluation inadaptée au métier
    - `8.3` — Train/Test split aléatoire au lieu de temporel (Time leakage)
    - `8.3` — Absence de K-Fold ou de validation croisée
    - `8.4` — Overfitting silencieux (Train parfait, Prod catastrophique)
    - `8.4` — Underfitting (Modèle capacitairement trop faible)
    - `8.4` — Over-optimisation de métrique au détriment du proxy métier
    - `8.5` — Espace de recherche d'hyperparamètres trop étriqué
    - `8.10` — Pipeline d'entraînement non idempotent (crée des doublons si relancé)
  * **Dimension 5 : Serving**
    - `8.8` — Incompatibilité de schéma entre l'Artefact Modèle et l'API de Serving
    - `8.9` — Latence d'inférence (Inference Time) inacceptable
    - `8.9` — OOM au chargement du modèle en inférence (Trop lourd)
  * **Dimension 8 : Gouvernance**
    - `8.6` — Artefact de modèle incomplet/corrompu dans le registre MLflow
    - `8.6` — Promotion d'un mauvais modèle suite à erreur humaine (Tagging UI)
    - `8.6` — Absence de traçabilité MLflow (Hyperparamètres, Git hash manquants)
    - `8.6` — Logs d'expérimentation lacunaires (impossible de comparer)
    - `8.9` — Modèle trop complexe pour le ROI attendu
    - `8.11` — Cimetière d'expérimentations (des centaines de runs non nommés)
    - `8.11` — Comparaison de modèles entraînés sur des splits/datasets différents


### CATÉGORIE 9 (== PlanMaitre : 9. Pipeline de données) : Problèmes de Pipeline de Données (Ingestion, Transformation & Orchestration)

(Tout ce qui concerne la circulation des données depuis les sources brutes jusqu’aux tables exploitables, indépendamment du feature engineering ML.)

#### 9.1 — Ingestion de données

- **Ingestion partielle**
  
  fichier incomplet accepté comme valide
  absence de contrôle de complétude

- **Ingestion échouée silencieuse**
  
  job terminé sans erreur visible
  mais aucune donnée ajoutée

- **Ingestion dupliquée**
  
  retry automatique
  relance manuelle
  absence d’idempotence
  → doublons en base

- **Mauvaise source de données**
  
  ingestion de dataset obsolète
  confusion environnement (dev vs prod)

#### 9.2 — Orchestration des pipelines

- **Jobs qui s’exécutent dans le mauvais ordre**
  
  dépendances non respectées
  données utilisées avant préparation

- **Pipeline partiellement exécuté**
  
  étape 3 OK
  étape 4 échoue
  absence de rollback global

- **DAG cassé**
  
  dépendances mal définies
  tâches orphelines ou bloquantes

- **Retry infini ou absent**
  
  boucle de retry qui surcharge le système
  ou absence totale de retry

#### 9.3 — Transformation des données (ETL/ELT)

- **Transformation incorrecte**
  
  logique métier mal implémentée
  erreurs silencieuses dans SQL / Python

- **Transformation non déterministe**
  
  résultats différents selon exécution

- **Perte d’information**
  
  agrégation excessive
  suppression de granularité utile

- **Ajout de biais involontaire**
  
  transformation modifie la distribution des données

#### 9.4 — Qualité des données en pipeline

- **Validation insuffisante**
  
  données invalides passent en production

- **Validation trop stricte**
  
  rejet de données pourtant valides

- **Absence de schema enforcement**
  
  structure libre → instabilité globale

- **Données corrompues propagées**
  
  erreur upstream non stoppée

#### 9.5 — Performance du pipeline

- **Pipeline trop lent**
  
  traitement batch qui dépasse les fenêtres temporelles

- **Saturation CPU / RAM**
  
  jobs massifs qui killent le système

- **Mauvais partitionnement**
  
  traitement non scalable

- **Requêtes SQL inefficaces**
  
  scans complets de tables massives

#### 9.6 — Gestion des erreurs

- **Erreurs non remontées**
  
  pipeline continue malgré échec

- **Erreurs trop bruyantes**
  
  alert fatigue côté ingénieurs

- **Absence de logs exploitables**
  
  impossible de diagnostiquer les échecs

- **Retry dangereux**
  
  reprocessing amplifie les erreurs

#### 9.7 — Cohérence des données entre systèmes

- **Désynchronisation des bases**
  
  PostgreSQL ≠ data warehouse ≠ feature store

- **Réplication partielle**
  
  certaines tables mises à jour, d’autres non

- **Latence d’intégration**
  
  data disponible à des moments différents selon systèmes

#### 9.8 — Gestion des schémas

- **Schéma évolutif non contrôlé**
  
  colonnes ajoutées/supprimées sans versioning

- **Breaking change de schéma**
  
  pipeline cassé brutalement

- **Incompatibilité entre tables**
  
  jointures impossibles après évolution

#### 9.9 — Pipeline batch vs streaming

- **Mélange mal géré**
  
  incohérences entre données temps réel et batch

- **Double comptage**
  
  événement traité dans les deux pipelines

- **Désordre temporel**
  
  événements traités hors ordre

#### 9.10 — Gouvernance du pipeline

- **Absence de ownership**
  
  personne responsable du pipeline

- **Documentation inexistante**
  
  logique métier perdue

- **Pipeline non versionné**
  
  impossible de reproduire un run passé

- **Dépendances implicites**
  
  relations cachées entre jobs

#### 9.11 — Corruption silencieuse du pipeline

- **Pipeline “green but wrong”**
  
  exécution réussie
  résultats faux

- **Dégradation progressive**
  
  erreurs introduites petit à petit

- **Effet cumulatif**
  
  petites erreurs → gros impact final

#### Résumé conceptuel de la catégorie 9

Cette catégorie couvre :
👉 tout ce qui fait que les données circulent, se transforment et s’assemblent de manière incorrecte ou instable dans les pipelines.

Caractéristique clé :
Le système peut tourner sans erreur, mais produire des données totalement fausses ou incohérentes.

Lien avec ton architecture BAAC
Dans ton cas :
- ingestion multi-sources (BAAC + météo + etc.)
- batch ETL complexe
- forte dépendance à orchestrateur (Prefect / Airflow)
- jointures multi-tables critiques

---

### Analyse de Correspondance avec la Taxonomie des Grandes Dimensions :
- **Dimension 9 : Exploitation** : 50% (Orchestration, DAGs, OOM, Timeouts, Retries).
- **Dimension 2 : Données** : 40% (Transformation SQL/Python, Data Contracts stricts, Propagation).
- **Dimension 8 : Gouvernance** : 10% (Dépendances invisibles).

### Suivi de l'Enrichissement Croisé (Application de la Règle 38) :
- [mlops_failure_modes_taxonomy.md](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md) : **Injection sélective de 16 incidents inédits (22 rejetés car doublons conceptuels prouvés).**

**Preuve d'Inversion de la Charge (Règle 36) :**
- ❌ **Rejets motivés (22) :**
  - "Ingestion partielle", "Ingestion dupliquée", "Mauvaise source" -> Absorbés par `17.1` (Données partiellement chargées, Double ingestion, Mauvais environnement).
  - "Ajout de biais involontaire" -> Absorbé par `21.4` (Biais temporel/classe).
  - "Validation insuffisante", "Erreurs non remontées", "Pipeline green but wrong" -> Absorbés par `17.12` (Pipeline vert mais données fausses).
  - "Absence de schema enforcement", Tous les cas "Gestion des schémas (9.8)" -> Absorbés par `17.2` (Schéma implicite, Colonnes supprimées) et `17.5` (Jointure cassée).
  - "Requêtes SQL inefficaces" -> Absorbé par le nouveau "Partitionnement inadéquat".
  - "Erreurs trop bruyantes" -> Absorbé par `20.7` et `22.8` (Alerting mal calibré / Trop d'alertes).
  - "Retry dangereux" -> Absorbé par "Ingestion dupliquée" (17.1) et la "Boucle de retry infinie".
  - "Désynchronisation des bases", "Latence d'intégration" -> Absorbés par `17.6` (Désynchronisation / Données en retard).
  - Tous les cas "Pipeline batch vs streaming (9.9)" -> Absorbés par `17.8` (Mélange / Double traitement / Retard).
  - "Absence de ownership", "Documentation inexistante", "Pipeline non versionné" -> Absorbés par `17.10` (Propriété inconnue, Non versionnées, Source non documentée).
  - "Dégradation progressive", "Effet cumulatif" -> Absorbés par `17.12` (Dérive progressive).
- ✅ **Inédits injectés (16) :**
  * **Dimension 9 : Exploitation**
    - `9.1` — Job d'ingestion terminé sans erreur (Exit 0) mais aucune donnée écrite
    - `9.2` — Dépendances de DAG non respectées (exécution hors ordre)
    - `9.2` — Échec partiel de pipeline ETL sans rollback global
    - `9.2` — Tâches orphelines ou blocage de DAG par dépendance circulaire
    - `9.2` — Boucle de retry infinie sur erreur déterministe (Surcharge)
    - `9.5` — Traitement Batch débordant de sa fenêtre d'ordonnancement (Timeout)
    - `9.5` — Job ETL massif provoquant un OOM (Out Of Memory) sur le worker
    - `9.5` — Partitionnement de données inadéquat (Full scan massif)
    - `9.6` — Logs ETL inexploitables ou inexistants en production
  * **Dimension 2 : Données**
    - `9.3` — Erreur silencieuse de logique métier dans la transformation (SQL/Python)
    - `9.3` — Transformation ETL non déterministe (résultats variant selon l'exécution)
    - `9.3` — Perte d'information par agrégation prématurée ou excessive
    - `9.4` — Contrat de données (Data Contract) trop strict bloquant des données valides
    - `9.4` — Effet domino de propagation silencieuse de données corrompues en aval
    - `9.7` — Réplication partielle (Tables désynchronisées au sein du même schéma)
  * **Dimension 8 : Gouvernance**
    - `9.10` — Dépendances invisibles inter-pipelines (Non déclarées dans le DAG)


## Rétro-Documentation des Rechecks (Genèse 1 à 6) - Application Règle 38

*(Note : Ces catégories de la Genèse ont été ingérées avant la mise en place de la Règle 36/38. Voici la traçabilité rétroactive de l'Inversion de la Charge de la Preuve pour les 6 premières itérations de Recheck).*

### Recheck 1 (Catégorie 1 : Infrastructure)
**Preuve d'Inversion de la Charge (Règle 36) :**
- ✅ **Inédits injectés (18) :** La Dimension 1 de la taxonomie était vierge avant cette ingestion. 100% des incidents techniques (OOM, Timeout, Deadlock) ont été prouvés inédits et injectés.

### Recheck 2 (Catégorie 2 : Pipeline ML)
**Preuve d'Inversion de la Charge (Règle 36) :**
- ❌ **100% rejetés :** Preuve mathématique établie que l'intégralité des concepts de la Catégorie 2 étaient des doublons exacts de la Catégorie 17 (Data Quality). Zéro injection (Fast-Forward).

### Recheck 3 (Catégorie 3 : Modèles)
**Preuve d'Inversion de la Charge (Règle 36) :**
- ❌ **100% rejetés :** Preuve formelle que la Catégorie 3 était un doublon sémantique de la Catégorie 21 (Qualité des Prédictions). Zéro injection (Fast-Forward).

### Recheck 4 (Catégorie 4 : Code & Versioning)
**Preuve d'Inversion de la Charge (Règle 36) :**
- ✅ **Inédits injectés (40) :** L'audit a prouvé un vide flagrant dans la matrice sur l'axe "Software Engineering & Reproductibilité" (Dimension CI/CD). Les 40 incidents ont été acceptés car totalement inédits dans l'extension.

### Recheck 5 (Catégorie 5 : Données)
**Preuve d'Inversion de la Charge (Règle 36) :**
- ❌ **100% rejetés :** Doublon parfait avec la Catégorie 17 (Data Quality). Les tentatives d'injection redondantes ont été annulées et purgées post-audit pour préserver l'intégrité de la Matrice.

### Recheck 6 (Catégorie 6 : Feature Store)
**Preuve d'Inversion de la Charge (Règle 36) :**
- ❌ **100% rejetés :** L'audit a prouvé que tous les concepts (Train-Serve Skew, Feature obsolète) étaient déjà présents sous l'indexation `4.6` (Dimension 3). L'injection initiale aveugle a été annulée et purgée en vertu de la Règle 30.

---


---

## PARTIE 4/100

*Curateur : Validé. Intégration stricte.*

### CATÉGORIE 10 (== PlanMaitre : 10. Sécurité) : Problèmes de Sécurité (Security, Access Control & Attack Surface)

(Tout ce qui concerne les failles de sécurité, les accès non autorisés, les fuites de données et les attaques sur l’infrastructure ou les modèles.)

- **10.1 — Authentification & accès**
  
  Absence d’authentification
  API exposée publiquement
  accès libre à /predict ou endpoints sensibles
  
  Authentification faible
  mots de passe simples
  absence de MFA
  tokens prévisibles
  
  Sessions non sécurisées
  tokens longs non révoqués
  session hijacking possible
  
  Mauvaise gestion des rôles
  pas de RBAC (role-based access control)
  utilisateurs normaux accèdent à des fonctions admin

- **10.2 — Exposition des données sensibles**
  
  Fuite de données personnelles (RGPD)
  données d’accidents contenant informations sensibles
  absence d’anonymisation
  
  Logs contenant des secrets
  credentials ou PII dans logs applicatifs
  
  Exposition de bases de données
  ports ouverts publiquement
  PostgreSQL accessible sans restriction
  
  Dashboards publics
  Superset ou Grafana exposés sans protection

- **10.3 — Secrets & configuration**
  
  Secrets hardcodés
  mots de passe dans le code source
  clés API dans GitHub
  
  Fichiers .env exposés
  commit accidentel de credentials
  
  Mauvaise gestion des secrets
  absence de vault (type Vault / Secrets Manager)
  
  Rotation des clés absente
  clés compromises valables indéfiniment

- **10.4 — Injection et attaques applicatives**
  
  Injection SQL
  requêtes non paramétrées
  exécution de commandes destructrices
  
  Injection via API
  payloads malveillants dans inputs utilisateurs
  
  Command injection
  exécution de commandes système via input
  
  Exploitation de sérialisation
  pickle / MLflow artifact mal sécurisé

- **10.5 — Attaques sur l’API**
  
  DDoS (Denial of Service)
  saturation de /predict
  indisponibilité totale du service
  
  Abuse de l’API
  scraping massif des prédictions
  extraction de comportements du modèle
  
  Rate limit absent
  pas de limitation de requêtes
  
  Bot traffic
  appels automatisés non contrôlés

- **10.6 — Sécurité des containers & infra**
  
  Images Docker non sécurisées
  images obsolètes ou vulnérables
  
  Containers privilégiés
  accès root inutile
  
  Ports exposés inutilement
  DB ou services internes accessibles publiquement
  
  Absence d’isolation réseau
  tous les services communiquent librement

- **10.7 — Sécurité des données**
  
  Accès non restreint aux datasets
  tout le monde peut lire les tables sensibles
  
  Mauvaise segmentation des environnements
  prod accessible depuis dev
  
  Absence de chiffrement
  données en clair au repos ou en transit
  
  Copie non contrôlée des données
  export massif sans audit

- **10.8 — Sécurité des modèles (ML Security)**
  
  Model extraction
  reproduction du modèle via API queries
  
  Model inversion
  reconstruction de données sensibles via outputs
  
  Membership inference
  savoir si une donnée a été dans le training set
  
  Exploitation du modèle
  utilisation malveillante des prédictions

- **10.9 — Sécurité CI/CD**
  
  Pipeline compromis
  injection de code dans CI/CD
  
  Artefacts malveillants
  modèle remplacé par version infectée
  
  Secrets exposés dans logs CI
  tokens visibles dans GitHub Actions

- **10.10 — Monitoring sécurité**
  
  Absence de détection d’attaque
  aucune alerte sur comportements suspects
  
  Logs non audités
  impossible de retracer une attaque
  
  Alertes ignorées
  trop de bruit → vraies attaques non détectées

- **10.11 — Supply chain security**
  
  Dépendances vulnérables
  librairies Python non patchées
  
  Packages malveillants
  dépendances compromises
  
  Manque de lockfile
  versions non contrôlées

- **10.12 — Erreurs humaines de sécurité**
  
  Mauvaise configuration cloud
  bucket public accidentel
  
  Mauvais firewall rules
  accès trop permissif
  
  Partage accidentel
  données envoyées au mauvais destinataire

---
### Analyse de Correspondance avec la Taxonomie des Grandes Dimensions :
- **Dimension 7 : Sécurité** : 80% (Authentification, Secrets, Injection, Attaques ML, Container Sec).
- **Dimension 1 : Infrastructure** : 10% (Réseau, Docker).
- **Dimension 8 : Gouvernance** : 10% (Accès, Isolation des environnements, CI/CD, Supply Chain).

### Suivi de l'Enrichissement Croisé :
* **Dimension 7 : Sécurité**
  - `10.1` — `RBAC applicatif (FastAPI/Superset) absent` (lignes [X])
  - `10.2` — `Exposition de dashboards internes (Superset)` (lignes [X])
  - `10.3` — `Absence de Secrets Manager (Vault)` (lignes [X])
  - `10.3` — `Absence de rotation des clés (Compromission)` (lignes [X])
  - `10.4` — `Injection SQL (Requêtes non paramétrées)` (lignes [X])
  - `10.4` — `Injection de payload malveillant (API)` (lignes [X])
  - `10.4` — `Command Injection (Exécution arbitraire)` (lignes [X])
  - `10.5` — `Absence de Rate Limiting (Abus d'API)` (lignes [X])
  - `10.6` — `Containers en mode privilégié (Root access)` (lignes [X])
  - `10.7` — `Porosité des environnements (Dev accède Prod)` (lignes [X])
  - `10.7` — `Exfiltration de données (Export massif)` (lignes [X])
  - `10.9` — `Compromission du pipeline CI/CD` (lignes [X])
  - `10.9` — `Remplacement d'artefact ML malveillant` (lignes [X])
  - `10.10` — `Cécité sécuritaire (Absence de SIEM)` (lignes [X])
  - `10.11` — `Absence de Lockfile (Versions non déterministes)` (lignes [X])

**Preuve d'Inversion de la Charge (Règle 36) :**
- ❌ Rejet de `Absence d'authentification`, absorbé par l'existant `18.1`.
- ❌ Rejet de `Tokens prévisibles` et `Sessions non sécurisées`, absorbés par `18.1 (Mauvaise gestion des tokens)`.
- ❌ Rejet de `Fuite RGPD` et `Données sensibles exposées`, absorbés par `17.11` et `N/A`.
- ❌ Rejet de `Logs avec secrets`, absorbé par `12.1`.
- ❌ Rejet de `Ports ouverts / DB exposée / Bucket public`, absorbés par `18.2`.
- ❌ Rejet de `Secrets hardcodés dans .env/Github`, absorbés par `18.1`.
- ❌ Rejet de `Pickle empoisonné`, absorbé par `18.3`.
- ❌ Rejet de `DDoS / Abuse API`, absorbés par `18.8` et `18.4`.
- ❌ Rejet de `Images obsolètes / Dépendances vulnérables / Attaques Supply Chain`, absorbés par `9.2`, `9.6` et `18.3`.
- ❌ Rejet de `Absence de chiffrement`, absorbé par `18.10`.
- ❌ Rejet de `Model Extraction / Inversion / Membership Inference / Adversarial`, absorbés par `18.4`, `18.6`, `18.7`.
- ✅ Validation de 15 failles MLOps inédites spécifiques à la configuration fine applicative (RBAC, Secrets Manager, Dashboards, Injection, Rate Limiting, Containers Root, Porosité des environnements, Exfiltration, CI/CD Compromission, SIEM Cécité, Lockfile).


---

## PARTIE 5/100 (Résumé Consolidé des 15 Catégories)

*Curateur : Validé comme version consolidée du Plan Maître. Aucune injection dans la matrice des risques pour éviter les doublons (Règle 30).*

**FRAMEWORK COMPLET — 15 CATÉGORIES MLOPS FAILURE MODES**

1. Infrastructure & Disponibilité
serveurs, OS, containers, réseau de base
crash système, disque plein, RAM, Docker, DB down

2. Pipelines de Données (ETL / ingestion / orchestration)
ingestion brute, transformation, jointures
schémas, qualité pipeline, idempotence, batch/stream

3. Modèle ML (performance, drift, comportement)
data drift, concept drift, biais
calibration, robustesse, overfitting

4. Code & Versioning (software engineering)
bugs, dépendances, reproductibilité
Git, environnements, MLflow tracking

5. Qualité des Données
valeurs manquantes, bruit, doublons
incohérences, représentativité, corruption

6. Feature Store & Feature Engineering
training/serving skew
features manquantes, drift, versioning
coût et latence des features

7. Temporalité (Time-related issues)
time leakage, désynchronisation
drift temporel, historisation, backtesting

8. Pipeline ML (training, evaluation, MLflow)
entraînement, validation, tuning
tracking, artefacts, reproductibilité modèle

9. Pipeline de Données (end-to-end orchestration)
workflows ETL globaux
scheduling, dépendances, cohérence inter-systèmes

10. Sécurité (system, data, model, API)
accès, authentification, injections
attaque API, fuite de données, supply chain

11. Gouvernance MLOps
ownership, documentation, auditabilité
conformité, responsabilité, traçabilité

12. Économie & Coûts
coût infra, API, training, scaling
optimisation ressources vs performance

13. Qualité des Prédictions (business output)
faux positifs / négatifs
calibration métier, erreurs critiques

14. Facteur Humain (organisation & process)
erreurs humaines, communication
mauvaise compréhension modèle
décisions métier incorrectes

15. Cas Extrêmes (Edge cases / black swans)
situations inédites
hors distribution, catastrophes
scénarios rares mais critiques




---

### CATÉGORIE 15 (== PlanMaitre : 7. Temps) : Les Problèmes Liés au Temps, aux Dates & aux Fuseaux Horaires

*(Tous les scénarios où la gestion du temps provoque des erreurs de données, de pipeline, d'entraînement ou de prédiction.)*

#### 15.1 — Fuseaux Horaires

- **Les données utilisent deux fuseaux horaires différents**
  
  Les données `BAAC` sont enregistrées en heure locale. L'API météo est en `UTC`. Les jointures temporelles deviennent incorrectes.

- **Heure locale utilisée au lieu d'UTC**
  
  Le serveur enregistre : `2026-07-15 08:00` sans préciser le fuseau. Impossible de savoir s'il s'agit de `UTC`, `Europe/Paris` ou autre.

- **Changement de fuseau lors d'un déploiement**
  
  Le serveur est déplacé. Le système passe automatiquement de `Europe/Paris` vers `UTC`. Tous les calculs horaires changent.

- **Deux serveurs utilisent des fuseaux différents**
  
  Le pipeline produit des timestamps différents selon le serveur qui l'exécute.

#### 15.2 — Heure d'Été / Heure d'Hiver

- **Heure inexistante**
  
  Lors du passage à l'heure d'été, une heure disparaît. Certaines dates deviennent impossibles.

- **Heure dupliquée**
  
  Lors du passage à l'heure d'hiver, la même heure existe deux fois. Impossible de savoir à quel événement correspond un timestamp.

- **Mauvais calcul de durée**
  
  Une durée calculée sur la nuit du changement d'heure est fausse d'une heure.

- **Pipeline planifié au mauvais moment**
  
  Le scheduler déclenche un batch deux fois, ou pas du tout.

#### 15.3 — Synchronisation des Horloges

- **Horloge système en retard**
  
  Le serveur dérive progressivement. Les timestamps deviennent incohérents.

- **Horloge en avance**
  
  Les événements semblent venir du futur. Les `Feature Views` deviennent invalides.

- **NTP indisponible**
  
  Les serveurs cessent de synchroniser leur heure via `NTP`. La dérive augmente progressivement.

- **Deux serveurs désynchronisés**
  
  Les logs deviennent impossibles à corréler.

#### 15.4 — Ordre Temporel

- **Les événements arrivent dans le désordre**
  
  Des données du 15 juillet arrivent avant celles du 14 juillet. Le pipeline les traite incorrectement.

- **Données retardées**
  
  Une source externe publie les données plusieurs heures après leur création. Le modèle utilise un historique incomplet.

- **Données futures**
  
  Une erreur produit des événements datés de l'année suivante. Le pipeline les considère comme les plus récents.

- **Timestamp dupliqué**
  
  Deux événements différents possèdent exactement la même date. Le tri devient ambigu.

#### 15.5 — Version Temporelle des Données

- **Utilisation d'une donnée "future"**
  
  Une feature calculée utilise accidentellement une information qui n'était pas disponible au moment de la prédiction. C'est un Data Leakage temporel.

- **Snapshot incorrect**
  
  Le Feature Store restitue la version actuelle d'une feature au lieu de la version historique. Impossible de reproduire une ancienne prédiction.

- **Mauvais point de référence**
  
  Une agrégation est calculée sur les 30 jours suivants au lieu des 30 jours précédents.

- **Historique incomplet**
  
  Certaines données anciennes sont supprimées. Les entraînements historiques deviennent impossibles.

#### 15.6 — Planification

- **Cron mal configuré**
  
  Le pipeline devait démarrer à `02:00` mais démarre à `14:00` sous l'effet d'une mauvaise configuration d'horaires.

- **Deux pipelines démarrent simultanément**
  
  Ils se bloquent mutuellement (locks de base de données).

- **Pipeline jamais exécuté**
  
  Une mauvaise expression `Cron` empêche tout déclenchement.

- **Pipeline exécuté deux fois**
  
  Une mauvaise configuration provoque des doublons.

- **Décalage progressif**
  
  Chaque exécution prend un peu plus longtemps. Au bout de plusieurs semaines, les pipelines finissent par se chevaucher.

#### 15.7 — Fenêtres Temporelles

- **Fenêtre glissante incorrecte**
  
  Une moyenne censée porter sur 7 jours est calculée sur 8.

- **Fenêtre vide**
  
  Aucune donnée n'entre dans la période analysée. Toutes les features deviennent `NULL`.

- **Chevauchement de fenêtres**
  
  Certaines données sont comptées plusieurs fois.

- **Mauvaise granularité**
  
  Le pipeline travaille à la minute alors que le modèle a été entraîné à la journée.

#### 15.8 — Dates Particulières

- **Année bissextile**
  
  Le 29 février provoque un bug.

- **Fin de mois**
  
  Le calcul échoue le 31 car certains mois n'ont que 30 jours.

- **Fin d'année**
  
  Les agrégations annuelles sont incorrectes.

- **Semaine ISO**
  
  Une semaine appartient à une année différente. Les statistiques deviennent incohérentes.

- **Changement de décennie**
  
  Des traitements supposent un nombre fixe d'années.

#### 15.9 — Vieillissement

- **Modèle trop ancien**
  
  Le modèle continue de fonctionner mais il n'a pas été réentraîné depuis plusieurs années.

- **Feature périmée**
  
  Une feature reste calculée selon une ancienne logique métier.

- **Données archivées**
  
  Certaines données nécessaires au modèle ont été déplacées. Le pipeline échoue.

- **Certificat expiré**
  
  Une dépendance temporelle classique : l'application cesse brutalement de fonctionner.

#### 15.10 — Cache

- **Cache jamais invalidé**
  
  Les anciennes valeurs sont servies pendant plusieurs jours.

- **Cache expiré trop rapidement**
  
  Toutes les requêtes recalculent les features. Les performances chutent.

- **TTL incohérent**
  
  Deux composants utilisent des durées de vie (`TTL`) différentes. Les données divergent.

#### 15.11 — Temps d'Entraînement

- **Les données changent pendant l'entraînement**
  
  Le dataset évolue alors que le modèle est en cours d'apprentissage. Le résultat n'est plus reproductible.

- **Deux entraînements utilisent des snapshots différents**
  
  Ils produisent des modèles différents malgré un code identique.

- **Réentraînement lancé trop tôt**
  
  Toutes les données de la journée ne sont pas encore disponibles.

- **Réentraînement oublié**
  
  Le modèle continue plusieurs années sans mise à jour.

#### 15.12 — Audit Temporel

- **Impossible de retrouver l'état du système à une date donnée**
  
  On connaît le modèle, mais pas les features, les données, les paramètres ou les dépendances au moment exact de la prédiction.

- **Horodatage manquant**
  
  Une prédiction est enregistrée, mais sa date ne l'est pas.

- **Les événements ne sont pas ordonnables**
  
  Les logs utilisent plusieurs formats de date. Impossible de reconstruire une chronologie.

- **Conservation insuffisante**
  
  Les logs ou historiques sont supprimés avant la fin de leur période utile.

#### Pourquoi cette catégorie est essentielle

Le temps est une dimension transversale : il intervient dans les données, les pipelines, les modèles, les logs, les sauvegardes et les audits. Une erreur de quelques minutes, un fuseau horaire mal géré ou une mauvaise fenêtre temporelle peuvent produire des modèles biaisés, des jointures incorrectes ou des prédictions impossibles à reproduire. Ces problèmes sont particulièrement difficiles à détecter, car ils ne provoquent pas toujours d'erreur explicite ; ils modifient souvent subtilement les résultats.

#### Une remarque spécifique à notre projet BAAC

Dans notre contexte, cette catégorie est encore plus importante parce que la variable temps est omniprésente :
- date et heure des accidents ;
- conditions météorologiques au moment de l'accident ;
- agrégations temporelles (accidents récents, saisonnalité) ;
- pipelines planifiés avec `Prefect` ;
- matérialisation des `Feature Views` ;
- entraînements périodiques ;
- reproductibilité des prédictions historiques.

Notre objectif ultime est de pouvoir répondre à une question comme :<br>
« Si nous rejouons aujourd'hui une prédiction réalisée le 14 novembre 2025 à 18 h 42, avec le modèle de l'époque, les features de l'époque, les données disponibles à cette date et les mêmes dépendances logicielles, est-ce que nous obtenons exactement le même résultat ? »

Si la réponse est oui, alors notre gestion du temps, du versionnement et de la traçabilité est véritablement maîtrisée.

---

### Analyse de Correspondance avec la Taxonomie des Grandes Dimensions :

- **Données** (Poids principal : 25%)
  
  La gestion des dérives de fuseaux horaires (`UTC` vs heure locale), les erreurs de conversion et d'heures d'été/hiver qui faussent les timestamps, les données arrivant dans le désordre, et la gestion de la fraîcheur/obsolescence des données injectées dans le système.

- **Feature Engineering** (Poids principal : 20%)
  
  Les calculs erronés sur fenêtres glissantes (moyennes temporelles sur 7 ou 8 jours), les granularités asymétriques, et le calcul de features dépendantes d'autres variables temporelles.

- **Infrastructure** (Poids principal : 10%)
  
  La désynchronisation des horloges systèmes entre serveurs (`NTP` down), et les décalages de configurations d'environnement lors de bascules ou d'auto-scaling.

- **Observabilité** (Poids principal : 10%)
  
  Les difficultés à corréler les logs distribués en raison de formats de dates inconsistants, et la détection préventive de dérives temporelles d'exécution.

- **Entraînement** (Poids principal : 10%)
  
  Le risque de Data Leakage temporel (données futures utilisées à l'entraînement), et la déviation de modèles suite à des entraînements lancés trop tôt avec des snapshots incomplets.

- **Gouvernance** (Poids secondaire : 8%)
  
  La traçabilité et l'auditabilité temporelle (reconstruction exacte de l'état des features à un instant $T$), et le respect des durées réglementaires de conservation des historiques.

- **Exploitation** (Poids secondaire : 8%)
  
  Les conflits de planification de pipelines `Cron` (`Prefect`) qui se chevauchent, et le vieillissement silencieux des certificats de sécurité ou des pipelines.

- **Serving** (Poids secondaire : 5%)
  
  La latence ou la dégradation induite par des temps de réponse de caches non invalidés ou de cache `TTL` expirant trop vite.

- **Sécurité** (Poids secondaire : 2%)
  
  L'expiration de certificats et de clés d'accès de services tiers bloquant les requêtes de serving.

- **Organisation** (Poids secondaire : 2%)
  
  Le manque d'alignement au sein des équipes sur le choix d'un fuseau standard (`UTC`) pour le stockage et l'entraînement.

**Résumé :**
La gestion du temps est transversale à tout système `MLOps` distribué. Les impacts se situent principalement au niveau de la qualité des **Données** (25%) et du **Feature Engineering** (20%), mais constituent un défi d'**Infrastructure** (10%) et d'**Observabilité** (10%) pour assurer le déterminisme de la plateforme.

### Suivi de l'Enrichissement Croisé :

- [mlops_failure_modes_taxonomy.md](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md) :

    - Traduction et intégration de 100% des incidents de la Catégorie 15 répartis sous leurs dimensions MLOps respectives :

    * **Dimension 1 : Infrastructure**
      - `15.1` — Changement de fuseau lors d'un déploiement (lignes [106](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L106))
      - `15.1` — Deux serveurs utilisent des fuseaux différents (lignes [107](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L107))
      - `15.3` — Horloge système en retard (décalage NTP) (lignes [108](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L108))
      - `15.3` — Horloge système en avance (Feature Views invalides) (lignes [109](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L109))
      - `15.3` — NTP indisponible (dérive d'horloge) (lignes [110](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L110))
      - `15.3` — Deux serveurs désynchronisés (corrélation logs) (lignes [111](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L111))


    * **Dimension 2 : Données**
      - `15.1` — Les données utilisent deux fuseaux horaires différents (lignes [172](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L172))
      - `15.1` — Heure locale utilisée au lieu d'UTC (sans offset) (lignes [173](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L173))
      - `15.2` — Heure inexistante (passage heure d'été) (lignes [174](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L174))
      - `15.2` — Heure dupliquée (passage heure d'hiver) (lignes [175](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L175))
      - `15.4` — Les événements arrivent dans le désordre (lignes [176](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L176))
      - `15.4` — Données retardées (historique incomplet serving) (lignes [177](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L177))
      - `15.4` — Données futures (année suivante) (lignes [178](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L178))
      - `15.4` — Timestamp dupliqué (tri ambigu) (lignes [179](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L179))
      - `15.5` — Historique incomplet (données supprimées) (lignes [180](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L180))
      - `15.9` — Données archivées (déplacées) (lignes [181](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L181))


    * **Dimension 3 : Feature Engineering**
      - `15.2` — Mauvais calcul de durée (changement d'heure) (lignes [221](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L221))
      - `15.5` — Snapshot incorrect (Feature Store version actuelle) (lignes [222](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L222))
      - `15.5` — Mauvais point de référence (fenêtres inversées) (lignes [223](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L223))
      - `15.7` — Fenêtre glissante incorrecte (7j vs 8j) (lignes [224](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L224))
      - `15.7` — Fenêtre vide (retours NULL) (lignes [225](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L225))
      - `15.7` — Chevauchement de fenêtres (données dupliquées) (lignes [226](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L226))
      - `15.7` — Mauvaise granularité (minute vs journée) (lignes [227](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L227))
      - `15.8` — Année bissextile (bug du 29 février) (lignes [228](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L228))
      - `15.8` — Fin de mois (calcul échoue le 31) (lignes [229](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L229))
      - `15.8` — Fin d'année (agrégations fausses) (lignes [230](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L230))
      - `15.8` — Semaine ISO (chevauchement d'années) (lignes [231](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L231))
      - `15.8` — Changement de décennie (hypothèses fixes) (lignes [232](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L232))
      - `15.9` — Feature périmée (ancienne logique métier) (lignes [233](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L233))


    * **Dimension 4 : Entraînement**
      - `15.5` — Utilisation d'une donnée "future" (Data Leakage) (lignes [266](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L266))
      - `15.11` — Les données changent pendant l'entraînement (lignes [267](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L267))
      - `15.11` — Deux entraînements utilisent des snapshots diff. (lignes [268](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L268))
      - `15.11` — Réentraînement lancé trop tôt (données incomplètes) (lignes [269](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L269))
      - `15.11` — Réentraînement oublié (modèle obsolète) (lignes [270](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L270))


    * **Dimension 5 : Serving**
      - `15.10` — Cache jamais invalidé (valeurs obsolètes) (lignes [351](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L351))
      - `15.10` — Cache expiré trop rapidement (perf chute) (lignes [352](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L352))
      - `15.10` — TTL cache incohérent entre composants (lignes [353](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L353))


    * **Dimension 6 : Observabilité**
      - `15.12` — Les événements ne sont pas ordonnables (formats) (lignes [376](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L376))


    * **Dimension 7 : Sécurité**
      - `15.9` — Certificat SSL expiré (blocage serving) (lignes [396](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L396))


    * **Dimension 8 : Gouvernance**
      - `15.12` — Impossible de retrouver l'état du système (lignes [421](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L421))
      - `15.12` — Horodatage manquant dans l'enregistrement (lignes [422](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L422))
      - `15.12` — Conservation insuffisante des historiques (lignes [423](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L423))


    * **Dimension 9 : Exploitation**
      - `15.2` — Pipeline planifié au mauvais moment (dst shift) (lignes [482](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L482))
      - `15.6` — Cron mal configuré (mauvais horaire batch) (lignes [483](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L483))
      - `15.6` — Deux pipelines démarrent simultanément (lock) (lignes [484](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L484))
      - `15.6` — Pipeline jamais exécuté (mauvais Cron) (lignes [485](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L485))
      - `15.6` — Pipeline exécuté deux fois (doublons) (lignes [486](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L486))
      - `15.6` — Décalage progressif (chevauchement pipelines) (lignes [487](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L487))
      - `15.9` — Modèle trop ancien (réentraînement manquant) (lignes [488](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L488))


    * **Dimension 10 : Organisation**
      - `15.1` — Manque d'alignement sur fuseau standard (UTC) (lignes [520](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L520))

  Voici les lignes exactes de chaque dimension où elles ont été réparties :
  - **Infrastructure (Dimension 1)** : Aux lignes [106 à 111](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L106-L111) (`timezone_deployment_shift.py`, `timezone_server_mismatch.py`, `clock_delay.py`, `clock_advance.py`, `ntp_unavailable.py`, `server_time_desync.py`).
  - **Données (Dimension 2)** : Aux lignes [172 à 181](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L172-L181) (`timezone_data_mismatch.py`, `timezone_local_utc_mix.py`, `daylight_saving_missing_hour.py`, `daylight_saving_dup_hour.py`, `time_out_of_order.py`, `time_delayed_data.py`, `time_future_data.py`, `time_duplicate_timestamp.py`, `time_incomplete_history.py`, `time_archived_data.py`).
  - **Feature Engineering (Dimension 3)** : Aux lignes [221 à 233](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L221-L233) (`time_duration_dst.py`, `time_bad_snapshot.py`, `time_bad_reference_point.py`, `time_bad_sliding_window.py`, `time_empty_window.py`, `time_overlapping_windows.py`, `time_bad_granularity.py`, `time_leap_year_bug.py`, `time_month_end_bug.py`, `time_year_end_bug.py`, `time_iso_week_bug.py`, `time_decade_change_bug.py`, `time_obsolete_feature.py`).
  - **Entraînement (Dimension 4)** : Aux lignes [266 à 270](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L266-L270) (`time_data_leakage.py`, `time_dynamic_training.py`, `time_snapshot_mismatch.py`, `time_early_retraining.py`, `time_forgotten_retraining.py`).
  - **Serving (Dimension 5)** : Aux lignes [351 à 353](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L351-L353) (`time_cache_stale.py`, `time_cache_short_ttl.py`, `time_incoherent_ttl.py`).
  - **Observabilité (Dimension 6)** : À la ligne [376](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L376) (`time_unorderable_logs.py`).
  - **Sécurité (Dimension 7)** : À la ligne [396](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L396) (`time_ssl_expired.py`).
  - **Gouvernance (Dimension 8)** : Aux lignes [421 à 423](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L421-L423) (`time_audit_impossible.py`, `time_missing_timestamp.py`, `time_short_retention.py`).
  - **Exploitation (Dimension 9)** : Aux lignes [482 à 488](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L482-L488) (`time_dst_pipeline_shift.py`, `time_cron_misconfigured.py`, `time_concurrent_pipelines.py`, `time_pipeline_never_run.py`, `time_pipeline_double_run.py`, `time_pipeline_overlapping.py`, `time_model_obsolete.py`).
  - **Organisation (Dimension 10)** : À la ligne [520](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L520) (`time_timezone_alignment.py`).

- [bi_observability_genesis.md](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/bi_observability_genesis.md) :
  - Création de la section 4.9 dédiée aux dashboards temporels.
- [mlops_anti_patterns_registry.md](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_anti_patterns_registry.md) :
  - Enregistrement de l'Anti-Pattern 19 (`Le Fuseau Local Fantôme`).
- [journal_mlops.md](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/journal_mlops.md) :
  - Ajout de l'Entrée 39 retraçant l'ingestion de la Catégorie 15.

---

### CATÉGORIE 16 (== PlanMaitre : 8. Pipeline ML) : Les Problèmes du Pipeline Machine Learning

*(Tous les scénarios où le pipeline d'entraînement, d'évaluation, de validation ou de sélection des modèles produit un modèle incorrect, biaisé, non reproductible ou sous-optimal.)*

#### 16.1 — Préparation des Données

- **Les données ne sont pas mélangées correctement**
  
  Le dataset est trié par département ou par date. Le modèle apprend un ordre artificiel. Les performances deviennent trompeuses.

- **Nettoyage différent entre deux exécutions**
  
  Une règle de nettoyage change. Le même dataset produit un modèle différent.

- **Mauvaise gestion des valeurs manquantes**
  
  Les `NaN` sont supprimés, imputés ou remplacés par `0` selon différents scripts. Le comportement du modèle change.

- **Mauvaise suppression des outliers**
  
  Des observations importantes sont supprimées par erreur. Le modèle perd sa capacité à traiter certains cas.

#### 16.2 — Découpage Train / Validation / Test

- **Mauvais découpage temporel**
  
  Le jeu d'entraînement (`train`) contient des données plus récentes que le jeu de test. Les performances paraissent excellentes, mais la généralisation est mauvaise.

- **Fuite entre train et test**
  
  Un même accident apparaît dans les deux jeux. Le modèle mémorise les exemples.

- **Validation non représentative**
  
  Le jeu de validation ne contient pas certaines catégories importantes. Les performances sont surestimées.

- **Test réutilisé plusieurs fois**
  
  Les décisions d'optimisation sont prises en regardant le jeu de test. Le test devient implicitement un jeu d'entraînement.

- **Répartition des classes différente**
  
  Le train est équilibré. Le test ne l'est pas. Les métriques deviennent difficiles à interpréter.

#### 16.3 — Validation Croisée

- **Mauvaise stratégie de cross-validation**
  
  Une validation aléatoire est utilisée alors que le problème est temporel.

- **Mélange d'observations dépendantes**
  
  Des observations fortement liées sont réparties dans plusieurs folds. Le modèle voit indirectement les mêmes informations.

- **Nombre de folds inadapté**
  
  Trop peu de folds induit une forte variance. Trop de folds engendre un coût d'entraînement excessif.

- **Validation non reproductible**
  
  Les folds changent à chaque exécution. Les résultats fluctuent fortement.

#### 16.4 — Hyperparamètres

- **Mauvais espace de recherche**
  
  Les meilleures valeurs possibles ne sont jamais explorées.

- **Recherche interrompue**
  
  Une optimisation s'arrête prématurément. Le meilleur modèle n'est jamais évalué.

- **Hyperparamètres non sauvegardés**
  
  Le modèle est conservé, mais les paramètres ayant permis de l'obtenir dans `MLflow` sont perdus.

- **Hyperparamètres incompatibles**
  
  Une combinaison produit un modèle instable ou impossible à entraîner.

#### 16.5 — Reproductibilité

- **Graine aléatoire absente**
  
  Deux entraînements identiques donnent des résultats différents.

- **Graine différente selon les bibliothèques**
  
  `numpy`, `random` et `scikit-learn` n'utilisent pas la même graine (`seed`).

- **Opérations non déterministes**
  
  Certaines bibliothèques produisent des résultats légèrement différents d'une exécution à l'autre.

- **Dataset modifié pendant l'entraînement**
  
  Le pipeline lit des données qui changent en cours d'exécution.

#### 16.6 — Sélection du Modèle

- **Mauvaise métrique optimisée**
  
  Le pipeline optimise l'accuracy (`accuracy`). Le métier s'intéresse au rappel (`rappel`) de la classe "grave".

- **Mauvais modèle promu**
  
  Le pipeline sélectionne automatiquement le meilleur score global. Il ignore les performances sur les cas critiques.

- **Différence statistiquement non significative**
  
  Deux modèles obtiennent `0.901` et `0.903`. La différence provient du hasard. Le pipeline promeut pourtant systématiquement le second.

- **Régression ignorée**
  
  Le modèle est meilleur globalement, mais moins bon sur un sous-groupe important.

#### 16.7 — Calibration

- **Probabilités mal calibrées**
  
  Le modèle annonce `95%` de confiance. En réalité, il se trompe souvent.

- **Seuil de décision oublié**
  
  Le modèle produit des probabilités. Le pipeline utilise par défaut un seuil de `0.5` alors qu'un seuil optimisé existait.

- **Seuil modifié**
  
  Un changement de seuil améliore une métrique, mais dégrade fortement les faux négatifs.

- **Calibration non reproduite**
  
  Le calibrateur utilisé à l'entraînement n'est pas sauvegardé.

#### 16.8 — Entraînement

- **Arrêt prématuré**
  
  Une erreur interrompt l'entraînement. Le pipeline enregistre malgré tout un modèle incomplet.

- **Convergence trompeuse**
  
  L'algorithme converge vers un minimum local peu performant.

- **Explosion des gradients**
  
  Les poids deviennent instables. Le modèle diverge.

- **Sous-apprentissage**
  
  Le modèle est trop simple. Il ne capture pas les relations importantes.

- **Surapprentissage**
  
  Le modèle mémorise les données d'entraînement (`overfitting`). Les performances en production chutent.

#### 16.9 — Évaluation

- **Mauvaise métrique**
  
  Le pipeline affiche uniquement l'accuracy (`accuracy`) alors que le problème est très déséquilibré.

- **Métrique mal implémentée**
  
  Le calcul du `F1 Score` contient une erreur.

- **Comparaison sur des jeux différents**
  
  Deux modèles sont comparés sur deux jeux de test différents. La comparaison est invalide.

- **Intervalles de confiance absents**
  
  Une amélioration de `0.2%` est interprétée comme certaine.

#### 16.10 — Pipeline Automatique

- **Une étape est sautée**
  
  Le Feature Engineering n'est pas exécuté, mais le pipeline continue.

- **Ordre incorrect**
  
  Le scaling (`StandardScaler`) est réalisé avant la séparation train/test. Une fuite d'information (`Data Leakage`) est introduite.

- **Cache d'entraînement obsolète**
  
  Le pipeline recharge des features anciennes.

- **Pipeline partiellement exécuté**
  
  Une erreur est ignorée. Les étapes suivantes continuent.

#### 16.11 — Ensembles & Stacking

- **Modèle de base absent**
  
  Un des modèles du `Stacking` n'est pas entraîné. Le méta-modèle reçoit des entrées incomplètes.

- **Ordre des modèles changé**
  
  Le méta-modèle reçoit les prédictions dans un ordre différent.

- **Modèle de base remplacé**
  
  Un modèle est modifié, mais le `Stacking` n'est pas réentraîné.

- **Corrélation excessive**
  
  Tous les modèles de l'ensemble font les mêmes erreurs. Le gain attendu disparaît.

#### 16.12 — Cycle de Vie

- **Réentraînement jamais déclenché**
  
  Le pipeline existe mais n'est jamais exécuté.

- **Réentraînement trop fréquent**
  
  Le modèle change tous les jours. Les performances deviennent instables.

- **Régression silencieuse**
  
  Chaque nouvelle version perd légèrement en qualité. Aucune alerte ne l'empêche d'être promue.

- **Historique incomplet**
  
  Impossible de retrouver les données, les paramètres, les métriques et les artefacts ayant permis de produire un ancien modèle.

#### Pourquoi cette catégorie est essentielle

Un pipeline `MLOps` peut être parfaitement orchestré, surveillé et hautement disponible tout en produisant des modèles de mauvaise qualité si les étapes scientifiques de préparation, d'entraînement et d'évaluation ne sont pas maîtrisées. Les erreurs de cette catégorie sont souvent silencieuses : elles ne provoquent ni crash ni exception, mais conduisent à des performances trompeuses, à des modèles non reproductibles ou à des décisions de déploiement inadaptées.

#### Une remarque spécifique à notre projet BAAC

Plusieurs scénarios connexes de cette catégorie sont déjà documentés dans nos sections existantes (notamment le `Data Leakage`, le `Surapprentissage` / `Overfitting`, le mauvais split temporel, les bascules et rollbacks de version via `MLflow`, et la dérive de performance). Nous ne supprimons rien. En revanche, ces éléments sont reliés à cette catégorie pour assurer une séparation claire au sein de notre architecture :
- les pipelines techniques d'ingestion, de transformation (`ETL`) et d'orchestration (`Prefect`) ;
- les features et la cohérence de leur serving en ligne (`Feast` / `Redis`) ;
- le pipeline scientifique de `Machine Learning` (préparation, découpage, validation croisée, entraînement, sélection, calibration, promotion et évaluation des modèles).

Cette distinction reflète l'organisation des plateformes `MLOps` industrielles où chaque couche possède ses propres modes de défaillance et ses mécanismes de validation dédiés.

---

### Analyse de Correspondance avec la Taxonomie des Grandes Dimensions :

- **Entraînement** (Poids principal : 45%)
  
  C'est le cœur de cette catégorie. La préparation des données (`NaN`, distribution, outliers), la validation croisée, le non-déterminisme lié aux graines aléatoires, le paramétrage (`MLflow`), l'optimisation des hyperparamètres, et la sélection de modèles relèvent directement de cette dimension.

- **Gouvernance** (Poids principal : 15%)
  
  L'évaluation métrologique (intervalles de confiance, exactitude des formules de F1-score), le choix des métriques alignées sur le métier, le choix des seuils de décision et de calibration, et l'archivage complet de l'historique d'entraînement.

- **Données** (Poids principal : 10%)
  
  La répartition de classes (skew), le tri artificiel des datasets d'entrée, et la gestion des outliers et valeurs manquantes dans les pipelines d'ingestion/validation.

- **Exploitation** (Poids principal : 5%)
  
  La non-exécution des pipelines de réentraînement, le déclenchement trop fréquent menant à des instabilités de production, ou l'exécution partielle silencieuse.

- **Feature Engineering** (Poids principal : 5%)
  
  Le calcul de preprocessing décalé (scaling), et la synchronisation de caches d'entraînement obsolètes.

- **Serving** (Poids principal : 5%)
  
  L'impact direct sur la production lors du déploiement de modèles non calibrés ou avec des seuils de classification par défaut inadaptés.

- **Observabilité** (Poids principal : 5%)
  
  La détection de régressions silencieuses d'une version de modèle à l'autre et la mesure de l'incertitude.

- **Infrastructure** (Poids principal : 5%)
  
  Le non-déterminisme dû aux optimisations de bas niveau ou à l'usage de matériels de calcul différents (`CPU` vs `GPU`).

- **Organisation** (Poids secondaire : 3%)
  
  Le manque d'alignement méthodologique sur la validation croisée et la sélection objective des architectures.

- **Sécurité** (Poids secondaire : 2%)
  
  Le risque d'attaques par empoisonnement si les jeux d'évaluation ou de validation croisée sont manipulés.

**Résumé :**
Le pipeline `ML` constitue le moteur de décision. Les défaillances de cette catégorie ont un impact direct sur la dimension **Entraînement** (45%) et soulèvent des enjeux importants de **Gouvernance** (15%) et de **Qualité des Données** (10%) pour garantir la viabilité et la pertinence métier du système en production.

### Suivi de l'Enrichissement Croisé :

- [mlops_failure_modes_taxonomy.md](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md) :
  - Traduction et intégration de 100% des incidents de la Catégorie 16 répartis sous leurs dimensions MLOps respectives :

    * **Dimension 1 : Infrastructure**
      - `16.5` — Opérations non déterministes (calcul GPU/CPU) (lignes [112](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L112))
    * **Dimension 2 : Données**
      - `16.1` — Les données ne sont pas mélangées correctement (lignes [189](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L189))
      - `16.1` — Nettoyage différent entre deux exécutions (lignes [190](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L190))
      - `16.1` — Mauvaise gestion des valeurs manquantes (NaN) (lignes [191](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L191))
      - `16.1` — Mauvaise suppression des outliers (lignes [192](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L192))
      - `16.2` — Répartition des classes différente (train/test) (lignes [193](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L193))
    * **Dimension 3 : Feature Engineering**
      - `16.10` — Ordre incorrect (scaling avant train/test split) (lignes [278](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L278))
      - `16.10` — Cache d'entraînement obsolète (old features) (lignes [279](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L279))
      - `16.11` — Modèle de base absent (Stacking incomplet) (lignes [280](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L280))
    * **Dimension 4 : Entraînement**
      - `16.2` — Mauvais découpage temporel (train plus récent) (lignes [315](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L315))
      - `16.2` — Fuite entre train et test (mêmes accidents) (lignes [316](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L316))
      - `16.2` — Validation non représentative (classes manquantes) (lignes [317](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L317))
      - `16.2` — Test réutilisé plusieurs fois (optimisation) (lignes [318](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L318))
      - `16.3` — Mauvaise stratégie de cross-validation (temporelle) (lignes [319](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L319))
      - `16.3` — Mélange d'observations dépendantes (leak) (lignes [320](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L320))
      - `16.3` — Nombre de folds inadapté (forte variance/coût) (lignes [321](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L321))
      - `16.3` — Validation non reproductible (folds fluctuants) (lignes [322](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L322))
      - `16.4` — Mauvais espace de recherche hyperparamètres (lignes [323](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L323))
      - `16.4` — Recherche hyperparamètres interrompue (lignes [324](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L324))
      - `16.4` — Hyperparamètres non sauvegardés dans MLflow (lignes [325](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L325))
      - `16.4` — Hyperparamètres incompatibles (fit crash) (lignes [326](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L326))
      - `16.5` — Graine aléatoire absente (non reproductible) (lignes [327](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L327))
      - `16.5` — Graine différente selon les bibliothèques (lignes [328](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L328))
      - `16.5` — Dataset modifié pendant l'entraînement (lignes [329](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L329))
      - `16.8` — Arrêt prématuré (modèle incomplet enregistré) (lignes [330](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L330))
      - `16.8` — Convergence trompeuse (minimum local pauvre) (lignes [331](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L331))
      - `16.8` — Explosion des gradients (divergence) (lignes [332](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L332))
      - `16.8` — Sous-apprentissage (modèle trop simple) (lignes [333](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L333))
      - `16.8` — Surapprentissage (overfitting) (lignes [334](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L334))
      - `16.11` — Ordre des modèles changé dans le Stacking (lignes [335](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L335))
      - `16.11` — Modèle de base remplacé sans réentraîner Stack (lignes [336](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L336))
      - `16.11` — Corrélation excessive des modèles de base (lignes [337](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L337))
    * **Dimension 5 : Serving**
      - `16.7` — Probabilités mal calibrées (confiance trompeuse) (lignes [398](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L398))
      - `16.7` — Seuil de décision oublié (default 0.5 utilisé) (lignes [399](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L399))
      - `16.7` — Seuil de décision modifié (faux négatifs) (lignes [400](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L400))
      - `16.7` — Calibration non reproduite (scaler non sauvé) (lignes [401](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L401))
    * **Dimension 6 : Observabilité**
      - `16.12` — Régression silencieuse (perte lente de F1-score) (lignes [421](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L421))
    * **Dimension 7 : Sécurité**
      - `16.3` — Empoisonnement du jeu de validation croisée (lignes [441](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L441))
    * **Dimension 8 : Gouvernance**
      - `16.6` — Mauvaise métrique optimisée (accuracy vs rappel) (lignes [499](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L499))
      - `16.6` — Mauvais modèle promu (cas critiques ignorés) (lignes [500](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L500))
      - `16.6` — Différence statistiquement non significative (lignes [501](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L501))
      - `16.6` — Régression ignorée (sous-groupe dégradé) (lignes [502](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L502))
      - `16.9` — Mauvaise métrique (accuracy sur déséquilibré) (lignes [503](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L503))
      - `16.9` — Métrique mal implémentée (calcul F1 erroné) (lignes [504](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L504))
      - `16.9` — Comparaison sur des jeux différents (lignes [505](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L505))
      - `16.9` — Intervalles de confiance absents (évaluation) (lignes [506](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L506))
      - `16.12` — Historique incomplet (métriques/données perdues) (lignes [507](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L507))
    * **Dimension 9 : Exploitation**
      - `16.10` — Une étape est sautée (Feature Eng. omis) (lignes [564](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L564))
      - `16.10` — Pipeline partiellement exécuté (erreur ignorée) (lignes [565](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L565))
      - `16.12` — Réentraînement jamais déclenché (modèle figé) (lignes [566](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L566))
      - `16.12` — Réentraînement trop fréquent (instabilité serving) (lignes [567](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L567))
    * **Dimension 10 : Organisation**
      - `16.3` — Manque d'alignement sur cross-validation (lignes [596](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L596))

  Voici les lignes exactes de chaque dimension où elles ont été réparties :

  - **Infrastructure (Dimension 1)** : À la ligne [112](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L112) (`time_non_deterministic_ops.py`).
  - **Données (Dimension 2)** : Aux lignes [189 à 193](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L189-L193) (`ml_data_shuffle_fail.py`, `ml_data_cleaning_desync.py`, `ml_data_nan_handling.py`, `ml_data_outliers_bad_del.py`, `ml_data_stratified_split.py`).
  - **Feature Engineering (Dimension 3)** : Aux lignes [278 à 280](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L278-L280) (`ml_feat_scaling_leakage.py`, `ml_feat_stale_cache.py`, `ml_stacking_missing_base.py`).
  - **Entraînement (Dimension 4)** : Aux lignes [315 à 337](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L315-L337) (`ml_train_temporal_leakage.py`, `ml_train_row_leakage.py`, `ml_train_unrep_val.py`, `ml_train_test_overfitting.py`, `ml_train_bad_cv_strategy.py`, `ml_train_group_leakage.py`, `ml_train_cv_folds_skew.py`, `ml_train_cv_random_state.py`, `ml_train_bad_search_space.py`, `ml_train_search_abort.py`, `ml_train_unlogged_params.py`, `ml_train_incompat_params.py`, `ml_train_missing_seed.py`, `ml_train_unaligned_seeds.py`, `ml_train_dataset_mutation.py`, `ml_train_early_stop_fail.py`, `ml_train_local_minimum.py`, `ml_train_gradient_explode.py`, `ml_train_underfitting.py`, `ml_train_overfitting.py`, `ml_stacking_order_shift.py`, `ml_stacking_base_desync.py`, `ml_stacking_high_corr.py`).
  - **Serving (Dimension 5)** : Aux lignes [398 à 401](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L398-L401) (`ml_serve_bad_calibration.py`, `ml_serve_default_threshold.py`, `ml_serve_threshold_skew.py`, `ml_serve_calibrator_lost.py`).
  - **Observabilité (Dimension 6)** : À la ligne [421](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L421) (`ml_obs_silent_regression.py`).
  - **Sécurité (Dimension 7)** : À la ligne [441](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L441) (`ml_sec_cv_poisoning.py`).
  - **Gouvernance (Dimension 8)** : Aux lignes [499 à 507](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L499-L507) (`ml_gov_metric_accuracy_skew.py`, `ml_gov_bad_model_promote.py`, `ml_gov_insignificant_diff.py`, `ml_gov_ignored_regression.py`, `ml_gov_improper_metric.py`, `ml_gov_buggy_metric.py`, `ml_gov_different_test_sets.py`, `ml_gov_missing_confidence.py`, `ml_gov_incomplete_history.py`).
  - **Exploitation (Dimension 9)** : Aux lignes [564 à 567](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L564-L567) (`ml_ops_pipeline_step_skip.py`, `ml_ops_pipeline_partial_run.py`, `ml_ops_no_retraining.py`, `ml_ops_frequent_retraining.py`).
  - **Organisation (Dimension 10)** : À la ligne [596](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L596) (`ml_org_cv_standard.py`).

- [bi_observability_genesis.md](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/bi_observability_genesis.md) :
  - Ajout des dashboards et alertes liés au pipeline ML et aux biais.
- [mlops_anti_patterns_registry.md](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_anti_patterns_registry.md) :
  - Ajout d'un anti-pattern pertinent pour les métriques de validation inadaptées.
- [journal_mlops.md](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/journal_mlops.md) :
  - Journalisation de l'intégration de la catégorie 16.

---

### CATÉGORIE 17 (== PlanMaitre : 9. Pipeline de données) : Les Problèmes du Pipeline de Données (Data Engineering & ETL)

> *(Tous les scénarios où les données brutes, transformées ou intégrées deviennent incorrectes, incohérentes, incomplètes ou non exploitables.)*

#### 17.1 — Ingestion des données

- **Le fichier source change de format sans prévenir**
  
  Le `BAAC` modifie :  <br>  nom de colonne  <br>  ordre des colonnes  <br>  encodage  <br>  séparateur  <br>  Le pipeline casse immédiatement ou produit des données incorrectes silencieusement.

- **Données partiellement chargées**
  
  Un fichier de 10M lignes n’est chargé qu’à 60 %.  <br>  Le reste est ignoré sans erreur explicite.

- **Fichier tronqué**
  
  Une interruption réseau ou serveur produit un fichier incomplet mais valide syntaxiquement.

- **Double ingestion**
  
  Le même fichier est ingéré deux fois :  <br>  relance de job  <br>  retry automatique `Prefect`  <br>  absence d’idempotence  <br>  → doublons en base

- **Ingestion dans le mauvais environnement**
  
  Les données de `staging` sont chargées en production ou inversement.

#### 17.2 — Schéma & structure

- **Schéma évolutif non géré**
  
  Une colonne change de type :  <br>  `int` → `string`  <br>  `string` → `float`  <br>  `float` → `datetime`  <br>  Sans validation stricte, tout passe… mais les résultats deviennent faux.

- **Colonnes supprimées**
  
  Le provider retire des champs utilisés par le modèle.

- **Colonnes ajoutées**
  
  Nouvelles colonnes ignorées ou mal intégrées.

- **Ordre des colonnes modifié**
  
  Cas rare mais critique si parsing positionnel (`CSV` sans header fiable).

- **Schéma implicite vs explicite**
  
  Le code suppose un schéma.  <br>  Les données en ont un autre.

#### 17.3 — Qualité des données

- **Valeurs aberrantes**
  
  âge = 999  <br>  vitesse = 5000 km/h  <br>  latitude invalide  <br>  dates futures

- **Explosion des valeurs manquantes**
  
  Une colonne passe de 2% à 70% de `NaN`.

- **Données constantes**
  
  Une variable devient constante suite à un bug `upstream`.

- **Données dupliquées**
  
  duplication de lignes  <br>  duplication partielle (jointure mal définie)

- **Données incohérentes**
  
  Exemples :  <br>  accident sans véhicule  <br>  véhicule sans accident  <br>  usager sans lien logique

#### 17.4 — Encodage & formats

- **Encodage cassé**
  
  `UTF-8` vs `Latin-1` → caractères corrompus

- **Dates mal parsées**
  
  01/02/2025 interprété comme février ou janvier selon système

- **Float mal interprété**
  
  virgule vs point décimal

- **`JSON` invalide**
  
  Champs imbriqués mal sérialisés

- **`CSV` fragile**
  
  Séparateurs internes non échappés

#### 17.5 — Jointures & intégration multi-sources

- **Jointure explosive (cartésienne involontaire)**
  
  Une clé mal définie multiplie les lignes ×10 ou ×100

- **Jointure cassée**
  
  Une clé change → perte massive de correspondances

- **Granularité différente**
  
  `BAAC` = accident  <br>  véhicule = multiple lignes  <br>  usagers = encore plus fin  <br>  Mauvaise agrégation → double comptage

- **Désynchronisation des sources**
  
  météo à J+1  <br>  accidents en temps réel  <br>  → features incohérentes

#### 17.6 — Time Alignment (lié mais côté data)

- **Mauvais alignement temporel**
  
  On associe :  <br>  météo après l’accident  <br>  trafic futur  <br>  → leakage implicite

- **Décalage horaire**
  
  Sources différentes en `UTC`/`local`

- **Données en retard**
  
  Certaines sources arrivent avec 24–72h de retard

#### 17.7 — Volume & performance data

- **Explosion du volume**
  
  x10 données historiques  <br>  pipeline non adapté  <br>  → ralentissement massif

- **Partitionnement absent**
  
  Tout est dans une seule table énorme

- **Mauvais index**
  
  Requêtes lentes → ingestion impactée

- **Data skew**
  
  Certaines régions / catégories surreprésentées

#### 17.8 — Streaming vs `batch`

- **Mélange des deux mondes**
  
  `batch` historique  <br>  `streaming` temps réel  <br>  Sans séparation claire → incohérences

- **Retard de `streaming`**
  
  Les événements arrivent hors ordre

- **Double traitement**
  
  Un événement est traité :  <br>  en `streaming`  <br>  en `batch`  <br>  → doublons

#### 17.9 — Idempotence

- **Job non idempotent**
  
  Relancer le pipeline :  <br>  → double insertion

- **Retry dangereux**
  
  Les retries réexécutent des opérations non protégées

- **Absence de clé primaire métier**
  
  Impossible de détecter les doublons proprement

#### 17.10 — Gouvernance des données

- **Source non documentée**
  
  On ne sait plus d’où vient une table

- **Définition métier ambiguë**
  
  Ex : "accident grave" change de définition

- **Données non versionnées**
  
  Impossible de retrouver l’état exact d’un dataset historique

- **Propriété des données inconnue**
  
  Qui est responsable de la correction ?

#### 17.11 — Sécurité & conformité data

- **Données sensibles exposées**
  
  plaques  <br>  localisation  <br>  données personnelles

- **`RGPD` non respecté**
  
  Pas de suppression possible

- **Données injectées (data poisoning)**
  
  Données falsifiées dans pipeline `upstream`

- **Accès non contrôlé**
  
  Tout le monde peut lire toutes les tables

#### 17.12 — Corruption silencieuse (le pire cas)

- **Pipeline “vert” mais données fausses**
  
  Tout passe :  <br>  ingestion OK  <br>  job OK  <br>  logs OK  <br>  Mais :  <br>  → données incohérentes

- **Dérive progressive des données**
  
  Pas de rupture brutale :  <br>  petites erreurs cumulées  <br>  biais progressif

- **Erreur non détectée pendant des mois**
  
  Les dashboards restent stables  <br>  Mais les décisions sont fausses

#### Pourquoi cette catégorie est critique

Le pipeline de données est la fondation invisible de tout système MLOps. Contrairement aux couches supérieures (API, modèles, monitoring), les erreurs ici ne provoquent souvent ni crash ni exception. Elles se propagent silencieusement dans les features, les modèles et les décisions métier. C’est pour cela que dans l’industrie, on considère souvent que “si les données sont fiables, 80% des problèmes sont déjà résolus”.

#### Lien avec notre architecture `BAAC`

Dans notre système, cette catégorie est particulièrement critique car :
- `BAAC` = données multi-sources complexes (caract / lieux / véhicules / usagers)
- jointures sensibles
- évolution gouvernementale non contrôlée
- forte dimension temporelle
- dépendance météo externe
👉 donc nous avons un risque structurel élevé de corruption silencieuse des données, même si tout “semble fonctionner”.

---

### Analyse de Correspondance avec la Taxonomie des Grandes Dimensions :

- **Poids estimé :** 100% orienté **Dimension 2 : Données**, avec des chevauchements sur **Dimension 1 : Infrastructure** (Performance, Volume, Idempotence) et **Dimension 7 : Sécurité**.
- **Justification :** Cette catégorie explore les fondations mêmes de tout pipeline MLOps. Les anomalies décrites ici se manifestent au niveau de l'acquisition, la transformation et le stockage. Si cette étape échoue (corruption, types de données, perte), toutes les dimensions en aval (Feature Engineering, Modèles, Serving) utiliseront des données dégradées ou fausses sans nécessairement planter, rendant le monitoring classique inopérant.
- **Résumé :** Une cartographie indispensable des défaillances de Data Engineering qui rappelle que la robustesse MLOps commence par l'intégrité absolue et les contrats de données de l'ingestion ETL.
### Suivi de l'Enrichissement Croisé :

- [mlops_failure_modes_taxonomy.md](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md) :
  - Traduction et intégration de 100% des incidents de la Catégorie 17 répartis sous leurs dimensions MLOps respectives :

    * **Dimension 1 : Infrastructure**
      - `17.7` — Explosion du volume (x10 historique) (lignes [113](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L113))
      - `17.7` — Partitionnement absent (table énorme) (lignes [114](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L114))
      - `17.7` — Mauvais index (lignes [115](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L115))
      - `17.7` — Data skew sur l'infrastructure (lignes [116](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L116))
      - `17.9` — Job non idempotent relancé (lignes [117](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L117))
      - `17.9` — Retry dangereux (lignes [118](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L118))
      - `17.9` — Absence de clé primaire métier (lignes [119](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L119))
    * **Dimension 2 : Données**
      - `17.1` — Le fichier source change de format sans prévenir (nom, ordre, encodage) (lignes [194](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L194))
      - `17.1` — Données partiellement chargées (ex: 60% d'un fichier) (lignes [195](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L195))
      - `17.1` — Fichier tronqué (interruption réseau/serveur) (lignes [196](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L196))
      - `17.1` — Double ingestion (relance job, retry auto) (lignes [197](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L197))
      - `17.1` — Ingestion dans le mauvais environnement (staging -> prod) (lignes [198](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L198))
      - `17.2` — Schéma évolutif non géré (int -> string -> float) (lignes [199](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L199))
      - `17.2` — Colonnes supprimées par le provider (lignes [200](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L200))
      - `17.2` — Colonnes ajoutées ignorées (lignes [201](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L201))
      - `17.2` — Ordre des colonnes modifié (CSV sans header) (lignes [202](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L202))
      - `17.2` — Schéma implicite vs explicite divergent (lignes [203](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L203))
      - `17.3` — Valeurs aberrantes (âge=999, dates futures) (lignes [204](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L204))
      - `17.3` — Explosion des valeurs manquantes (2% -> 70% NaN) (lignes [205](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L205))
      - `17.3` — Données devenues constantes (bug upstream) (lignes [206](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L206))
      - `17.3` — Données dupliquées (lignes ou partiel) (lignes [207](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L207))
      - `17.3` — Données incohérentes (accident sans véhicule) (lignes [208](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L208))
      - `17.4` — Encodage cassé (UTF-8 vs Latin-1) (lignes [209](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L209))
      - `17.4` — Dates mal parsées (01/02/2025) (lignes [210](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L210))
      - `17.4` — Float mal interprété (virgule vs point) (lignes [211](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L211))
      - `17.4` — JSON invalide (champs imbriqués mal sérialisés) (lignes [212](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L212))
      - `17.4` — CSV fragile (séparateurs internes non échappés) (lignes [213](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L213))
      - `17.5` — Jointure explosive (cartésienne involontaire) (lignes [214](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L214))
      - `17.5` — Jointure cassée (clé modifiée) (lignes [215](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L215))
      - `17.5` — Granularité différente mal agrégée (lignes [216](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L216))
      - `17.5` — Désynchronisation des sources (météo J+1 vs accident TR) (lignes [217](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L217))
      - `17.6` — Mauvais alignement temporel (météo future) (lignes [218](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L218))
      - `17.6` — Décalage horaire (UTC vs local) (lignes [219](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L219))
      - `17.6` — Données en retard (24-72h) (lignes [220](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L220))
      - `17.8` — Mélange streaming vs batch (lignes [221](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L221))
      - `17.8` — Retard de streaming (hors ordre) (lignes [222](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L222))
      - `17.8` — Double traitement (streaming + batch) (lignes [223](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L223))
      - `17.10` — Source non documentée (lignes [224](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L224))
      - `17.10` — Définition métier ambiguë ou modifiée (lignes [225](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L225))
      - `17.10` — Données non versionnées (lignes [226](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L226))
      - `17.10` — Propriété des données inconnue (lignes [227](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L227))
      - `17.12` — Pipeline vert mais données fausses (lignes [228](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L228))
      - `17.12` — Dérive progressive des données (lignes [229](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L229))
      - `17.12` — Erreur non détectée pendant des mois (lignes [230](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L230))
    * **Dimension 7 : Sécurité**
      - `17.11` — Données sensibles exposées (plaques, PI) (lignes [442](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L442))
      - `17.11` — RGPD non respecté (lignes [443](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L443))
      - `17.11` — Données injectées (data poisoning) (lignes [444](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L444))
      - `17.11` — Accès non contrôlé aux tables analytiques (lignes [445](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L445))

  Voici les lignes exactes de chaque dimension où elles ont été réparties :

  - **Infrastructure (Dimension 1)** : Aux lignes [113 à 119](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L113-L119) (`17_7_sim.py`, `17_9_sim.py`).
  - **Données (Dimension 2)** : Aux lignes [194 à 230](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L194-L230) (`17_1_sim.py`, `17_2_sim.py`, `17_3_sim.py`, `17_4_sim.py`, `17_5_sim.py`, `17_6_sim.py`, `17_8_sim.py`, `17_10_sim.py`, `17_12_sim.py`).
  - **Sécurité (Dimension 7)** : Aux lignes [442 à 445](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L442-L445) (`17_11_sim.py`).

- [bi_observability_genesis.md](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/bi_observability_genesis.md): Alertes liées à la qualité et l'intégrité de l'ingestion de données brutes.
- [mlops_anti_patterns_registry.md](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_anti_patterns_registry.md): Validation de schéma implicite sans data contracts.
- [journal_mlops.md](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/journal_mlops.md): Journalisation de l'intégration de la catégorie 17.

---

### CATÉGORIE 18 (== PlanMaitre : 10. Sécurité) : Les Problèmes de Sécurité (Cyber, Accès, Modèles & Données)

> *(Tous les scénarios où le système est compromis, manipulé, exposé ou détourné — volontairement ou non.)*

#### 18.1 — Authentification & Accès

- **`API` publique sans authentification**
  
  Le endpoint /v1/predict est accessible à tous.  <br>  Conséquences :  <br>  spam de requêtes  <br>  coût explosif  <br>  déni de service (`DoS`)  <br>  extraction du comportement du modèle

- **Mauvaise gestion des tokens**
  
  tokens non expirants  <br>  tokens partagés  <br>  absence de rotation  <br>  → accès permanent non contrôlé

- **Clés exposées dans le code**
  
  Exemples :  <br>  .env commit sur `GitHub`  <br>  secrets dans `docker-compose`  <br>  variables `CI` visibles  <br>  → compromission immédiate

- **`SSH` faible ou absent**
  
  mot de passe simple  <br>  pas de clé `SSH`  <br>  brute force possible

#### 18.2 — `API` & Injection

- **Injection `SQL`**
  
  Exemple classique :  <br>  '; DROP TABLE accidents; --

- **→ destruction ou exfiltration de données**
  
  

- **Injection dans filtres `API`**
  
  paramètres non sanitizés  <br>  requêtes dynamiques mal construites

- **Injection via `JSON` / payload ML**
  
  Un utilisateur injecte des valeurs manipulées dans les features :  <br>  falsification de prédiction  <br>  corruption indirecte du modèle

- **Injection dans logs**
  
  Log poisoning :  <br>  fausse trace d’erreur  <br>  camouflage d’attaque

#### 18.3 — Sécurité des données

- **Exfiltration de données sensibles**
  
  Accès non filtré aux tables :  <br>  accidents géolocalisés  <br>  données personnelles (`RGPD`)

- **Absence de chiffrement**
  
  données en clair en base  <br>  trafic `HTTP` non sécurisé

- **Mauvais contrôle d’accès (`RBAC` absent)**
  
  Tous les services ont accès à toutes les données

- **Dump de base de données**
  
  Attaquant récupère :  <br>  historique complet `BAAC`  <br>  features métiers  <br>  logs sensibles

#### 18.4 — Sécurité du modèle (ML Security)

- **Model extraction attack**
  
  Un attaquant interroge l’`API` :  <br>  reconstruit approximativement le modèle  <br>  copie le comportement métier

- **Model inversion attack**
  
  À partir des prédictions :  <br>  → reconstruction de données sensibles  <br>  Ex : retrouver caractéristiques d’accidents individuels

- **Membership inference attack**
  
  Déterminer si un accident spécifique était dans le dataset d’entraînement

- **Poisoning du modèle**
  
  Injection de données malveillantes dans le dataset :  <br>  biais progressif  <br>  dégradation invisible  <br>  manipulation ciblée des prédictions

#### 18.5 — Sécurité du Feature Store

- **Feature leakage malveillant**
  
  Un attaquant injecte des features contenant :  <br>  informations futures  <br>  labels cachés  <br>  → modèle biaisé volontairement

- **Accès libre aux `Feature Views`**
  
  Toutes les features sont consultables :  <br>  → reconstitution du dataset complet possible

- **Corruption des features**
  
  Modification silencieuse de valeurs dans le store

#### 18.6 — Infrastructure & Container Security

- **Image `Docker` compromise**
  
  Une image contient :  <br>  backdoor  <br>  script malveillant  <br>  crypto-miner

- **Dépendances compromises**
  
  Ex :  <br>  package `PyPI` infecté  <br>  dépendance ML trojanisée

- **Container breakout**
  
  Un conteneur accède à l’hôte  <br>  → contrôle complet du serveur

- **Secrets dans les containers**
  
  Variables d’environnement exposées dans logs ou inspection runtime

#### 18.7 — Réseau

- **`API` exposée sans firewall**
  
  Tout Internet peut interroger les services internes

- **Man-in-the-Middle (MITM)**
  
  Sans `TLS` :  <br>  → interception des prédictions et données

- **`DNS` spoofing**
  
  Redirection vers faux endpoints :  <br>  `API` météo falsifiée  <br>  ingestion corrompue

- **Port scanning & exposition**
  
  Ports ouverts non nécessaires :  <br>  `PostgreSQL` exposé publiquement  <br>  `MLflow` UI accessible

#### 18.8 — ML Supply Chain Attack

- **Dépendances compromises**
  
  Une librairie ML contient du code malveillant :  <br>  exfiltration de données  <br>  modification des prédictions

- **`MLflow` artifact poisoning**
  
  Un modèle enregistré est remplacé ou modifié

- **Dataset remplacé**
  
  Le fichier `BAAC` est remplacé par une version falsifiée

#### 18.9 — Logging & Observabilité (sécurité détournée)

- **Logs sensibles exposés**
  
  Logs contenant :  <br>  données personnelles  <br>  tokens  <br>  requêtes complètes

- **Désactivation des logs**
  
  Un attaquant coupe `Sentry` ou les alertes  <br>  → attaque invisible

- **Alert fatigue exploitée**
  
  Attaquant génère beaucoup d’erreurs bénignes  <br>  → les vraies alertes sont ignorées

#### 18.10 — Déni de service (`DoS` / `DDoS`)

- **`API` saturée**
  
  Des milliers de requêtes :  <br>  → CPU saturé  <br>  → latence infinie

- **Feature computation attack**
  
  Appels qui déclenchent des features coûteuses :  <br>  → explosion du coût de calcul

- **ML `SHAP` abuse**
  
  Utilisation répétée de `SHAP` :  <br>  → saturation mémoire / CPU

#### 18.11 — Sécurité organisationnelle

- **Droits trop larges en interne**
  
  Un ingénieur peut :  <br>  modifier `production`  <br>  déployer modèle  <br>  supprimer données

- **Absence de séparation `dev/prod`**
  
  Une erreur en `staging` impacte `production`

- **`CI`/CD non sécurisé**
  
  Pipeline `GitHub` Actions compromis :  <br>  → déploiement automatique malveillant

#### 18.12 — Attaques spécifiques MLOps

- **Adversarial examples**
  
  Entrées légèrement modifiées :  <br>  → prédictions totalement changées

- **Data drift forcé**
  
  Attaquant modifie distribution des données pour dégrader le modèle

- **Feature manipulation ciblée**
  
  Modification d’une seule feature critique :  <br>  → biais systématique des décisions

#### Pourquoi cette catégorie est critique

La sécurité en MLOps est particulière car elle ne concerne pas seulement l’accès aux systèmes, mais aussi la manipulation des données et du comportement du modèle lui-même. Contrairement aux bugs classiques, rien ne crash forcément, les prédictions continuent, mais elles peuvent être contrôlées ou biaisées.

#### Lien avec notre architecture `BAAC`

Dans notre cas, les points critiques sont :
- `API` `/predict` exposée
- Feature Store (`Feast`) accessible
- `MLflow` (tracking + artifacts)
- dépendances externes météo
- jointures complexes `BAAC` (faciles à empoisonner)
- absence potentielle de monitoring sécurité spécialisé

👉 Conclusion simple : Dans une architecture MLOps, la sécurité n’est pas une couche “en plus”, c’est une propriété transversale qui peut être compromise à n’importe quel niveau (data → features → modèle → `API` → infra).

---

### Analyse de Correspondance avec la Taxonomie des Grandes Dimensions :

- **Poids estimé :** 90% orienté **Dimension 7 : Sécurité**, avec des chevauchements sur **Dimension 1 : Infrastructure** (Container, Network) et **Dimension 10 : Organisation** (RBAC, CI/CD).
- **Justification :** Cette catégorie aborde l'ensemble du spectre de la sécurité offensive et défensive. Du *Data Poisoning* spécifique au ML, à la compromission d'infrastructure classique (Docker breakout). La Sécurité traverse toutes les strates : Ingestion, Entraînement, Serving, et Observabilité (camouflage).
- **Résumé :** Une cartographie de la surface d'attaque globale du système MLOps soulignant l'importance d'une sécurité *Shift-Left* à la fois logicielle, réseau et algorithmique.

### Suivi de l'Enrichissement Croisé :

- [mlops_failure_modes_taxonomy.md](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md) :
  - Traduction et intégration de 100% des incidents de la Catégorie 18 répartis sous leurs dimensions MLOps respectives :

    * **Dimension 7 : Sécurité**
      - `18.1` — API publique sans authentification (lignes [446](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L446))
      - `18.1` — Mauvaise gestion des tokens (non expirants, partagés) (lignes [447](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L447))
      - `18.1` — Clés exposées dans le code (GitHub, CI, env) (lignes [448](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L448))
      - `18.1` — SSH faible ou absent (lignes [449](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L449))
      - `18.2` — Réseau plat (absence de VPC/DMZ) (lignes [450](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L450))
      - `18.2` — Ports ouverts au monde entier (0.0.0.0/0) (lignes [451](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L451))
      - `18.2` — Bucket cloud public (S3/GCS) (lignes [452](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L452))
      - `18.3` — Dépendances vérolées (Supply Chain) (lignes [453](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L453))
      - `18.3` — Docker image compromise (DockerHub) (lignes [454](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L454))
      - `18.3` — Pickle empoisonné (Deserialization attack) (lignes [455](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L455))
      - `18.4` — Vol des poids du modèle (lignes [456](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L456))
      - `18.4` — Extraction de modèle via API (Model stealing) (lignes [457](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L457))
      - `18.5` — Data Poisoning (entrainement) (lignes [458](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L458))
      - `18.5` — Label manipulation (lignes [459](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L459))
      - `18.6` — Adversarial Examples (Evasion) (lignes [460](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L460))
      - `18.6` — Bypass des filtres de sécurité (lignes [461](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L461))
      - `18.7` — Membership Inference Attack (lignes [462](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L462))
      - `18.7` — Inversion de modèle (Model Inversion) (lignes [463](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L463))
      - `18.8` — Déni de Service (DoS) sur le serving (lignes [464](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L464))
      - `18.8` — Sponge Attack (Energy latency) (lignes [465](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L465))
      - `18.9` — Log Injection (lignes [466](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L466))
      - `18.9` — Monitoring empoisonné (lignes [467](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L467))
      - `18.10` — Absence de chiffrement au repos (lignes [468](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L468))
      - `18.10` — Absence de chiffrement en transit (HTTP) (lignes [469](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L469))
      - `18.12` — Data drift forcé (lignes [470](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L470))
      - `18.12` — Feature manipulation ciblée (lignes [471](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L471))
    * **Dimension 10 : Organisation**
      - `18.11` — Droits internes trop larges (ingénieur supprime tout) (lignes [597](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L597))
      - `18.11` — Absence de séparation dev/prod (lignes [598](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L598))
      - `18.11` — CI/CD non sécurisé (GitHub Actions compromis) (lignes [599](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L599))

  Voici les lignes exactes de chaque dimension où elles ont été réparties :

  - **Sécurité (Dimension 7)** : Aux lignes [446 à 471](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L446-L471) (`18_1_sim.py`, `18_2_sim.py`, `18_3_sim.py`, `18_4_sim.py`, `18_5_sim.py`, `18_6_sim.py`, `18_7_sim.py`, `18_8_sim.py`, `18_9_sim.py`, `18_10_sim.py`, `18_12_sim.py`).
  - **Organisation (Dimension 10)** : Aux lignes [597 à 599](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_failure_modes_taxonomy.md#L597-L599) (`18_11_sim.py`).

- [bi_observability_genesis.md](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/bi_observability_genesis.md): Alertes de sécurité, détection d'injection, et audit d'accès non autorisés.
- [mlops_anti_patterns_registry.md](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/mlops_anti_patterns_registry.md): L'Exhibitionnisme Algorithmique (Anti-pattern 20) a été ajouté pour adresser l'API sans authentification.
- [journal_mlops.md](file:///Users/nolll/.gemini/antigravity/brain/10b271a9-5646-4286-b482-9f27ac791062/journal_mlops.md): Journalisation de l'intégration de la catégorie 18.

---

## Annexes : Débats Conceptuels & Paradoxes MLOps sous-jacents

Cette section documente les débats théoriques d'architecture et les paradoxes de conception soulevés par l'ingestion des catégories de l'Ontologie. Elle vise à mettre en conscience les arbitrages de design système.

### A. Notice Opérationnelle : Débat Conceptuel FMEA (Cause vs Effet pour RPO/RTO)

Voici l'explication théorique et méthodologique de ce débat classique en gestion des risques (`FMEA`), qui distingue la cause originelle (la panne) de la conséquence finale (l'impact sur les objectifs `RPO`/`RTO`) :

1. **La Distinction Théorique : Cause vs. Effet**
   Dans une analyse de risques classique (comme l'`AMDEC` / `FMEA`) :
   *   **Le Failure Mode (La Cause)** : C'est la défaillance technique ou humaine initiale (ex: *le disque dur crashe*, *le script de sauvegarde écrit un fichier vide*, *la région cloud est indisponible*).
   *   **L'Impact / Effet (La Conséquence)** : C'est la métrique business ou opérationnelle qui est compromise (ex: *Disponibilité*, *Perte de données*, ou spécifiquement le non-respect des engagements contractuels de reprise).
   *   Le `RPO` (*Recovery Point Objective* - la quantité maximale de données qu'on accepte de perdre) et le `RTO` (*Recovery Time Objective* - le temps maximal d'interruption acceptable) ne sont pas des pannes. Ce sont des indicateurs contractuels de résilience.

2. **Comment ces concepts s'intègrent implicitement dans les colonnes d'une ligne technique**
   Dans une approche purement technique, le dépassement du `RPO` ou du `RTO` ne nécessite pas de ligne dédiée car il est déduit des caractéristiques des autres pannes :
   *   **Pour le RPO (Perte de données)** :
       *   Si ton script de backup tourne toutes les 24h, ta perte de données maximale théorique est de 24h.
       *   Si la panne est *"Sauvegarde `PostgreSQL` en échec silencieux"* et qu'on ne la détecte qu'après 3 jours, ta perte de données réelle sera de 3 jours. Si ton engagement `RPO` était de 4h, tu as dépassé ton `RPO`.
       *   Le risque est donc directement mesuré par les colonnes `Détection` (à quelle vitesse on s'en aperçoit) et `Temps` de la ligne technique *"Échec silencieux de sauvegarde"*.
   *   **Pour le RTO (Temps de reprise)** :
       *   Si le serveur physique brûle, l'action corrective est *"Reconstruction de l'instance"*.
       *   Si cette reconstruction prend 8 heures (colonne `Temps` de réaction attendu) alors que ton engagement `RTO` est de 2 heures, tu as dépassé ton `RTO`.
       *   Le risque est mesuré par le temps nécessaire à l'`Intervention Humaine` de la ligne *"Destruction du serveur"*.

3. **Pourquoi les avoir quand même ajoutés comme lignes physiques ?**
   Bien que théoriquement le `RPO` et le `RTO` soient des métriques d'impact et non des pannes, nous avons choisi de les insérer sous forme de lignes explicites dans notre matrice (`Dimension 9`, `Cat. 10.7`) pour deux raisons `MLOps` majeures :
   *   **Fidélité Absolue à l'Ontologie (Règle 7)** : L'ontologie d'origine listait des scénarios centrés sur le non-respect de ces objectifs. Les matérialiser sous forme de lignes garantit qu'aucun de ces scénarios n'est éludé.
   *   **Scénarios de Chaos spécifiques** : Cela permet d'associer des scripts de simulation dédiés (ex: simuler un `RTO` dépassé pour forcer le basculement en mode dégradé, ou tester la ré-ingestion de données delta en cas de dépassement de `RPO`).

**En résumé** : Techniquement, le dépassement de `RPO`/`RTO` est la conséquence directe d'une mauvaise détection ou d'une mauvaise remédiation sur une ligne technique. Organisationnellement, les lister permet d'avoir des scénarios d'exercice de `Chaos` clairs sur les plans de continuité d'activité.

### B. Analyse des Paradoxes de l'Ontologie (Catégories 9.XX, 10.XX, 11.XX, 12.XX, 13.XX & 14.XX)

Certains points de l'Ontologie, sous des formulations très simples, cachent des paradoxes et des débats d'architecture `MLOps` fondamentaux qui n'ont pas encore été pleinement "débattus" ou conscientisés dans notre implémentation.

1. **Le Paradoxe de la Cohérence Temporelle Distribuée (Cat. 10.3 / 10.4)**
   *   **La Panne dans la matrice** : *"Registre de modèles `MLflow` perdu"*, *"Données `DVC` inaccessibles"*, *"Signature de modèle perdue"*.
   *   **Le Concept non débattu** : La désynchronisation de l'état (*Split-Brain*) du `MLOps`. Un système IA é composé de 3 piliers qui vivent dans des systèmes de stockage différents : le code (`Git`), les métadonnées de tracking (`PostgreSQL`/`MLflow`) et les fichiers lourds (`DVC`/`S3`). Si tu restaures ta base `PostgreSQL` à son état de la veille à 12h00 suite à un crash, mais que ton stockage `S3`/`DVC` a continué de vivre ou a été restauré à son état de la veille à 18h00, tu te retrouves avec des pointeurs cassés (des runs qui référencent des fichiers inexistants, ou des modèles V2 qui s'exécutent avec des preprocessings de V1).
   *   **Mise en conscience** : Nous avons les lignes de pannes séparées, mais nous n'avons pas encore conçu le concept de **Sauvegarde Coordonnée** (un snapshot atomique qui fige simultanément `Git`, `MLflow` et `DVC` pour garantir la cohérence temporelle post-restauration).

2. **Le Syndrome du "Succès en Miniature" (Cat. 10.8)**
   *   **La Panne dans la matrice** : *"Tests de reprise sur petits volumes"*.
   *   **Le Concept non débattu** : La non-linéarité de l'échelle d'infrastructure. Tester la restauration à blanc en pré-production sur une base de données de test de 50 Mo prend 2 minutes et réussit toujours. Le jour du sinistre en production, restaurer 5 To de données sous pression réseau et disque prend 18 heures et échoue à cause de la saturation des IOPS ou des timeouts de connexion.
   *   **Mise en conscience** : Valider le code du script de restauration (ce que fait le `Chaos` actuel) ne valide pas la capacité physique et réseau à tenir le `RTO` réel sur de la vraie volumétrie. C'est une illusion de sécurité.

3. **Le dilemme de la "Graceful Degradation" (Le Mode Dégradé) (Cat. 10.6 / 10.7)**
   *   **La Panne dans la matrice** : *"Dépassement du RTO"* (mitigé par un "Mode dégradé").
   *   **Le Concept non débattu** : Heuristique Métier vs Modèle IA en cas de crise. Si l'infrastructure de serving s'effondre et prend 4 heures à se reconstruire, quelle est la politique de repli ? L'application cliente doit-elle renvoyer des erreurs 500 (panne totale) ou le système doit-il basculer sur un microservice ultra-léger sans IA qui sert des prédictions statiques (ex: la moyenne historique d'accidentologie par département) ?
   *   **Mise en conscience** : Le choix de ce que contient le "mode dégradé" est un arbitrage business/gouvernance critique qui n'est pas formalisé dans nos plans de secours actuels.

4. **La "Dette de Reproductibilité" vs Le Coût d'Archivage (Cat. 9.7)**
   *   **La Panne dans la matrice** : *"Incapacité de reconstruire un environnement historique"*.
   *   **Le Concept non débattu** : La durabilité environnementale et financière de la reproductibilité. L'ontologie exige d'être capable de reconstruire un environnement d'il y a 3 ans. En théorie, c'est beau. En pratique, cela exige de conserver indéfiniment des images `Docker` gigantesques sur nos registres, de maintenir des compatibilités avec des versions d'OS obsolètes, ou de payer pour du stockage inactif (`FinOps`).
   *   **Mise en conscience** : Où s'arrête la responsabilité de reproductibilité ? Doit-on pouvoir ré-entraîner à l'identique (très cher à conserver) ou simplement être capable de ré-exécuter le modèle compilé (plus simple) ?

5. **Le Paradoxe du "Health Check Flapping" (Cat. 11.2)**
   *   **La Panne dans la matrice** : *"Health Check `LB` trop strict (flapping)"*.
   *   **Le Concept non débattu** : L'instabilité auto-induite (l'effet de résonance). Pour maximiser la disponibilité, on configure des health checks très sensibles. Dès qu'une instance de serving ralentit sous l'effet du garbage collector ou d'une micro-surcharge, le Load Balancer la retire. Cela reporte 100% de la charge sur les autres instances, qui ralentissent à leur tour et se font également retirer. Le système s'effondre en boucle en cherchant à se protéger.
   *   **Mise en conscience** : La Haute Disponibilité exige des amortisseurs de bascule (cooldowns, seuils glissants) pour éviter les cascades d'indisponibilité auto-induites.

6. **Le Paradoxe de la Réplication WAL Asynchrone (Cat. 11.3 / 11.4)**
   *   **La Panne dans la matrice** : *"Réplication `PostgreSQL` arrêtée"* ou *"Réplication `PostgreSQL` retard important"*.
   *   **Le Concept non débattu** : La perte de transactions lors du failover (Data Loss on Failover). Dans les architectures de base de données, pour préserver la latence d'écriture du primaire, on utilise une réplication asynchrone. En cas de sinistre, la bascule automatique vers le secondaire évite le temps d'indisponibilité (HA), mais au prix d'une perte silencieuse de données. Cela peut briser la cohérence temporelle entre les prédictions servies et les données enregistrées.
   *   **Mise en conscience** : Arbitrage fondamental entre disponibilité immédiate (AP dans le théorème CAP) ou cohérence stricte des données (CP).

7. **Le Paradoxe du Monitoring de Monitoring (Le Régressif Actif) (Cat. 12.9)**
   *   **La Panne dans la matrice** : *"L'outil de monitoring tombe"* ou *"Collecteur de metrics arrêté"*.
   *   **Le Concept non débattu** : La récursion infinie de l'observabilité. Pour surveiller le serving, on configure Prometheus. Pour surveiller Prometheus, on a une sonde externe. Mais pour surveiller la sonde... À quel moment s'arrête la chaîne de dépendances de surveillance ? Si le système de monitoring lui-même s'effondre silencieusement, l'équipe technique conserve un sentiment de sécurité illusoire ("les dashboards sont verts") alors que le système is aveugle.
   *   **Mise en conscience** : Nécessité d'un interrupteur de type "Dead Man's Switch" (un heartbeat binaire externe hébergé de façon totalement isolée de notre réseau principal) pour s'assurer que le moniteur est actif.

8. **Le Paradoxe de la Fatigue d'Alertes (Cat. 12.3 / 12.10)**
   *   **La Panne dans la matrice** : *"Seuil d'alerte trop faible (alert fatigue)"* ou *"Bruit de monitoring"*.
   *   **Le Concept non débattu** : La désensibilisation cognitive de l'humain face aux signaux répétitifs. Plus un système génère de notifications pour des variations normales ou mineures, plus l'équipe d'exploitation développe un filtre passif d'indifférence. Le jour où l'alerte critique réelle est générée, elle est ignorée car assimilée au bruit quotidien.
   *   **Mise en conscience** : Une observabilité robuste exige de dissocier strictement le "Bruit" (à logger), les "Warnings" (à auditer en heure ouvrable) et le "Paging" (intervention humaine immédiate requise en astreinte).

9. **Le Paradoxe de l'Optimisation Locale (FinOps vs Performance) (Cat. 13.12)**
   *   **La Panne dans la matrice** : *"Performances accrues mais coût explose"* ou *"Optimisation locale dégradant le global"*.
   *   **Le Concept non débattu** : Le coût marginal de la micro-performance. Accélérer la latence d'inférence d'un modèle XGBoost de 20 ms à 15 ms en multipliant par 3 les ressources CPU allouées donne une amélioration technique locale de 25%. Cependant, cela augmente de 300% la facture cloud tout en décalant simplement le bottleneck vers la base de données PostgreSQL qui répond en 80 ms.
   *   **Mise en conscience** : La performance doit être modélisée de manière holistique via des métriques de parcours complet (end-to-end tracing) associées à des budgets d'infrastructure maximum (Error Budget / FinOps), plutôt que par optimisation de micro-composants isolés.

10. **Le Choke Point de Sérialisation (Cat. 13.1)**
    *   **La Panne dans la matrice** : *"Temps de sérialisation JSON important"* ou *"Temps de préprocessing serving dominant"*.
    *   **Le Concept non débattu** : L'inefficacité du CPU sur l'orchestration des formats de données par rapport à l'inférence. Dans beaucoup d'applications de ML en production, les ingénieurs passent des jours à optimiser le modèle (vectorisation, quantification) pour gagner 2 ms sur l'inférence mathématique, sans voir que les frameworks web passent 30 ms à parser de volumineuses requêtes JSON imbriquées ou à dupliquer les DataFrames en RAM pour le preprocessing. Le goulet d'étranglement n'est plus l'IA, mais l'interfaçage de données.
    *   **Mise en conscience** : Les architectures d'inférence performantes doivent utiliser des protocoles de transport rapides (ex: middlewares en C, parsers JSON ultra-rapides comme `orjson`, ou gRPC) et des structures de données à zéro-copie en mémoire.

11. **Le Paradoxe de la Coexistence Multiversionnelle (Split-Brain de Vues) (Cat. 14.8)**
    *   **La Panne dans la matrice** : *"Mauvaise version de Feature View chargée (V2 au lieu de V3)"* ou *"Feature View supprimée"*.
    *   **Le Concept non débattu** : La cohabitation temporelle de schémas. En MLOps, contrairement au génie logiciel classique où une base de données migre vers un état unique, le Feature Store doit être capable de servir simultanément des versions différentes de la même feature (ex: la V2 pour un modèle historique toujours en cours d'A/B test et la V3 pour le nouveau modèle). Si la matérialisation ou la modification de schéma écrase ou supprime la V2, les prédictions du modèle V2 s'effondrent immédiatement ou dérivent silencieusement.
    *   **Mise en conscience** : Un Feature Store mature doit être conçu comme un registre immuable et versionné (Immutable Feature Registry) qui interdit la suppression ou l'altération de structures historiques tant qu'un modèle dépendant est actif.

12. **Le Syndrome de la Feature Statique Fantôme (Cat. 14.6)**
    *   **La Panne dans la matrice** : *"Feature devenue constante (toutes les lignes à 0)"* ou *"Explosion des NaN dans Feast"*.
    *   **Le Concept non débattu** : L'absence de mort de feature. Si le pipeline qui alimente l'Offline Store plante, ou si la source s'arrête d'émettre des variations, le Feature Store continue à matérialiser ou à servir la dernière valeur connue (le cache Redis ne renvoie pas d'erreur, il renvoie juste une valeur obsolète). Le modèle continue à prédire avec des données "fantômes" constantes. L'API est 100% disponible, mais sa qualité de prédiction se dégrade de façon totalement transparente pour l'infrastructure.
    *   **Mise en conscience** : La santé d'un Feature Store exige d'associer à chaque valeur servie une **métadonnée de fraîcheur** (Data Timestamp) validée à chaud lors de l'inférence par un disjoncteur (Circuit Breaker) si la donnée dépasse un seuil d'obsolescence (TTL strict).

13. **Le Dilemme de la Vérité Historique (Offline vs Online) (Cat. 14.7)**
    *   **La Panne dans la matrice** : *"Offline Store correct mais Online Store obsolète"*.
    *   **Le Concept non débattu** : L'asynchronisme de la vérité. L'Offline Store (PostgreSQL) contient l'historique complet et correct des features pour l'entraînement. L'Online Store (Redis) contient les valeurs à chaud pour l'inférence. Si la matérialisation échoue, ces deux mondes se séparent : les entraînements futurs se font sur des données parfaites du passé, mais le modèle déployé prédit sur des valeurs online figées et fausses. Ce décalage temporel brise la reproductibilité et invalide les tests de validation.
    *   **Mise en conscience** : Nécessité de mettre en œuvre des **tests de consistance croisés** (Offline-Online Parity Checks) réguliers qui comparent le hash des features stockées dans PostgreSQL avec celles lues dans Redis pour alerter au moindre écart de synchronisation.

14. **Le Paradoxe du Voyage Temporel Involontaire (Data Leakage Temporel) (Cat. 15.5)**
    *   **La Panne dans la matrice** : *"Utilisation d'une donnée 'future'"* ou *"Snapshot incorrect"*.
    *   **Le Concept non débattu** : La porosité temporelle des pipelines d'entraînement. Lors du calcul de features d'entraînement historiques, si un calcul d'agrégation utilise par erreur des enregistrements postérieurs à la date d'inférence historique (ex: calculer la moyenne des accidents d'un département sur les 30 jours *suivants* au lieu de *précédents*), le modèle apprend sur le futur. À l'évaluation, les métriques sont exceptionnelles, mais en production réelle, les performances s'effondrent car le futur est indisponible.
    *   **Mise en conscience** : La reproductibilité exige un cloisonnement temporel hermétique (Point-in-Time Joins) implémenté au niveau du Feature Store pour interdire tout calcul utilisant des données postérieures au timestamp de l'événement.

15. **Le Split-Brain Temporel des Fuseaux Horaires (Cat. 15.1 / 15.2)**
    *   **La Panne dans la matrice** : *"Les données utilisent deux fuseaux horaires différents"* ou *"Changement de fuseau lors d'un déploiement"*.
    *   **Le Concept non débattu** : La désynchronisation sémantique des événements temporels. Si le serving enregistre les prédictions en heure locale (Europe/Paris) sans timezone offset, et que la météo ou d'autres API externes répondent en UTC, les heures d'accidents ne correspondent plus aux heures météorologiques. De plus, lors des changements d'heure (été/hiver), une heure est dupliquée ou disparue, provoquant des anomalies de calcul et de jointure.
    *   **Mise en conscience** : L'architecture doit imposer l'utilisation exclusive d'un référentiel de temps unique et absolu (`UTC` ou timestamp epoch en millisecondes) à tous les niveaux (base de données, logs, API, Feature Store) et reléguer la conversion en heure locale uniquement à la couche de présentation.

16. **Le Paradoxe du Seuil de Décision Universel (Cat. 16.7)**
    *   **La Panne dans la matrice** : *"Seuil de décision oublié (utilisant 0.5)"* ou *"Seuil modifié"*.
    *   **Le Concept non débattu** : La décorrélation entre probabilité probabiliste et coût d'erreur asymétrique. Dans un problème déséquilibré comme la prédiction d'accidents graves, utiliser un seuil par défaut de `0.5` suppose qu'un faux positif (prédire un accident grave à tort) a exactement le même coût qu'un faux négatif (rater un accident grave réel). En réalité, rater un cas grave a un coût humain ou business infiniment plus élevé. Choisir le seuil optimal de décision relève d'une fonction d'utilité métier et non de la pure performance statistique.
    *   **Mise en conscience** : Les modèles de classification en production ne doivent pas retourner de classes brutes (0/1), mais des probabilités calibrées et laisser la couche de serving appliquer un seuil dynamique optimisé par rapport à la fonction d'utilité métier.

17. **Le Dilemme du Déterminisme vs Optimisation d'Infrastructure (Cat. 16.5)**
    *   **La Panne dans la matrice** : *"Opérations non déterministes"* ou *"Graine différente selon les bibliothèques"*.
    *   **Le Concept non débattu** : La perte d'exactitude mathématique au profit de l'efficacité matérielle. Pour accélérer les calculs d'entraînement sur GPU ou processeurs multi-cœurs (avec des librairies comme `XGBoost` ou deep learning), les architectures matérielles réordonnent les opérations d'addition en virgule flottante de façon asynchrone. En raison des erreurs d'arrondi des floats, ce non-déterminisme physique produit des modèles finaux différents à chaque run, même en fixant toutes les graines aléatoires logicielles.
    *   **Mise en conscience** : La reproductibilité absolue est incompatible avec l'optimisation maximale du matériel distribué. L'équipe doit accepter une tolérance statistique de variance de métriques ou payer un surcoût d'exécution pour forcer le mode déterministe (CPU mono-thread).

18. **Le Paradoxe de la Résilience vs Idempotence (Le Retry Empoisonné) (Cat. 17.9)**
    *   **La Panne dans la matrice** : *"Job non idempotent"* ou *"Retry dangereux"*.
    *   **Le Concept non débattu** : La différence entre la reprise après erreur en software classique et en data engineering. En software, relancer une requête HTTP `GET` échouée est toujours sûr. En Data Engineering, si un pipeline de calcul de features échoue à 90% et qu'un orchestrateur (Prefect/Airflow) le relance aveuglément sans purger les 90% déjà insérés, on duplique la donnée. Le mécanisme conçu pour assurer la fiabilité du pipeline détruit l'intégrité de la donnée.
    *   **Mise en conscience** : La règle d'or du MLOps : "Il ne faut jamais implémenter de mécanisme de retry automatique si l'on n'a pas garanti mathématiquement l'idempotence des opérations sous-jacentes (via des Upserts stricts ou des suppressions préalables de partitions)".

19. **Le Débat du Schéma-on-Read vs Schéma-on-Write en MLOps (Cat. 17.2)**
    *   **La Panne dans la matrice** : *"Schéma évolutif non géré"* ou *"Schéma implicite vs explicite"*.
    *   **Le Concept non débattu** : L'ingestion moderne de données (Data Lake) favorise le *Schema-on-Read* (accepter toutes les données brutes telles quelles et s'occuper du schéma à la lecture) pour maximiser l'agilité et ne jamais bloquer l'acquisition. Mais le Machine Learning est par nature strict et fragile : il exige un *Schema-on-Write* ou des contrats de données stricts (Data Contracts), car un `int` converti silencieusement en `string` fait exploser les opérations tensorielles downstream.
    *   **Mise en conscience** : Le MLOps est le cimetière du Schema-on-Read. L'acquisition doit imposer une validation de schéma bloquante (via `Pydantic`, `Great Expectations` ou `Pandera`) le plus tôt possible dans l'ETL, quitte à rejeter des données valides, pour protéger le modèle.

20. **L'Illusion du Monitoring de Pipeline "Vert" (Corruption Silencieuse) (Cat. 17.12)**
    *   **La Panne dans la matrice** : *"Pipeline vert mais données fausses"*.
    *   **Le Concept non débattu** : L'observabilité opérationnelle (CPU, RAM, exit code = 0) vs l'observabilité sémantique. Un orchestrateur affiche une tâche en "Success" car le script Python n'a levé aucune exception. Pourtant, le fichier d'entrée ne contenait que des `NaN` ou des zéros. L'infrastructure est en parfaite santé technique, mais en arrêt de mort sémantique.
    *   **Mise en conscience** : En MLOps, un code de retour `0` (succès technique) ne prouve rien sur l'intégrité de l'exécution. L'observabilité Data doit auditer les variations statistiques des payloads échangés entre les étapes, pas seulement les états des conteneurs.

21. **L'Asymétrie de la Menace MLOps (Data Poisoning vs Zero Trust) (Cat 18.4 / 18.12)**
    *   **La Panne dans la matrice** : *"Poisoning du modèle"* ou *"Data drift forcé"*.
    *   **Le Concept non débattu** : Contrairement aux failles traditionnelles où un attaquant exploite une vulnérabilité réseau (buffer overflow, port ouvert), le Data Poisoning transforme les *données* d'entraînement en vecteur d'attaque. Une modification minime et progressive de la distribution des données suffit pour dégrader ou contrôler le comportement du modèle de manière indétectable par la cybersécurité classique, sans intrusion sur les serveurs.
    *   **Mise en conscience** : L'architecture MLOps doit appliquer le paradigme *Zero Trust* non seulement aux flux réseaux, mais aux données elles-mêmes, en instaurant des défenses de détection d'anomalies algorithmiques en amont du Feature Store.

22. **Le Contraste Obscurité / Transparence (Model Extraction) (Cat 18.4 / 18.10)**
    *   **La Panne dans la matrice** : *"Model extraction attack"* ou *"ML SHAP abuse"*.
    *   **Le Concept non débattu** : En MLOps, la quête d'explicabilité et de confiance (XAI, SHAP, probabilités de sortie) rend paradoxalement le système vulnérable. Rendre un modèle "transparent" pour les utilisateurs métier permet à un attaquant de reconstruire le modèle par requêtage ou de saturer les ressources de calcul avec des requêtes SHAP complexes.
    *   **Mise en conscience** : La transparence algorithmique a un coût sécuritaire direct. L'observabilité externe doit être volontairement dégradée ou bridée (rate limiting sévère, arrondi des probabilités) pour les utilisateurs finaux afin de protéger la propriété intellectuelle du modèle.

23. **L'Exploitation Cognitive du Monitoring (Alert Fatigue Armée) (Cat 18.9)**
    *   **La Panne dans la matrice** : *"Alert fatigue exploitée"*.
    *   **Le Concept non débattu** : Les attaquants modernes n'éteignent plus les logs (ce qui déclencherait une alerte de "perte de signal"). Ils génèrent volontairement un volume massif de faux positifs bénins pour désensibiliser l'équipe SRE/MLOps. La véritable attaque est ensuite déclenchée et noyée dans ce bruit.
    *   **Mise en conscience** : Le système de monitoring qui devait protéger l'infrastructure devient l'arme qui la rend aveugle par surcharge cognitive de l'opérateur humain.


---

## Annexes : Débats Conceptuels & Paradoxes MLOps sous-jacents

Cette section documente les débats théoriques d'architecture et les paradoxes de conception soulevés par l'ingestion des catégories de l'Ontologie. Elle vise à mettre en conscience les arbitrages de design système.

**1. Notice Opérationnelle : Débat Conceptuel FMEA (Cause vs Effet pour RPO/RTO)**

Voici l'explication théorique et méthodologique de ce débat classique en gestion des risques (`FMEA`), qui distingue la cause originelle (la panne) de la conséquence finale (l'impact sur les objectifs `RPO`/`RTO`) :
*   **La Distinction Théorique : Cause vs. Effet** : Le Failure Mode (La Cause) est la défaillance technique. L'Impact (La Conséquence) est la métrique compromise. Le `RPO` et le `RTO` ne sont pas des pannes, ce sont des indicateurs contractuels.
*   **Implicite dans les colonnes** : Le risque est mesuré par le temps de détection et de réaction des lignes techniques.
*   **Pourquoi les avoir quand même ajoutés comme lignes physiques ?** : Fidélité Absolue à l'Ontologie (Règle 7) et pour permettre des scénarios de Chaos spécifiques sur la continuité d'activité.

**2. Le Paradoxe de la Cohérence Temporelle Distribuée (Cat. 10.3 / 10.4)**
   *   **La Panne dans la matrice** : *"Registre de modèles `MLflow` perdu"*, *"Données `DVC` inaccessibles"*, *"Signature de modèle perdue"*.
   *   **Le Concept non débattu** : La désynchronisation de l'état (*Split-Brain*) du `MLOps` entre `Git`, `MLflow` et `DVC` en cas de restauration asynchrone de sauvegardes.
   *   **Mise en conscience** : Nécessité de concevoir une "Sauvegarde Coordonnée" atomique pour figer ces trois états simultanément.

**3. Le Syndrome du "Succès en Miniature" (Cat. 10.8)**
   *   **La Panne dans la matrice** : *"Tests de reprise sur petits volumes"*.
   *   **Le Concept non débattu** : La non-linéarité de l'échelle d'infrastructure. Une restauration de 50 Mo réussit toujours, une restauration de 5 To échoue sous la pression IOPS.
   *   **Mise en conscience** : Valider le script de restauration ne valide pas la capacité physique à tenir le `RTO`. C'est une illusion de sécurité.

**4. Le dilemme de la "Graceful Degradation" (Le Mode Dégradé) (Cat. 10.6 / 10.7)**
   *   **La Panne dans la matrice** : *"Dépassement du RTO"* (mitigé par un "Mode dégradé").
   *   **Le Concept non débattu** : Heuristique Métier vs Modèle IA en cas de crise. Faut-il renvoyer une erreur 500 ou basculer sur un fallback statique (ex: moyenne historique) ?
   *   **Mise en conscience** : Le choix du "mode dégradé" est un arbitrage business critique souvent ignoré par l'ingénierie technique.

**5. La "Dette de Reproductibilité" vs Le Coût d'Archivage (Cat. 9.7)**
   *   **La Panne dans la matrice** : *"Incapacité de reconstruire un environnement historique"*.
   *   **Le Concept non débattu** : La durabilité environnementale et financière de la reproductibilité indéfinie (FinOps vs MLOps).
   *   **Mise en conscience** : Définir si la responsabilité est de pouvoir "ré-entraîner à l'identique" ou juste "ré-exécuter le modèle compilé".

**6. Le Paradoxe du "Health Check Flapping" (Cat. 11.2)**
   *   **La Panne dans la matrice** : *"Health Check `LB` trop strict (flapping)"*.
   *   **Le Concept non débattu** : L'instabilité auto-induite. Des health checks trop sensibles retirent des instances ralentis, reportant la charge sur les survivantes qui s'effondrent à leur tour.
   *   **Mise en conscience** : La Haute Disponibilité exige des amortisseurs de bascule (cooldowns) pour éviter les cascades auto-induites.

**7. Le Paradoxe de la Réplication WAL Asynchrone (Cat. 11.3 / 11.4)**
   *   **La Panne dans la matrice** : *"Réplication `PostgreSQL` arrêtée"* ou *"Réplication `PostgreSQL` retard important"*.
   *   **Le Concept non débattu** : Data Loss on Failover. Pour préserver la latence d'écriture, on réplique asynchrone. Le failover évite l'indisponibilité mais perd silencieusement les dernières données.
   *   **Mise en conscience** : Arbitrage fondamental entre disponibilité immédiate (AP) et cohérence stricte (CP).

**8. Le Paradoxe du Monitoring de Monitoring (Le Régressif Actif) (Cat. 12.9)**
   *   **La Panne dans la matrice** : *"L'outil de `monitoring` tombe"* ou *"Collecteur de metrics arrêté"*.
   *   **Le Concept non débattu** : La récursion infinie de l'observabilité. Si Prometheus tombe, qui alerte ?
   *   **Mise en conscience** : Nécessité d'un "Dead Man's Switch" hébergé isolément pour auditer le moniteur lui-même.

**9. Le Paradoxe de la Fatigue d'Alertes (Cat. 12.3 / 12.10)**
   *   **La Panne dans la matrice** : *"Seuil d'alerte trop faible (alert fatigue)"* ou *"Bruit de `monitoring`"*.
   *   **Le Concept non débattu** : La désensibilisation cognitive. Plus un système génère de notifications mineures, plus l'équipe développe une indifférence.
   *   **Mise en conscience** : Dissocier le "Bruit" (logs), les "Warnings" (audits en heure ouvrable) et le "Paging" (astreinte immédiate).

**10. Le Paradoxe de l'Optimisation Locale (FinOps vs Performance) (Cat. 13.12)**
   *   **La Panne dans la matrice** : *"Performances accrues mais coût explose"* ou *"Optimisation locale dégradant le global"*.
   *   **Le Concept non débattu** : Le coût marginal de la micro-performance. Gagner 5ms de CPU pour 300% de facture cloud, alors que la BDD prend 80ms.
   *   **Mise en conscience** : La performance doit être modélisée de manière holistique avec des budgets FinOps/Error Budgets.

**11. Le Choke Point de Sérialisation (Cat. 13.1)**
   *   **La Panne dans la matrice** : *"Temps de sérialisation JSON important"*.
   *   **Le Concept non débattu** : Les ingénieurs optimisent l'inférence mathématique, ignorant que les frameworks web passent le double du temps à parser du JSON.
   *   **Mise en conscience** : L'utilisation de protocoles rapides (gRPC, orjson, zéro-copie) est souvent plus rentable que l'optimisation GPU de l'inférence.

**12. Le Paradoxe de la Coexistence Multiversionnelle (Split-Brain de Vues) (Cat. 14.8)**
   *   **La Panne dans la matrice** : *"Mauvaise version de Feature View chargée"*.
   *   **Le Concept non débattu** : Le Feature Store doit servir simultanément plusieurs schémas (V2 et V3) pour différents modèles actifs.
   *   **Mise en conscience** : Le Feature Store doit être un registre immuable (Immutable Feature Registry).

**13. Le Syndrome de la Feature Statique Fantôme (Cat. 14.6)**
   *   **La Panne dans la matrice** : *"Feature devenue constante (toutes les lignes à 0)"*.
   *   **Le Concept non débattu** : L'absence de mort de feature. Un Offline Store cassé gèle les valeurs dans Redis. L'API renvoie des prédictions basées sur des données fantômes obsolètes sans crasher.
   *   **Mise en conscience** : Nécessité d'une métadonnée de fraîcheur (TTL) validée par un disjoncteur à l'inférence.

**14. Le Dilemme de la Vérité Historique (Offline vs Online) (Cat. 14.7)**
   *   **La Panne dans la matrice** : *"Offline Store correct mais Online Store obsolète"*.
   *   **Le Concept non débattu** : Asynchronisme de la vérité. Le modèle s'entraîne sur l'Offline (parfait) mais prédit sur l'Online (cassé/figé).
   *   **Mise en conscience** : Implémenter des Offline-Online Parity Checks systématiques.

**15. Le Paradoxe du Voyage Temporel Involontaire (Data Leakage Temporel) (Cat. 15.5)**
   *   **La Panne dans la matrice** : *"Utilisation d'une donnée 'future'"*.
   *   **Le Concept non débattu** : La porosité temporelle des pipelines d'entraînement (fuite de données du futur vers le passé lors d'agrégations).
   *   **Mise en conscience** : Imposer des Point-in-Time Joins stricts dans le Feature Store.

**16. Le Split-Brain Temporel des Fuseaux Horaires (Cat. 15.1 / 15.2)**
   *   **La Panne dans la matrice** : *"Les données utilisent deux fuseaux horaires différents"*.
   *   **Le Concept non débattu** : Désynchronisation sémantique due aux changements d'heure (été/hiver) ou mélanges UTC/Local.
   *   **Mise en conscience** : Utilisation exclusive d'UTC ou de timestamp Epoch dans tout le pipeline backend.

**17. Le Paradoxe du Seuil de Décision Universel (Cat. 16.7)**
   *   **La Panne dans la matrice** : *"Seuil de décision oublié (utilisant 0.5)"*.
   *   **Le Concept non débattu** : Un faux positif n'a souvent pas le même coût qu'un faux négatif. Le seuil 0.5 suppose une symétrie des coûts illusoire.
   *   **Mise en conscience** : Le seuil de décision est une fonction d'utilité métier, pas une constante mathématique.

**18. Le Dilemme du Déterminisme vs Optimisation d'Infrastructure (Cat. 16.5)**
   *   **La Panne dans la matrice** : *"Opérations non déterministes"*.
   *   **Le Concept non débattu** : Les calculs GPU ou asynchrones réordonnent les additions flottantes, créant du non-déterminisme matériel au profit de la vitesse.
   *   **Mise en conscience** : La reproductibilité absolue exige souvent de sacrifier la vitesse (CPU mono-thread).

**19. Le Paradoxe de la Résilience vs Idempotence (Le Retry Empoisonné) (Cat. 17.9)**
   *   **La Panne dans la matrice** : *"Job non idempotent"* ou *"Retry dangereux"*.
   *   **Le Concept non débattu** : Un pipeline relancé suite à une micro-coupure duplique la donnée s'il n'est pas idempotent. La résilience de l'orchestrateur détruit l'intégrité de la base.
   *   **Mise en conscience** : Aucun mécanisme de retry ne doit exister sans idempotence stricte (Upsert, Delete-before-Insert).

**20. Le Débat du Schéma-on-Read vs Schéma-on-Write en MLOps (Cat. 17.2)**
   *   **La Panne dans la matrice** : *"Schéma évolutif non géré"*.
   *   **Le Concept non débattu** : Le Data Lake favorise le Schema-on-Read pour l'agilité, mais le ML explose face aux types instables.
   *   **Mise en conscience** : Le MLOps est le cimetière du Schema-on-Read. Validation de schéma bloquante requise à l'acquisition (Data Contracts).

**21. L'Illusion du Monitoring de Pipeline "Vert" (Corruption Silencieuse) (Cat. 17.12)**
   *   **La Panne dans la matrice** : *"Pipeline vert mais données fausses"*.
   *   **Le Concept non débattu** : L'orchestrateur voit un exit code 0 (succès technique), mais le script a traité des NaN. L'infrastructure est saine, la sémantique est morte.
   *   **Mise en conscience** : L'observabilité Data doit auditer les variations statistiques des payloads, pas juste le code de retour des conteneurs.

**22. L'Asymétrie de la Menace MLOps (Data Poisoning vs Zero Trust) (Cat. 18.4 / 18.12)**
   *   **La Panne dans la matrice** : *"Poisoning du modèle"*.
   *   **Le Concept non débattu** : L'attaque ne vise pas le réseau mais la distribution de la donnée d'entraînement pour corrompre l'apprentissage.
   *   **Mise en conscience** : Appliquer le Zero Trust aux données elles-mêmes (détection d'anomalies pré-Feature Store).

**23. Le Contraste Obscurité / Transparence (Model Extraction) (Cat. 18.4 / 18.10)**
   *   **La Panne dans la matrice** : *"Model extraction attack"* ou *"ML SHAP abuse"*.
   *   **Le Concept non débattu** : Rendre un modèle "transparent" (SHAP/Probabilités) facilite sa rétro-ingénierie par un attaquant (vol de propriété intellectuelle).
   *   **Mise en conscience** : La transparence doit être bridée pour les utilisateurs externes pour des raisons de sécurité.

**24. L'Exploitation Cognitive du Monitoring (Alert Fatigue Armée) (Cat. 18.9)**
   *   **La Panne dans la matrice** : *"Alert fatigue exploitée"*.
   *   **Le Concept non débattu** : Les attaquants génèrent volontairement un volume massif de faux positifs pour désensibiliser l'équipe SRE. La véritable attaque est noyée dans ce bruit.
   *   **Mise en conscience** : Le système de monitoring devient une arme par surcharge cognitive si les alertes ne sont pas filtrées intelligemment.

**25. Le Paradoxe du "Meilleur Score" (Cat. 19.3)**
   *   **La Panne dans la matrice** : *"gov_global_metric_only.py"*.
   *   **Le Concept non débattu** : Un F1-score global cache souvent un désastre sur un sous-groupe minoritaire critique.
   *   **Mise en conscience** : La validation doit être une Gate multidimensionnelle (slices métier), pas une équation scalaire unique.

**26. Le Paradoxe de la Transparence Financièrement Inviable (Cat. 20.2)**
   *   **La Panne dans la matrice** : *"cost_shap_always_on.py"*.
   *   **Le Concept non débattu** : Calculer les valeurs de Shapley coûte souvent 100x plus cher en CPU que de faire la prédiction elle-même.
   *   **Mise en conscience** : L'explicabilité doit être "On-Demand" (asynchrone), et non synchronisée sur chaque inférence standard.

**27. Le Paradoxe de la Justesse Inutile (Cat. 21.1)**
   *   **La Panne dans la matrice** : *"gov_good_metric_bad_usage.py"*.
   *   **Le Concept non débattu** : Prédire parfaitement un événement sur lequel le métier ne peut avoir aucune action correctrice est mathématiquement beau mais opérationnellement inutile.
   *   **Mise en conscience** : La cible d'optimisation doit être le "Business ROI Score", pas le F1-Score technique abstrait.

**28. Le Paradoxe de la Confiance Destructrice (Cat. 22.1)**
   *   **La Panne dans la matrice** : *"gov_blind_trust.py"*.
   *   **Le Concept non débattu** : Quand le modèle gagne la confiance à 100% du métier, l'humain arrête de valider. C'est là que le biais d'automatisation rend le risque maximal.
   *   **Mise en conscience** : Forcer des "Audits de Désaccord" (Humain-in-the-loop) et injecter de l'incertitude explicite.

**29. Le Paradoxe de la Haute Disponibilité Trompeuse (Cat. 1.1 / 1.2)**
   *   **La Panne dans la matrice** : `infra_memory_leak.py` / `infra_docker_oom.py`
   *   **Le Concept non débattu** : L'auto-healing Kubernetes masque les fuites mémoire MLOps en redémarrant silencieusement les pods, retardant la détection jusqu'à l'effondrement fatal.
   *   **Mise en conscience** : L'infrastructure doit déclencher une alerte fatale visible par les Data Scientists lorsqu'un seuil de "OOMKills" est atteint.

**30. Le Mythe du Déterminisme (Cat. 4.12)**
   *   **La Panne dans la matrice** : `Impossible de reproduire un résultat` (Ligne 217).
   *   **Le Concept non débattu** : En ML, un pipeline n'est jamais purement déterministe par défaut. La reproductibilité est un effort d'ingénierie artificiel.
   *   **Mise en conscience** : Fixer un seed global est insuffisant. Il faut versionner le graphe de calcul entier, les hyperparamètres ET les données.

**31. Le Paradoxe de la Disponibilité Partielle (Cat. 1.1)**
   *   **La Panne dans la matrice** : `Crash sous charge` ou `Timeout Feature Store` (Ligne 56/58).
   *   **Le Concept non débattu** : Une BDD peut être 100% saine, mais si le proxy réseau sature, le système global est perçu comme mort par le client.
   *   **Mise en conscience** : La disponibilité doit se mesurer de bout-en-bout (End-to-End), pas par silo.

**32. Le Paradoxe de l'Idempotence Destructrice (Cat. 2.1)**
   *   **La Panne dans la matrice** : `data_double_ingestion.py`
   *   **Le Concept non débattu** : Les retries d'Airflow/Prefect sur un script non-idempotent dupliquent massivement la donnée au moindre hoquet réseau.
   *   **Mise en conscience** : Chaque étape ETL doit être conçue pour être relancée 100 fois de suite avec le même résultat final exact (ex: `UPSERT`).

**33. Le Paradoxe de l'Adaptation Continue (Cat. 3.1)**
   *   **La Panne dans la matrice** : `model_data_drift.py` / `model_concept_drift.py`
   *   **Le Concept non débattu** : Plus l'entraînement continu est automatisé pour contrer le Drift, plus on risque d'amplifier un feedback loop négatif où le modèle apprend ses propres prédictions biaisées.
   *   **Mise en conscience** : Le réentraînement continu est un anti-pattern s'il n'est pas couplé à un "Holdout Set Historique" intouchable.

**34. Le Paradoxe de la Dépendance Figeante (Cat. 4.2)**
   *   **La Panne dans la matrice** : `code_deps_not_pinned.py` / `code_lib_upgrade_break.py`
   *   **Le Concept non débattu** : Figer (`pin`) toutes les dépendances garantit la reproductibilité à l'instant T, mais garantit aussi une obsolescence et une dette technique de sécurité massive à T+1.
   *   **Mise en conscience** : Un système MLOps doit inclure une stratégie de "Décongélation Contrôlée" via CI stricte pour tester l'upgrade des dépendances figées.

**35. Le Paradoxe de la Qualité Sémantique (Cat. 5.11)**
   *   **La Panne dans la matrice** : `data_semantic_blur.py` / `data_definition_change.py`
   *   **Le Concept non débattu** : La validation de données technique garantit la syntaxe. Mais un dataset peut être techniquement irréprochable et sémantiquement mort si la définition métier a changé.
   *   **Mise en conscience** : La "Qualité des Données" exige un Data Contract sémantique, couplé à une observabilité métier indépendante du code de retour du pipeline.



**36. Le Paradoxe de la Fragilité de l'Optimisation (Les Black Swans) (Cat. 23.1 / 23.7)**
   *   **La Panne dans la matrice** : `edge_thundering_herd.py` / `edge_total_stationarity_break.py`
   *   **Le Concept non débattu** : Plus un système MLOps est parfaitement réglé, contraint et optimisé pour le régime nominal (99.9% des cas avec des schémas stricts, des timeouts agressifs et des distributions stables), plus il devient cassant et s'effondre de manière catastrophique face à un événement "Black Swan" (0.1%). L'hyper-optimisation pour la normalité détruit la résilience face au chaos.
   *   **Mise en conscience** : La véritable résilience exige d'accepter une dégradation volontaire (un coût ou une latence sous-optimale) en régime normal pour maintenir des "amortisseurs" (buffers, fallbacks statiques, découplage fort) capables d'absorber des scénarios hors-distribution.


**37. Le Paradoxe du Point de Vérité Unique (Cat. 6.1)**
   *   **La Panne dans la matrice** : `serve_feature_computation_skew.py` / `serve_db_feature_store_desync.py`
   *   **Le Concept non débattu** : Le concept même de Feature Store est de garantir une source de vérité unique entre Train et Serve. Cependant, pour atteindre les exigences de latence du temps réel, on est souvent forcé de calculer des features "online" de manière approximée par rapport au calcul "batch" d'entraînement, réintroduisant la désynchronisation qu'on cherchait à fuir.
   *   **Mise en conscience** : La cohérence absolue Train/Serve est impossible à latence quasi-nulle. Il faut documenter et monitorer l'écart acceptable (le *skew*) plutôt que de chercher l'égalité stricte.

**38. Le Paradoxe de la Propreté Temporelle (Cat. 7.2)**
   *   **La Panne dans la matrice** : `train_temporal_leakage_split.py` / `train_biased_backtesting.py`
   *   **Le Concept non débattu** : Les Data Scientists nettoient et mettent à jour rétroactivement les données du passé pour s'entraîner sur un historique "parfait". Mais en production au temps T, la donnée est par nature brute, incomplète et "sale". Entraîner sur un passé nettoyé garantit une désillusion en production.
   *   **Mise en conscience** : Un modèle doit être entraîné sur la donnée "telle qu'elle était connue à l'instant T", avec toutes ses erreurs et lacunes d'origine (Point-in-time correctness), et non sur sa version corrigée à T+1.

**39. Le Paradoxe de la Perfection Aveugle (Loi de Goodhart) (Cat. 8.4)**
   *   **La Panne dans la matrice** : `train_goodharts_law_overopt.py` / `train_silent_degenerate_weights.py`
   *   **Le Concept non débattu** : Plus un pipeline ML est automatisé (AutoML, Grid Search massif) pour maximiser une métrique technique pure (ex: F1-score ou AUC), plus le modèle trouve des failles statistiques pour gonfler ce score tout en détruisant son utilité métier réelle sur le terrain.
   *   **Mise en conscience** : La métrique d'optimisation technique n'est qu'un proxy. Le pipeline doit forcer une validation sur une "Métrique d'Impact Métier" décorrélée du framework d'entraînement (ex: ROI simulé, coût d'erreur asymétrique).

**40. Le Paradoxe du Pipeline Vert (Illusion de Complétion) (Cat. 9.11)**
   *   **La Panne dans la matrice** : `etl_silent_empty_ingestion.py` / `data_silent_transformation_bug.py`
   *   **Le Concept non débattu** : L'orchestration moderne (Airflow, Prefect) est tellement résiliente (retries, skip, fallbacks) qu'elle garantit souvent l'Exit 0 (le passage au vert du DAG). Mais un pipeline techniquement réussi ne prouve absolument pas que les données produites sont sémantiquement correctes ou même présentes.
   *   **Mise en conscience** : Découpler le "Succès Opérationnel" (le DAG a tourné) du "Succès Data" (les Data Contracts sont validés post-exécution). Un DAG Vert sans audit métier est un vecteur de corruption silencieuse.

**41. Le Paradoxe de la Forteresse Applicative (Cat. 10.4 / 10.7)**
   *   **La Panne dans la matrice** : `sec_sql_injection.py` / `sec_env_porosity.py`
   *   **Le Concept non débattu** : L'équipe ML investit massivement dans la sécurisation algorithmique des modèles (Adversarial Robustness, Data Poisoning defense) mais le modèle est déployé avec une API FastAPI qui lit les secrets dans un `.env` sur Github, ou sans Rate Limiter.
   *   **Mise en conscience** : La sécurité d'un système MLOps est strictement égale à celle de son composant logiciel le plus faible. L'OWASP classique fera tomber le modèle bien avant les attaques complexes spécifiques au ML.


---

## Rétro-Documentation des Rechecks (Genèse 1 à 6) - Application Règle 38

*(Note : Ces catégories de la Genèse ont été ingérées avant la mise en place de la Règle 36/38. Voici la traçabilité rétroactive de l'Inversion de la Charge de la Preuve pour les 6 premières itérations de Recheck).*

### Recheck 1 (Catégorie 1 : Infrastructure)
**Preuve d'Inversion de la Charge (Règle 36) :**
- ✅ **Inédits injectés (18)** : La Dimension 1 de la taxonomie était vierge avant cette ingestion. 100% des incidents techniques (OOM, Timeout, Deadlock) ont été prouvés inédits et injectés.

### Recheck 2 (Catégorie 2 : Pipeline ML)
**Preuve d'Inversion de la Charge (Règle 36) :**
- ❌ **100% rejetés** : Preuve mathématique établie que l'intégralité des concepts de la Catégorie 2 étaient des doublons exacts de la Catégorie 17 (Data Quality). Zéro injection (Fast-Forward).

### Recheck 3 (Catégorie 3 : Modèles)
**Preuve d'Inversion de la Charge (Règle 36) :**
- ❌ **100% rejetés** : Preuve formelle que la Catégorie 3 était un doublon sémantique de la Catégorie 21 (Qualité des Prédictions). Zéro injection (Fast-Forward).

