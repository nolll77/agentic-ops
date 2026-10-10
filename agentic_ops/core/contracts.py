from pydantic import BaseModel, Field
from enum import Enum
from typing import Any, Dict, List, Optional
from datetime import datetime

class Signal(BaseModel):
    signal_id: str
    source: str
    observed_at: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
class ActionType(str, Enum):
    CREATE_ISSUE = "create_issue"
    INVESTIGATE = "investigate"
    PROPOSE_RETRAIN = "propose_retrain"
    RESTART_POD = "restart_pod"
    SCALE_UP = "scale_up"
    ROLLBACK = "rollback"
    PROMOTE_MODEL = "promote_model"

class ActionProposal(BaseModel):
    type: ActionType
    risk_id: str
    requested_by: str
    reversible: bool = False
    blast_radius: int = 0
    parameters: Dict[str, Any] = Field(default_factory=dict)

class ExecutionResult(BaseModel):
    status: str
    executor: str
    result_ref: Optional[str] = None
    details: str

class DecisionEnum(str, Enum):
    ALLOW = "ALLOW"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
    DENY = "DENY"

class Decision(BaseModel):
    decision: DecisionEnum
    matched_rule: str
    shadow_decision: Optional[str] = None
    shadow_divergence: bool = False
    reason_codes: List[str] = Field(default_factory=list)

class Finding(BaseModel):
    description: str

class Diagnosis(BaseModel):
    findings: List[Finding]
    confidence_score: float
    risk_id: Optional[str] = None
    agent: Optional[str] = None

class Episode(BaseModel):
    episode_id: str
    dedup_key: str
    timestamp_utc: datetime
    state_trace: List[str]
    risk_id: str
    signal: Signal
    diagnosis: Diagnosis
    action_proposal: ActionProposal
    policy_evaluation: Decision
    human_approval_required: bool
    execution: Optional[ExecutionResult] = None


class ModelRegistryStatusEnum(str, Enum):
    REGISTERED = "REGISTERED"
    VALIDATED = "VALIDATED"
    REJECTED = "REJECTED"
    ARCHIVED = "ARCHIVED"

class ModelDeploymentStatusEnum(str, Enum):
    CANDIDATE = "CANDIDATE"
    DEPLOYED = "DEPLOYED"
    ACTIVE = "ACTIVE"
    FAILED = "FAILED"

class ModelVersion(BaseModel):
    version_id: str
    metrics: Dict[str, float]
    schema_compatible: bool
    registry_status: ModelRegistryStatusEnum = ModelRegistryStatusEnum.REGISTERED
    deployment_status: ModelDeploymentStatusEnum = ModelDeploymentStatusEnum.CANDIDATE
