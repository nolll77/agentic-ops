import pytest

from agentic_ops.entrypoints.alert_benchmark import (
    run_benchmark,
    run_benchmark_matrix,
)


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


def test_alert_benchmark_matrix_measures_each_size_and_applies_local_thresholds():
    result = run_benchmark_matrix(
        [2, 5],
        min_processing_records_per_second=0.001,
        max_worker_latency_ms_p95=10_000,
    )

    assert result["passed"] is True
    assert result["thresholds"] == {
        "min_processing_records_per_second": 0.001,
        "max_worker_latency_ms_p95": 10_000,
    }
    results = result["results"]
    assert [row["records"] for row in results] == [2, 5]
    assert all(row["processing_records_per_second"] > 0 for row in results)
    assert all("processing_throughput_vs_first_pct" in row for row in results)


@pytest.mark.parametrize("counts", [[], [1, 0], [1, 1]])
def test_alert_benchmark_matrix_rejects_invalid_sizes(counts):
    with pytest.raises(ValueError):
        run_benchmark_matrix(counts)


def test_alert_benchmark_matrix_reports_failed_threshold_without_hiding_measurements():
    result = run_benchmark_matrix([2], min_processing_records_per_second=10**12)

    assert result["passed"] is False
    assert result["results"][0]["processing_records_per_second"] > 0


@pytest.mark.parametrize(
    "thresholds",
    [
        {"min_processing_records_per_second": float("nan")},
        {"max_worker_latency_ms_p95": float("inf")},
    ],
)
def test_alert_benchmark_matrix_rejects_non_finite_thresholds(thresholds):
    with pytest.raises(ValueError, match="positive"):
        run_benchmark_matrix([1], **thresholds)
