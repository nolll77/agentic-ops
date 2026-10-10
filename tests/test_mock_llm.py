import pytest
from unittest.mock import patch, MagicMock
from agentic_ops.core.specialist import DataSpecialist
from agentic_ops.core.contracts import Signal, Diagnosis, Finding
import datetime

@patch("agentic_ops.core.specialist.litellm.completion")
def test_data_specialist_diagnosis(mock_completion):
    # Setup mock LLM response
    mock_response = Diagnosis(
        findings=[Finding(description="Drift détecté sur la feature VMA.")],
        confidence_score=0.92
    )
    
    # We patch the instructor `client.chat.completions.create` 
    # Actually, the DataSpecialist uses `self.client.chat.completions.create`.
    # Let's mock it correctly at the class level or instance level.
    
    specialist = DataSpecialist()
    
    # Mocking instructor client
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response
    specialist.client = mock_client
    
    signal = Signal(
        signal_id="sig-123",
        source="evidently",
        observed_at=datetime.datetime.utcnow(),
        metadata={"drift_score": 0.45}
    )
    
    diagnosis = specialist.diagnose(risk_id="DATA-042", signal=signal)
    
    assert len(diagnosis.findings) == 1
    assert "VMA" in diagnosis.findings[0].description
    assert diagnosis.confidence_score == 0.92
    mock_client.chat.completions.create.assert_called_once()
