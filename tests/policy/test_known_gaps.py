from concurrent.futures import ThreadPoolExecutor
from agentic_ops.core.policy_engine import evaluate, EvalContext
from agentic_ops.core.atomic_quota import AtomicQuotaManager
from .conftest import facts, prop, Inv

def test_concurrent_restarts_respect_rate_limit(bundle, tmp_path):
    import threading
    barrier = threading.Barrier(8)
    manager = AtomicQuotaManager(str(tmp_path / "quotas.db"))
    def attempt(_):
        barrier.wait()
        ctx = EvalContext(
            facts=facts(infra=2),
            inventory=Inv(),
            recent_count=lambda *a: 0,
            reserve_quota=manager.reserve,
            reservation_key=f"attempt-{threading.get_ident()}",
        )
        v = evaluate(bundle, prop("restart_pod"), ctx)
        return v.effect
    with ThreadPoolExecutor(8) as ex:
        assert sum(e != "DENY" for e in ex.map(attempt, range(8))) == 1
