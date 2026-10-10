from typing import Dict, Optional, Literal
from pydantic import BaseModel, Field, field_validator
import re

class PolicyCondition(BaseModel):
    """Conditions strictes autorisées pour une action."""
    blast_radius_max: Optional[int] = Field(None, ge=0, description="Niveau de risque maximal autorisé (0-10).")
    rate_limit: Optional[str] = Field(None, description="Format X/hour, X/minute, X/day")

    @field_validator('rate_limit')
    @classmethod
    def validate_rate_limit(cls, v):
        if v and not re.match(r'^\d+/(hour|minute|day)$', v):
            raise ValueError("rate_limit invalide. Format attendu : X/hour, X/minute, X/day (ex: 1/hour).")
        return v

class PolicyRule(BaseModel):
    """Règle de gouvernance pour une action LLM."""
    autonomy: Literal["autonomous", "human_approval_required", "deny"] = "human_approval_required"
    conditions: Optional[PolicyCondition] = Field(default_factory=PolicyCondition)

class PolicyManifest(BaseModel):
    """Manifeste complet de la politique de sécurité MLOps."""
    policy_version: str
    rules: Dict[str, PolicyRule]
