from agentic_ops.core.contracts import ActionProposal, ExecutionResult, ActionType
from agentic_ops.adapters.protocol import ExecutionAdapter
import logging

logger = logging.getLogger("KubernetesAdapter")

# [ALERTE MLOPS] White-List Stricte pour éviter l'Élévation de Privilèges (Audit Scenario 1)
ALLOWED_PATCH_PATHS = [
    "/spec/template/metadata/annotations/kubectl.kubernetes.io~1restartedAt",
    "/spec/replicas"
]

class KubernetesExecutionAdapter(ExecutionAdapter):
    """
    Adapter Kubernetes avec validation stricte d'admission intégrée.
    Bloque toute tentative du LLM de modifier l'identité (ServiceAccount)
    ou de monter des volumes non autorisés.
    """
    def __init__(self, kubeconfig_path: str = "~/.kube/config", context: str = "default"):
        self.kubeconfig_path = kubeconfig_path
        self.context = context

    def _validate_patch(self, action: ActionProposal):
        """
        Garantit que le LLM ne tente pas une attaque par escalade de privilèges.
        Ex: patcher `serviceAccountName: cluster-admin`.
        """
        if "patch_body" in action.parameters:
            patch = action.parameters["patch_body"]
            # Simulation d'une vérification de JSON Patch
            if isinstance(patch, list):
                for op in patch:
                    if op.get("path") not in ALLOWED_PATCH_PATHS:
                        logger.critical(f"🚨 TENTATIVE D'ÉLÉVATION DE PRIVILÈGES : Accès au path {op.get('path')} refusé.")
                        raise PermissionError(f"Le chemin K8s {op.get('path')} est strictement interdit par sécurité.")
                        
        return True

    def execute(self, action: ActionProposal) -> ExecutionResult:
        print(f"[KubernetesAdapter] Executing action {action.type.value} for risk {action.risk_id}")
        
        target_deployment = action.parameters.get("deployment_name", "fastapi-serving")
        target_namespace = action.parameters.get("namespace", "mlops-prod")
        
        try:
            self._validate_patch(action)
        except PermissionError as e:
            return ExecutionResult(
                status="FAILED",
                executor="kubernetes_adapter",
                details=str(e)
            )
        
        if action.type == ActionType.RESTART_POD:
            details = f"Redémarrage ordonné (rolling update sécurisé via annotation) pour {target_deployment} dans {target_namespace}."
        elif action.type == ActionType.SCALE_UP:
            replicas = action.parameters.get("replicas", 3)
            details = f"Mise à l'échelle de {target_deployment} à {replicas} replicas."
        elif action.type == ActionType.ROLLBACK:
            details = f"Rollback de {target_deployment} vers la version précédente."
        else:
            return ExecutionResult(
                status="FAILED",
                executor="kubernetes_adapter",
                details=f"L'action {action.type.value} n'est pas supportée par Kubernetes."
            )
            
        return ExecutionResult(
            status="SUCCESS",
            executor="kubernetes_adapter",
            result_ref=f"k8s://{target_namespace}/{target_deployment}",
            details=details
        )
