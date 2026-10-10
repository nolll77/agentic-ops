import json
import logging
import urllib.request
from typing import Dict, Any

from agentic_ops.adapters.protocol import NotificationAdapter

logger = logging.getLogger("SlackAdapter")

class SlackInteractiveAdapter(NotificationAdapter):
    """
    Envoie une requête d'approbation (Block Kit) sur Slack.
    Les boutons déclencheront un Webhook vers le Control Plane.
    """
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    def request_approval(self, episode: Dict[str, Any]) -> None:
        episode_id = episode.get("episode_id", "UNKNOWN")
        risk_id = episode.get("risk_id", "UNKNOWN")
        action = episode.get("action_proposal", {})
        action_type = action.get("type", "UNKNOWN")
        
        # Slack Block Kit Payload
        payload = {
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "🚨 MLOps Control Plane : Approbation Requise",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Épisode :* `{episode_id}`\n*Risque :* `{risk_id}`\n*Action Demandée :* `{action_type}`\n\nLe Policy Engine a bloqué cette action et requiert une validation humaine."
                    }
                },
                {
                    "type": "actions",
                    "block_id": f"approval_actions_{episode_id}",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "✅ Approuver",
                                "emoji": True
                            },
                            "style": "primary",
                            "value": f"APPROVE_{episode_id}"
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "❌ Rejeter",
                                "emoji": True
                            },
                            "style": "danger",
                            "value": f"DENY_{episode_id}"
                        }
                    ]
                }
            ]
        }
        
        # Simulation de l'appel HTTP vers Slack
        print(f"[Slack] Sending approval request for {episode_id} to webhook...")
        # req = urllib.request.Request(
        #     self.webhook_url, 
        #     data=json.dumps(payload).encode('utf-8'),
        #     headers={'Content-Type': 'application/json'}
        # )
        # urllib.request.urlopen(req)
