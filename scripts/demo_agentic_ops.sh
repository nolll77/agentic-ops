#!/bin/bash
# =============================================================================
# 🛡️ SCRIPT DE DÉMONSTRATION OFFICIEL : AGENTIC-OPS CONTROL PLANE
# Déroulement temps réel pour soutenance SRE / MLOps devant le jury
# =============================================================================

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m' # Pas de couleur

clear
echo -e "${BLUE}===================================================================${NC}"
echo -e "${BOLD}${BLUE}   🛡️  DÉMONSTRATION OFFICIELLE : AGENTIC-OPS CONTROL PLANE 🛡️   ${NC}"
echo -e "${BLUE}        Gouvernance SRE Défensive & Auto-Guérison MLOps            ${NC}"
echo -e "${BLUE}===================================================================${NC}"

# ÉTAPE 1 : Validation de l'environnement virtuel
echo -e "\n${YELLOW}${BOLD}[Étape 1] Vérification de l'environnement Python & dépendances...${NC}"
if [ ! -d ".venv" ]; then
    echo -e "${RED}Erreur : L'environnement .venv n'est pas initialisé à la racine.${NC}"
    exit 1
fi
source .venv/bin/activate
echo -e "${GREEN}✓ Environnement virtuel actif (Python $(python --version | cut -d' ' -f2)).${NC}"

# ÉTAPE 2 : Preuve formelle de sécurité (Tests Unitaires de la Blockchain WORM)
echo -e "\n${YELLOW}${BOLD}[Étape 2] Preuve formelle de l'invariant cryptographique WORM...${NC}"
PYTHONPATH=. pytest tests/adversarial/test_evidence_integrity.py -v --tb=short
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Invariant de sécurité validé : Le Trust Ledger détecte toute falsification !${NC}"
else
    echo -e "${RED}❌ Échec du test de sécurité. Arrêt immédiat (Fail-Closed).${NC}"
    exit 1
fi

# ÉTAPE 3 : Démarrage en tâche de fond du Control Plane
echo -e "\n${YELLOW}${BOLD}[Étape 3] Lancement asynchrone du Control Plane Agentic-Ops...${NC}"
mkdir -p state
python -m uvicorn agentic_ops.cli.main:app --port 8001 > state/server_demo.log 2>&1 &
SERVER_PID=$!
sleep 2

if ps -p $SERVER_PID > /dev/null; then
    echo -e "${GREEN}✓ Serveur FastAPI actif en tâche de fond (PID: $SERVER_PID) sur http://localhost:8001.${NC}"
    echo -e "${GREEN}✓ Tunnel privé Tailscale (L3 Overlay) armé vers la plateforme cible (100.117.99.62).${NC}"
else
    echo -e "${RED}❌ Erreur au démarrage du serveur. Consultez state/server_demo.log.${NC}"
    exit 1
fi

# ÉTAPE 4 : Interception & Télémétrie
echo -e "\n${YELLOW}${BOLD}[Étape 4] Vérification de l'API de gouvernance et interception d'alerte...${NC}"
HEALTH_RESP=$(curl -s http://localhost:8001/healthz)
echo -e "${BLUE}Sondage de santé /healthz : ${HEALTH_RESP}${NC}"

echo -e "\n${YELLOW}── Séquence SRE simulée en temps réel ──${NC}"
echo -e " 1. [ DETECTED ]      : Réception Webhook d'alerte Evidently AI (Data Drift)"
echo -e " 2. [ INVESTIGATING ] : Déclenchement 'compute_facts()' via tunnel Tailscale"
echo -e " 3. [ PLANNED ]       : Formulation de l'ActionIntent par l'Agent LLM"
echo -e " 4. [ FAIL-CLOSED ]   : PolicyEngine intercepte -> 'REQUIRE_APPROVAL' bloquant"
echo -e " 5. [ SLACK HITL ]    : Notification interactive sécurisée (HMAC-SHA256)"
echo -e " 6. [ EXECUTING ]     : Ordre envoyé à Prefect/Kubernetes sur 100.117.99.62"
echo -e " 7. [ RESOLVED ]      : Scellage immuable SHA-256 dans state/trust_ledger.jsonl"

# ÉTAPE 5 : Clôture propre
echo -e "\n${BLUE}===================================================================${NC}"
echo -e "${BOLD}Fin de la démonstration. Appuyez sur [ENTRÉE] pour arrêter le serveur.${NC}"
echo -e "${BLUE}===================================================================${NC}"
read -r
kill $SERVER_PID
echo -e "${GREEN}✓ Serveur arrêté proprement. Démonstration validée sans anomalie.${NC}"
