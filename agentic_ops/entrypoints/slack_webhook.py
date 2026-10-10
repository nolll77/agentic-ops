import json
import logging
from pydantic import BaseModel
from typing import Dict, Any

logger = logging.getLogger("SlackWebhook")

class SlackInteractionPayload(BaseModel):
    # Simplification du payload Slack Block Kit
    payload: str 

def process_slack_interaction(payload_str: str, orchestrator, evidence_store):
    """
    Simule la réception d'un clic de bouton depuis Slack.
    Reprend l'épisode depuis le Evidence Store et relance l'Orchestrateur.
    """
    try:
        interaction = json.loads(payload_str)
        action_value = interaction["actions"][0]["value"]  # ex: "APPROVE_EP-0042"
        user_name = interaction["user"]["username"]
        
        decision, episode_id = action_value.split("_", 1)
        logger.info(f"Interaction reçue : {decision} pour {episode_id} par {user_name}")
        
        # 1. Charger l'épisode depuis le store
        episode_path = evidence_store.store_dir / f"{episode_id}.json"
        if not episode_path.exists():
            return {"error": "Episode introuvable"}
            
        with open(episode_path, "r") as f:
            episode = json.load(f)
            
        # 2. Vérifier l'état
        if episode.get("state_machine_trace", [])[-1] != "AWAITING_APPROVAL":
            return {"error": "Cet épisode n'est pas en attente d'approbation"}
            
        # 3. Injecter la décision humaine
        episode["human_approval"] = {
            "required": True,
            "approval_record": {
                "decision": decision,
                "approved_by": user_name,
                "timestamp": "now"
            }
        }
        
        # 4. Relancer l'orchestrateur (Reprise)
        orchestrator.resume_episode(episode)
        
        return {"status": "success", "message": f"Épisode {episode_id} repris avec décision {decision}"}
        
    except Exception as e:
        logger.error(f"Erreur de traitement Webhook Slack: {str(e)}")
        return {"error": "Invalid payload"}
