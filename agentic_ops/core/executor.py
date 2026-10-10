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


from typing import Any
from agentic_ops.core.contracts import ExecutionResult

def execute(action: ActionProposal, registry: Any = None) -> ExecutionResult:
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
    
    if action.type.value == "promote_model":
        if registry:
            success = registry.promote_model(action.parameters.get("version"))
            if not success:
                return ExecutionResult(
                    status="FAILED",
                    executor="local_simulated.promote_model",
                    details="La promotion du modèle a échoué (Registre: Refusé)."
                )
        return ExecutionResult(
            status="SIMULATED",
            executor="local_simulated.promote_model",
            details="Promotion du modèle réussie."
        )

    if action.type.value == "rollback":
        if registry:
            success = registry.rollback_model(action.parameters.get("version"))
            if not success:
                return ExecutionResult(
                    status="FAILED",
                    executor="local_simulated.rollback_model",
                    details="Le rollback du modèle a échoué (Registre: Version invalide/inconnue)."
                )
        return ExecutionResult(
            status="SIMULATED",
            executor="local_simulated.rollback_model",
            details="Rollback simulé avec succès."
        )
        
    return ExecutionResult(
        status="SKIPPED",
        executor="local_simulated.unsupported",
        details=f"Aucun executor implémenté pour '{action.type.value}' dans M0",
    )
