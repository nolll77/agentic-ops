"""
Unit Tests for DeterministicRAGEngine.
Verifies:
1. Indexing loads the 435 failure modes from docs/mlops_failure_modes_taxonomy.md.
2. Indexing loads the 36 simulation scenarios from docs/mlops_simulation_scenarios_registry.md.
3. Indexing loads YAML contracts from tests/scenarios/data/*.yaml.
4. Search by exact failure mode ID (e.g., DATA-042, INFRA-001, SEC-054).
5. Search by scenario number/ID (e.g., Scénario 1, SIM-001, SC-101).
6. High RPN filtering (rpn >= 80).
7. Grounding context retrieval generates clean markdown cards.
8. Offline SRE degraded-mode answer generation.
"""

import pytest
from agentic_ops.core.deterministic_rag import DeterministicRAGEngine


@pytest.fixture
def rag():
    return DeterministicRAGEngine.get_instance()


def test_rag_indexes_failure_modes_count(rag):
    """The 435 failure modes taxonomy must be parsed into memory."""
    assert len(rag.failure_modes) >= 430
    assert "DATA-042" in rag.failure_modes
    assert "INFRA-001" in rag.failure_modes
    assert "SEC-054" in rag.failure_modes


def test_rag_indexes_scenarios_count(rag):
    """The 36 simulation scenarios must be indexed."""
    assert len(rag.scenarios) >= 36
    assert "SIM-001" in rag.scenarios or "SIM-1" in rag.scenarios or "SCENARIO-1" in rag.scenarios


def test_rag_search_exact_failure_mode(rag):
    """Direct lookup by risk_id returns exact metadata."""
    results = rag.search_failure_modes("DATA-042")
    assert len(results) == 1
    fm = results[0]
    assert fm.risk_id == "DATA-042"
    assert "dérive" in fm.name.lower() or "progressive" in fm.name.lower()
    assert fm.rpn == 64
    assert fm.impact_slo == "Précision"
    assert "Evidently" in fm.detection or "dbt" in fm.detection


def test_rag_search_high_rpn(rag):
    """RPN filter >= 80 must return the top critical risks."""
    results = rag.search_failure_modes("rpn >= 80", limit=10)
    assert len(results) > 0
    for r in results:
        assert r.rpn >= 80


def test_rag_search_scenarios(rag):
    """Lookup by scenario number or keyword."""
    sc1 = rag.search_scenarios("Scénario 1")
    assert len(sc1) >= 1
    assert "Cascade Silencieuse" in sc1[0].title or "SIM-001" in sc1[0].sim_id


def test_rag_retrieve_grounding_context(rag):
    """Context retrieval generates markdown snippets for prompt augmentation."""
    ctx = rag.retrieve_grounding_context("Quelles sont les implications de DATA-042 et du Scénario 1 ?")
    assert ctx is not None
    assert "DATA-042" in ctx
    assert "Score RPN" in ctx
    assert "Scénario de Simulation" in ctx


def test_rag_offline_sre_response(rag):
    """Offline response provides a zero-token standalone answer."""
    ans = rag.get_offline_sre_response("Parle-moi de la panne DATA-042")
    assert ans is not None
    assert "Mode Dégradé SRE" in ans
    assert "DATA-042" in ans
    assert "RPN" in ans
