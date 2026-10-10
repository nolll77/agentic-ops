# Post-Mortem & Runbook : INFRA-001 (OOMKilled Pod)
**Dernière occurrence** : 3 Novembre 2025
**Symptôme** : Le pod `fastapi-serving` consomme toute la mémoire et se fait tuer par le contrôleur K8s (OOMKilled).
**Root Cause Historique** : Fuite mémoire dans le cache LRU du modèle Scikit-Learn ou pic de prédictions batch.
**Remédiation Recommandée (Résolution Éprouvée)** :
1. Action immédiate : `restart_pod` pour rétablir le service (Mitigation).
2. Action secondaire (si récidive) : `scale_up` (ajouter +2 replicas).
3. Toujours escalader en mode `REQUIRE_APPROVAL` si le pod a déjà été redémarré dans l'heure.
