# Post-Mortem & Runbook : DATA-042 (Data Drift VMA)
**Dernière occurrence** : 14 Septembre 2025
**Symptôme** : Dérive critique (drift_score > 0.2) détectée sur la feature `vma` par Evidently.
**Root Cause Historique** : Un changement réglementaire ou un bug du pipeline d'ingestion a injecté des valeurs aberrantes (ex: VMA à 130 km/h en ville).
**Remédiation Recommandée (Résolution Éprouvée)** : 
1. NE PAS lancer de `retrain` automatique aveuglément (le modèle apprendrait le bruit).
2. Vérifier la distribution des VMA dans la Staging Area.
3. L'action préférentielle est `create_issue` pour assigner l'équipe Data Engineering à l'investigation du Data Contract Pandera.
