from typing import List
from agentic_ops.core.telemetry import STATE_TRANSITIONS

class StateMachine:
    """FSM canonique pour le cycle de vie de résolution d'incident MLOps."""
    VALID_STATES = [
        "DETECTED", "INVESTIGATING", "DIAGNOSED", "PLANNED",
        "AWAITING_APPROVAL", "EXECUTING", "RESOLVED", "DENIED"
    ]
    
    def __init__(self, initial: str = "DETECTED"):
        self.current = initial
        self.trace: List[str] = [initial]
        
    def transition(self, next_state: str):
        if next_state not in self.VALID_STATES:
            raise ValueError(f"État invalide: {next_state}")
        STATE_TRANSITIONS.labels(from_state=self.current, to_state=next_state).inc()
        self.current = next_state
        self.trace.append(next_state)
