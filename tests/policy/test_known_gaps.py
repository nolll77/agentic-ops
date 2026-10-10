import pytest
from concurrent.futures import ThreadPoolExecutor
from agentic_ops.core.policy_engine import evaluate, EvalContext
from .conftest import facts, prop, Inv

@pytest.mark.xfail(strict=True, reason="P0-6: rate limit lu depuis l'historique, pas de réservation atomique")
def test_concurrent_restarts_respect_rate_limit(bundle):
    import threading
    barrier = threading.Barrier(8)
    history = []
    def attempt(_):
        barrier.wait()
        ctx = EvalContext(facts=facts(infra=2), inventory=Inv(), recent_count=lambda *a: (time.sleep(0.01), len(history))[1])
        v = evaluate(bundle, prop("restart_pod"), ctx)
        if v.effect != "DENY": history.append(1)
        return v.effect
    with ThreadPoolExecutor(8) as ex:
        assert sum(e != "DENY" for e in ex.map(attempt, range(8))) <= 1
