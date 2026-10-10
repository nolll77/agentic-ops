from __future__ import annotations
from typing import Protocol
from agentic_ops.core.contracts import Signal, ActionProposal, ExecutionResult

class ObservabilityAdapter(Protocol):
    """Interface to fetch telemetry, metrics, or alerts from an external system."""
    def get_signal(self, signal_id: str) -> Signal: ...

class ExecutionAdapter(Protocol):
    """Interface to execute remediation actions on an external system."""
    def execute(self, action: ActionProposal) -> ExecutionResult: ...

class NotificationAdapter(Protocol):
    """Interface pour les notifications et requêtes d'approbation humaines (HITL)."""
    def request_approval(self, episode: dict) -> None: ...

class KnowledgeAdapter(Protocol):
    """Interface pour interroger la base de connaissance MLOps (RAG)."""
    def search_runbooks(self, risk_id: str, query: str) -> str: ...
