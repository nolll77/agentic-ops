from pathlib import Path

import yaml


def test_risk_register_loads():
    # Verify the risk register parses as valid YAML
    base_dir = Path(__file__).parent.parent
    risk_file = base_dir / "agentic_ops" / "governance" / "risk_register.yaml"
    
    assert risk_file.exists(), "Risk register file is missing!"
    
    with open(risk_file, "r") as f:
        risks = yaml.safe_load(f)
        
    assert isinstance(risks, list), "Risks should be a list"
    assert len(risks) > 0, "Risk register should not be empty"
    
    # Check structure of first risk
    first_risk = risks[0]
    assert "id" in first_risk
    assert "severity" in first_risk
