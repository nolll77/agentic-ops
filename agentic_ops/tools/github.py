from pydantic import BaseModel, Field

from .base import AgentTool


class CreateIssueArgs(BaseModel):
    title: str = Field(..., description="Titre de l'issue.")
    body: str = Field(..., description="Contenu détaillé de l'issue.")
    risk_id: str = Field(..., description="L'ID du risque associé.")


class CreateIssue(AgentTool):
    name = "create_github_issue"
    description = "Crée une Issue sur GitHub pour notifier d'une dérive ou d'un incident. Cet outil exécute une action."
    args_schema = CreateIssueArgs
    requires_approval = True
    timeout_seconds = 10

    readOnlyHint = False
    destructiveHint = False
    idempotentHint = False
    openWorldHint = True

    read_only_hint = False
    destructive_hint = False
    idempotent_hint = False
    open_world_hint = True

    def _execute(self, title: str, body: str, risk_id: str) -> str:
        return f"[Simulé] Issue créée: '{title}' (Risque: {risk_id}). ID #42."
