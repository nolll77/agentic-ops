import pytest
from agentic_ops.adapters.registry_adapter import SimulatedModelRegistry
from agentic_ops.core.contracts import ModelRegistryStatusEnum, ModelDeploymentStatusEnum

@pytest.fixture
def registry():
    return SimulatedModelRegistry()

def test_valid_promotion_scenario(registry):
    # Scenario A: Modèle conforme
    registry.register_model("v1.0.0", metrics={"f1_score": 0.90}, schema_compatible=True)
    
    is_valid = registry.validate_promotion("v1.0.0")
    assert is_valid is True
    
    mv = registry.get_model("v1.0.0")
    assert mv.registry_status == ModelRegistryStatusEnum.VALIDATED
    
    # Promotion autorisée
    promoted = registry.promote_model("v1.0.0")
    assert promoted is True
    assert mv.deployment_status == ModelDeploymentStatusEnum.ACTIVE
    assert registry.active_version_id == "v1.0.0"

def test_defective_model_scenario(registry):
    # Scenario B: Schéma incompatible
    registry.register_model("v1.0.1", metrics={"f1_score": 0.95}, schema_compatible=False)
    
    is_valid = registry.validate_promotion("v1.0.1")
    assert is_valid is False
    
    mv = registry.get_model("v1.0.1")
    assert mv.registry_status == ModelRegistryStatusEnum.REJECTED
    
    # Promotion bloquée
    promoted = registry.promote_model("v1.0.1")
    assert promoted is False

def test_regression_rollback_scenario(registry):
    # Scenario C: Régression après promotion
    registry.register_model("v1.0.0", metrics={"f1_score": 0.90}, schema_compatible=True)
    registry.validate_promotion("v1.0.0")
    registry.promote_model("v1.0.0")
    
    # Nouvelle version qui passe la validation et est promue
    registry.register_model("v1.1.0", metrics={"f1_score": 0.88}, schema_compatible=True)
    registry.validate_promotion("v1.1.0")
    registry.promote_model("v1.1.0")
    
    assert registry.active_version_id == "v1.1.0"
    
    # Oups, régression détectée en prod. Rollback vers la dernière version connue (v1.0.0)
    rolled_back = registry.rollback_model("v1.0.0")
    assert rolled_back is True
    assert registry.active_version_id == "v1.0.0"

    mv_fallback = registry.get_model("v1.0.0")
    assert mv_fallback.deployment_status == ModelDeploymentStatusEnum.ACTIVE

def test_invalid_rollback(registry):
    # Tentative de rollback vers une version au schéma incompatible
    registry.register_model("v0.9.0", metrics={"f1_score": 0.80}, schema_compatible=False)
    rolled_back = registry.rollback_model("v0.9.0")
    assert rolled_back is False
