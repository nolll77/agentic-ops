import json
import logging
import hmac
import hashlib
import time
from typing import Any
from fastapi import FastAPI, Request, HTTPException, Depends

logger = logging.getLogger("SlackWebhook")

app = FastAPI(title="AgenticOps HITL Webhook")

import os
SLACK_SIGNING_SECRET = os.environ.get("SLACK_SIGNING_SECRET")
if not SLACK_SIGNING_SECRET and os.environ.get("ENVIRONMENT") == "production":
    raise RuntimeError("Fail-Safe: SLACK_SIGNING_SECRET est obligatoire en production.")
SLACK_SIGNING_SECRET = SLACK_SIGNING_SECRET or "dummy_secret_for_tests"


async def verify_slack_signature(request: Request):
    """
    Middleware de validation cryptographique HMAC-SHA256 (Fix P0 Audit).
    Vérifie que la requête HTTP provient bien de Slack et bloque les attaques par rejeu.
    """
    timestamp = request.headers.get("X-Slack-Request-Timestamp")
    slack_signature = request.headers.get("X-Slack-Signature")
    
    if not timestamp or not slack_signature:
        raise HTTPException(status_code=400, detail="Missing Slack signature headers")
        
    # Prévention des Replay Attacks (Max 5 minutes d'âge)
    if abs(time.time() - int(timestamp)) > 60 * 5:
        raise HTTPException(status_code=400, detail="Replay attack detected. Timestamp too old.")
        
    body = await request.body()
    sig_basestring = f"v0:{timestamp}:{body.decode('utf-8')}"
    
    my_signature = 'v0=' + hmac.new(
        SLACK_SIGNING_SECRET.encode(),
        sig_basestring.encode(),
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(my_signature, slack_signature):
        logger.critical("🚨 [HITL SECURITY] Signature Slack invalide (Tentative de forgeage)")
        raise HTTPException(status_code=401, detail="Invalid signature")

@app.post("/webhook/slack/interactive", dependencies=[Depends(verify_slack_signature)])
async def process_slack_interaction(request: Request, orchestrator: Any = None, evidence_store: Any = None):
    """
    Reçoit un payload interactif (Bouton Block Kit) de Slack.
    Bloqué par `verify_slack_signature` si la source n'est pas authentique.
    """
    try:
        body = await request.body()
        payload_str = body.decode('utf-8')
        
        # En vrai, le body contient payload=urlencoded_json, on simplifie pour le proof of concept
        if payload_str.startswith("payload="):
            from urllib.parse import unquote
            payload_str = unquote(payload_str[8:])
            
        interaction = json.loads(payload_str)
        action_value = interaction["actions"][0]["value"]  # ex: "APPROVE_EP-0042"
        user_name = interaction["user"]["username"]
        
        decision, episode_id = action_value.split("_", 1)
        if decision not in {"APPROVE", "DENY"}:
            logger.critical(f"🚨 TENTATIVE D'INJECTION WEBHOOK : Décision '{decision}' interdite.")
            raise HTTPException(status_code=400, detail="Décision inconnue")
        logger.info(f"Interaction reçue : {decision} pour {episode_id} par {user_name}")
        
        if evidence_store is None or orchestrator is None:
            return {"status": "success", "message": "Mode standalone (Test). Signature validée."}
            
        episode_path = evidence_store.store_dir / f"{episode_id}.json"
        if not episode_path.exists():
            raise HTTPException(status_code=404, detail="Episode introuvable")
            
        with open(episode_path, "r") as f:
            episode = json.load(f)
            
        if episode.get("state_machine_trace", [])[-1] != "AWAITING_APPROVAL":
            raise HTTPException(status_code=400, detail="Cet épisode n'est pas en attente d'approbation")
            
        episode["human_approval"] = {
            "required": True,
            "approval_record": {
                "decision": decision,
                "approved_by": user_name,
                "timestamp": time.time(),
                "signature_verified": True
            }
        }
        
        orchestrator.resume_episode(episode)
        
        return {"status": "success", "message": f"Épisode {episode_id} repris avec décision {decision}"}
        
    except Exception as e:
        logger.error(f"Erreur de traitement Webhook Slack: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid payload")
