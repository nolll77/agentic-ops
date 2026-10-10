from typing import Protocol, Dict, Optional
from agentic_ops.core.contracts import (
    ModelVersion, 
    ModelRegistryStatusEnum, 
    ModelDeploymentStatusEnum
)

class ModelRegistryAdapter(Protocol):
    def register_model(self, version_id: str, metrics: Dict[str, float], schema_compatible: bool) -> ModelVersion: ...
    def get_model(self, version_id: str) -> Optional[ModelVersion]: ...
    def validate_promotion(self, version_id: str) -> bool: ...



    def _deactivate_current(self):
        if self.active_version_id and self.active_version_id in self._store:
            self._store[self.active_version_id].deployment_status = ModelDeploymentStatusEnum.DEPLOYED
            
    def promote_model(self, version_id: str) -> bool: ...
    def rollback_model(self, fallback_version_id: str) -> bool: ...


class SimulatedModelRegistry:
    def __init__(self):
        self._store: Dict[str, ModelVersion] = {}
        self.active_version_id: Optional[str] = None

    def register_model(self, version_id: str, metrics: Dict[str, float], schema_compatible: bool) -> ModelVersion:
        mv = ModelVersion(
            version_id=version_id,
            metrics=metrics,
            schema_compatible=schema_compatible
        )
        self._store[version_id] = mv
        return mv

    def get_model(self, version_id: str) -> Optional[ModelVersion]:
        return self._store.get(version_id)

    def validate_promotion(self, version_id: str) -> bool:
        mv = self.get_model(version_id)
        if not mv:
            return False
        
        # Simulated Gatekeeper Rules: F1 > 0.85, schema strictly compatible
        if mv.schema_compatible and mv.metrics.get("f1_score", 0.0) >= 0.85:
            mv.registry_status = ModelRegistryStatusEnum.VALIDATED
            return True
            
        mv.registry_status = ModelRegistryStatusEnum.REJECTED
        return False




    def _deactivate_current(self):
        if self.active_version_id and self.active_version_id in self._store:
            self._store[self.active_version_id].deployment_status = ModelDeploymentStatusEnum.DEPLOYED
            
    def promote_model(self, version_id: str) -> bool:
        mv = self.get_model(version_id)
        if not mv or mv.registry_status != ModelRegistryStatusEnum.VALIDATED:
            return False
            
        self._deactivate_current()
        mv.deployment_status = ModelDeploymentStatusEnum.ACTIVE
        self.active_version_id = version_id
        return True

    def rollback_model(self, fallback_version_id: str) -> bool:
        mv = self.get_model(fallback_version_id)
        # Fix 2: Un rollback ne peut se faire que vers une version qui a été validée
        if not mv or mv.registry_status != ModelRegistryStatusEnum.VALIDATED:
            return False
            
        self._deactivate_current()
        # Re-activate fallback version
        mv.deployment_status = ModelDeploymentStatusEnum.ACTIVE
        self.active_version_id = fallback_version_id
        return True
