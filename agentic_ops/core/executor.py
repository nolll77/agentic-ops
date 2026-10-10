"""
Executor simulé — pas d'appel réseau réel en M0.
Remplacer par github_tools.create_issue() en Phase 3.
"""

from __future__ import annotations

import itertools
from threading import Lock

from agentic_ops.core.contracts import ActionProposal, ExecutionResult

_issue_counter = itertools.count(start=1)
_issue_counter_lock = Lock()


def execute(action: ActionProposal) -> ExecutionResult:
    if action.type.value == "create_issue":
        with _issue_counter_lock:
            n = next(_issue_counter)
        return ExecutionResult(
            status="SUCCESS",
            executor="local_simulated.create_issue",
            result_ref=f"local://issues/{n}",
            details=f"Issue simulée créée pour {action.risk_id}",
        )
    if action.type.value in ("investigate", "propose_retrain"):
        return ExecutionResult(
            status="SIMULATED",
            executor="local_simulated.noop",
            details=f"Action '{action.type.value}' simulée : aucun effet externe",
        )
    
    if action_type == "promote_model":
        return ExecutionResult(
            status="SIMULATED",
            executor="local_simulated.promote_model",
            details="Promotion du modèle simulée. Aucun artefact réellement déployé sur Kubernetes."
        )

    if action_type == "rollback":
        return ExecutionResult(
            status="SIMULATED",
            executor="local_simulated.rollback_model",
            details="Rollback simulé. Aucune modification du trafic réel."
        )
        
    return ExecutionResult(
        status="SKIPPED",
        executor="local_simulated.unsupported",
        details=f"Aucun executor implémenté pour '{action.type.value}' dans M0",
    )
