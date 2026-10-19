import pytest

from agentic_ops.entrypoints.alert_benchmark import run_benchmark


def test_alert_benchmark_reports_measured_throughput_and_latency():
    result = run_benchmark(5)

    assert result["records"] == 5
    assert result["duplicates"] == 0
    assert result["enqueue_records_per_second"] > 0
    assert result["processing_records_per_second"] > 0
    assert result["worker_latency_ms_p50"] > 0
    assert result["worker_latency_ms_p95"] > 0
    assert result["worker_latency_ms_max"] >= result["worker_latency_ms_p50"]
    assert result["recovery_lease_seconds"] == 1
    assert result["crash_to_recovered_completion_seconds"] >= 1
    assert result["database_bytes"] > 0


def test_alert_benchmark_rejects_non_positive_count():
    with pytest.raises(ValueError, match="positive"):
        run_benchmark(0)
