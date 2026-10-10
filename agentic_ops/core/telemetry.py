from prometheus_client import Counter, Gauge

# Définition des métriques MLOps critiques
INCIDENTS_TOTAL = Counter(
    "agentic_ops_incidents_total",
    "Nombre total d'incidents interceptés par le control plane",
    ["risk_id", "source"]
)

STATE_TRANSITIONS = Counter(
    "agentic_ops_fsm_transitions_total",
    "Transitions de la Machine à États (FSM)",
    ["from_state", "to_state"]
)

POLICY_DECISIONS = Counter(
    "agentic_ops_policy_decisions_total",
    "Décisions arbitraires du Policy Engine (ALLOW, DENY, REQUIRE_APPROVAL)",
    ["decision", "action_type"]
)

LLM_CONFIDENCE = Gauge(
    "agentic_ops_llm_confidence_score",
    "Score de confiance remonté par l'Agent Spécialiste",
    ["agent_name", "risk_id"]
)

CIRCUIT_BREAKER_STATUS = Gauge(
    'agentic_ops_circuit_breaker_status',
    'Statut du Circuit Breaker FinOps (0=OK, 1=Tripped)'
)

SHADOW_POLICY_DIVERGENCES = Counter(
    'agentic_ops_shadow_policy_divergences_total',
    'Divergences détectées entre la policy Primaire et la Shadow Policy',
    ['action_type', 'primary_decision', 'shadow_decision']
)
