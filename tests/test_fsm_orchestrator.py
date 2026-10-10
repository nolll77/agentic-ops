import pytest
from agentic_ops.core.state import StateMachine

def test_state_machine_valid_transitions():
    sm = StateMachine()
    assert sm.current == "DETECTED"
    
    sm.transition("INVESTIGATING")
    assert sm.current == "INVESTIGATING"
    
    sm.transition("DIAGNOSED")
    assert sm.current == "DIAGNOSED"
    
    sm.transition("PLANNED")
    assert sm.current == "PLANNED"
    
    assert sm.trace == ["DETECTED", "INVESTIGATING", "DIAGNOSED", "PLANNED"]

def test_state_machine_invalid_transition():
    sm = StateMachine()
    with pytest.raises(ValueError):
        sm.transition("INVALID_STATE")
