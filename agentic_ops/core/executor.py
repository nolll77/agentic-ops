import os
import itertools
import logging
import httpx
from threading import Lock
from typing import Any

from agentic_ops.core.contracts import ActionProposal, ExecutionResult
from agentic_ops.core.executor_gateway import live_execution_block_reason

logger = logging.getLogger("Executor")

_issue_counter = itertools.count(start=1)
_issue_counter_lock = Lock()

def is_simulation_mode() -> bool:
    if not globals().get("SIMULATION_MODE", True):
        return False
    raw = os.environ.get("SIMULATION_MODE", "true").strip().lower()
    # Fail-closed: only explicit "false", "0", "no", "off" turns simulation off
    return raw not in ("false", "0", "no", "off")

SIMULATION_MODE = True
DEMO_NAMESPACE = os.environ.get("DEMO_NAMESPACE", "demo-sandbox")

# Safeguard strict: Liste d'actions K8s autorisées (Fail-Closed)
ALLOWED_K8S_DEPLOYMENTS = frozenset({"fastapi-model-demo", "worker-demo"})

def parse_and_validate_k8s_target(target: str | None, default_namespace: str) -> tuple[str, str] | None:
    """
    Strictly parses and validates a Kubernetes target against ALLOWED_K8S_DEPLOYMENTS.
    Accepts:
      - "<deployment_name>" (e.g. "fastapi-model-demo")
      - "deployment/<deployment_name>"
      - "<namespace>/<deployment_name>"
      - "<namespace>/deployment/<deployment_name>"
    Rejects trailing slashes, empty segments, shell metacharacters, or unauthorized namespaces.
    Returns (namespace, deployment_name) if valid, else None.
    """
    if not target or not isinstance(target, str):
        return None
    clean = target.strip()
    if not clean or clean.endswith("/") or clean.startswith("/"):
        return None

    import re
    if not re.match(r"^[a-zA-Z0-9_\-\.\/]+$", clean):
        return None

    parts = [p for p in clean.split("/") if p]
    if len(parts) == 1:
        dep = parts[0]
        ns = default_namespace
    elif len(parts) == 2:
        if parts[0] == "deployment":
            ns = default_namespace
            dep = parts[1]
        else:
            ns = parts[0]
            dep = parts[1]
    elif len(parts) == 3 and parts[1] == "deployment":
        ns = parts[0]
        dep = parts[2]
    else:
        return None

    if ns != default_namespace:
        return None
    if dep not in ALLOWED_K8S_DEPLOYMENTS:
        return None
    return ns, dep

def create_real_github_issue(action: ActionProposal) -> ExecutionResult:
    blocked = live_execution_block_reason(action, is_simulation_mode())
    if blocked:
        return ExecutionResult(status="FAILED", executor="github", details=f"Exécution bloquée: {blocked}.")
    token = os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("GITHUB_REPO", "nolll77/mlops-target-infrastructure")
    
    if not token:
        return ExecutionResult(status="FAILED", executor="github", details="GITHUB_TOKEN manquant pour l'API réelle.")
        
    url = f"https://api.github.com/repos/{repo}/issues"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    payload = {
        "title": f"[Agentic-Ops] Alerte de Dérive : {action.risk_id}",
        "body": f"Action suggérée par l'agent : {action.type.value}\nCible : {action.target}",
        "labels": ["mlops-incident", "agent-created"]
    }
    
    try:
        r = httpx.post(url, headers=headers, json=payload, timeout=10.0)
        r.raise_for_status()
        issue_url = r.json().get("html_url")
        return ExecutionResult(status="SUCCESS", executor="github", result_ref=issue_url, details="Issue GitHub réelle créée.")
    except Exception as e:
        return ExecutionResult(status="FAILED", executor="github", details=f"Échec API GitHub: {e}")

def execute_real_k8s_action(action: ActionProposal) -> ExecutionResult:
    blocked = live_execution_block_reason(action, is_simulation_mode())
    if blocked:
        return ExecutionResult(status="FAILED", executor="kubernetes", details=f"Exécution bloquée: {blocked}.")
    
    validated = parse_and_validate_k8s_target(action.target, DEMO_NAMESPACE)
    if not validated:
        return ExecutionResult(
            status="FAILED",
            executor="kubernetes",
            details=f"Cible '{action.target}' invalide ou non autorisée par la Policy Executor.",
        )
    target_ns, deployment_name = validated

    try:
        from kubernetes import client, config
        # En cluster, config.load_incluster_config()
        # En local, config.load_kube_config()
        try:
            config.load_incluster_config()
        except:
            config.load_kube_config()
            
        apps_v1 = client.AppsV1Api()
            
        if action.type.value == "scale_to_zero":
            body = {"spec": {"replicas": 0}}
            apps_v1.patch_namespaced_deployment(deployment_name, target_ns, body)
            
            # Vérification (Read-After-Write)
            updated = apps_v1.read_namespaced_deployment(deployment_name, target_ns)
            if updated.spec.replicas == 0:
                return ExecutionResult(status="SUCCESS", executor="kubernetes.scale", details=f"Déploiement {deployment_name} scalé à 0 avec succès dans {target_ns}.")
            else:
                return ExecutionResult(status="FAILED", executor="kubernetes.scale", details="La vérification post-exécution a échoué (répliques > 0).")
                
        return ExecutionResult(status="SKIPPED", executor="kubernetes", details="Action K8s non supportée.")
        
    except Exception as e:
        return ExecutionResult(status="FAILED", executor="kubernetes", details=f"Erreur Kubernetes: {e}")


def execute_real_prefect_retrain(action: ActionProposal) -> ExecutionResult:
    sim_mode = is_simulation_mode() and SIMULATION_MODE
    blocked = live_execution_block_reason(action, sim_mode)
    if blocked:
        return ExecutionResult(status="FAILED", executor="prefect.retrain", details=f"Exécution bloquée: {blocked}.")
    # Récupération de l'URL cible depuis les variables de la Sandbox
    prefect_url = os.environ.get("TARGET_PREFECT_URL", "http://100.117.99.62:4200")
    # L'ID du déploiement Prefect pour le pipeline d'entraînement
    deployment_id = action.parameters.get("deployment_id", "default_train_id")
    
    url = f"{prefect_url}/api/deployments/{deployment_id}/create_flow_run"
    
    try:
        # Envoi physique de l'ordre d'écriture vers le serveur de production (via Tailscale)
        # Timeout très strict (Fail-Closed en cas de coupure réseau)
        r = httpx.post(url, json={"state": {"type": "SCHEDULED"}}, timeout=15.0)
        r.raise_for_status()
        run_id = r.json().get("id")
        return ExecutionResult(status="SUCCESS", executor="prefect.retrain", result_ref=str(run_id), details="Pipeline Prefect déclenché avec succès sur le serveur distant.")
    except Exception as e:
        return ExecutionResult(status="FAILED", executor="prefect.retrain", details=f"Échec réseau Tailscale ou API Prefect: {e}")

def execute_real_mlflow_promote(action: ActionProposal) -> ExecutionResult:
    sim_mode = is_simulation_mode() and SIMULATION_MODE
    blocked = live_execution_block_reason(action, sim_mode)
    if blocked:
        return ExecutionResult(status="FAILED", executor="mlflow.promote", details=f"Exécution bloquée: {blocked}.")
    mlflow_url = os.environ.get("TARGET_MLFLOW_URL", "http://100.117.99.62:5001")
    url = f"{mlflow_url}/api/2.0/mlflow/registered-models/alias"
    
    # Payload pour promouvoir la version X sous l'alias @Production
    payload = {
        "name": "lgbm_accidents",
        "alias": "Production",
        "version": str(action.parameters.get("version", "1"))
    }
    
    try:
        r = httpx.post(url, json=payload, timeout=10.0)
        r.raise_for_status()
        return ExecutionResult(status="SUCCESS", executor="mlflow.promote", details="Modèle officiellement promu en @Production sur MLflow.")
    except Exception as e:
        return ExecutionResult(status="FAILED", executor="mlflow.promote", details=f"Échec API MLflow: {e}")

def execute(action: ActionProposal, registry: Any = None) -> ExecutionResult:
    sim_mode = is_simulation_mode() and SIMULATION_MODE

    if action.type.value == "investigate":
        return ExecutionResult(
            status="SIMULATED",
            executor="local_simulated.investigation",
            details="Investigation enregistrée; aucune action externe exécutée.",
        )

    if not sim_mode:
        blocked = live_execution_block_reason(action, sim_mode)
        if blocked:
            return ExecutionResult(
                status="FAILED",
                executor="executor_gateway",
                details=f"Exécution physique refusée par défaut: {blocked}.",
            )

    # 1. GitHub Issue
    if action.type.value == "create_issue":
        if sim_mode:
            with _issue_counter_lock:
                n = next(_issue_counter)
            return ExecutionResult(
                status="SIMULATED",
                executor="local_simulated.create_issue",
                result_ref=f"local://issues/{n}",
                details=f"Issue simulée créée pour {action.risk_id}"
            )
        else:
            return create_real_github_issue(action)
            
    # 2. Kubernetes Scale To Zero
    if action.type.value == "scale_to_zero":
        if sim_mode:
            return ExecutionResult(status="SIMULATED", executor="local_simulated.scale", details="Scale to zero simulé.")
        else:
            return execute_real_k8s_action(action)
            
    # Actions purement simulées pour l'instant
    if action.type.value in ("investigate", "propose_retrain"):
        return ExecutionResult(
            status="SIMULATED",
            executor="local_simulated.noop",
            details=f"Action '{action.type.value}' simulée : aucun effet externe",
        )
    

    # 3. MLOps: Déclenchement de l'entraînement Prefect
    if action.type.value.upper() == "TRIGGER_RETRAINING" or action.type.value.lower() == "propose_retrain":
        if SIMULATION_MODE:
            return ExecutionResult(status="SIMULATED", executor="local_simulated.prefect", details="Trigger Prefect simulé.")
        else:
            return execute_real_prefect_retrain(action)

    # 4. MLOps: Promotion du Modèle MLflow
    if action.type.value.upper() == "PROMOTE_MODEL" or action.type.value.lower() == "promote_model":
        if SIMULATION_MODE:
            return ExecutionResult(status="SIMULATED", executor="local_simulated.mlflow", details="Promotion MLflow simulée.")
        else:
            return execute_real_mlflow_promote(action)

    if action.type.value == "promote_model":
        if registry:
            success = registry.promote_model(action.parameters.get("version"))
            if not success:
                return ExecutionResult(status="FAILED", executor="local_simulated.promote_model", details="Refus du registre.")
        return ExecutionResult(status="SIMULATED", executor="local_simulated.promote_model", details="Promotion réussie.")

    if action.type.value == "rollback":
        if SIMULATION_MODE:
            return ExecutionResult(
                status="SIMULATED",
                executor="local_simulated.rollback_model",
                details="Rollback simulé : aucun changement de registre effectué.",
            )
        if registry:
            success = registry.rollback_model(action.parameters.get("version"))
            if not success:
                return ExecutionResult(status="FAILED", executor="local_simulated.rollback_model", details="Version inconnue.")
        return ExecutionResult(status="SIMULATED", executor="local_simulated.rollback_model", details="Rollback simulé.")
        
    return ExecutionResult(
        status="SKIPPED",
        executor="local_simulated.unsupported",
        details=f"Aucun executor implémenté pour '{action.type.value}'",
    )
