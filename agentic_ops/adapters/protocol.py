from __future__ import annotations
from typing import Protocol
from agentic_ops.core.contracts import Signal, ActionProposal, ExecutionResult

class ObservabilityAdapter(Protocol):
    """Interface to fetch telemetry, metrics, or alerts from an external system."""
    def get_signal(self, signal_id: str) -> Signal: ...

class ExecutionAdapter(Protocol):
    """Interface to execute remediation actions on an external system."""
    def execute(self, action: ActionProposal) -> ExecutionResult: ...
