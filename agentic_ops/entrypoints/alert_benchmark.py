from __future__ import annotations

import argparse
import json
import statistics
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from agentic_ops.core.alert_outbox import AlertIngestionWorker, AlertOutbox


def _percentile(values: list[float], percentile: float) -> float:
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, int((len(ordered) - 1) * percentile)))
    return ordered[index]


def run_benchmark(count: int) -> dict[str, float | int | str]:
    if count < 1:
        raise ValueError("count must be positive")
    with tempfile.TemporaryDirectory(prefix="agentic-ops-alert-benchmark-") as directory:
        database = Path(directory) / "alerts.sqlite3"
        outbox = AlertOutbox(str(database), dedup_window_seconds=1)
        alerts = [
            {
                "status": "firing",
                "labels": {"alertname": "Benchmark", "sequence": str(index)},
                "startsAt": f"benchmark-{index}",
            }
            for index in range(count)
        ]
        enqueue_started = time.perf_counter()
        records, duplicates = outbox.enqueue(alerts)
        enqueue_elapsed = time.perf_counter() - enqueue_started
        if duplicates or len(records) != count:
            raise RuntimeError(
                f"benchmark setup accepted {len(records)} records and found {duplicates} duplicates"
            )

        latencies_ms: list[float] = []
        worker = AlertIngestionWorker(outbox, "benchmark-worker", lambda alert: None)
        processing_started = time.perf_counter()
        for _ in range(count):
            started = time.perf_counter()
            if not worker.run_once():
                raise RuntimeError("benchmark worker stopped before draining the queue")
            latencies_ms.append((time.perf_counter() - started) * 1000)
        processing_elapsed = time.perf_counter() - processing_started
        if worker.run_once():
            raise RuntimeError("benchmark worker found unexpected extra queue work")

        recovery_record, _ = outbox.enqueue(
            [
                {
                    "status": "firing",
                    "labels": {"alertname": "RecoveryProbe"},
                    "startsAt": f"recovery-{time.time_ns()}",
                }
            ]
        )
        lease_seconds = 1
        crash_code = """
import os
import sys
from agentic_ops.core.alert_outbox import AlertOutbox
record = AlertOutbox(sys.argv[1]).claim("benchmark-crashed-worker", lease_seconds=1)
assert record is not None
os._exit(23)
"""
        recovery_started = time.perf_counter()
        crashed = subprocess.run(
            [sys.executable, "-c", crash_code, str(database)],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        if crashed.returncode != 23:
            raise RuntimeError(
                f"recovery probe process exited unexpectedly: {crashed.returncode}"
            )
        time.sleep(lease_seconds + 0.05)
        recovery_worker = AlertIngestionWorker(
            outbox,
            "benchmark-recovery-worker",
            lambda alert: None,
            lease_seconds=lease_seconds,
        )
        if not recovery_worker.run_once():
            raise RuntimeError("recovery worker did not reclaim the expired lease")
        recovery_elapsed = time.perf_counter() - recovery_started
        recovered = outbox.get(recovery_record[0].tracking_id)
        if recovered is None or recovered.status != "COMPLETED" or recovered.attempts != 2:
            raise RuntimeError("recovery probe did not complete exactly one reclaimed alert")

        return {
            "records": count,
            "duplicates": duplicates,
            "enqueue_seconds": round(enqueue_elapsed, 6),
            "enqueue_records_per_second": round(count / enqueue_elapsed, 2),
            "processing_seconds": round(processing_elapsed, 6),
            "processing_records_per_second": round(count / processing_elapsed, 2),
            "worker_latency_ms_p50": round(statistics.median(latencies_ms), 3),
            "worker_latency_ms_p95": round(_percentile(latencies_ms, 0.95), 3),
            "worker_latency_ms_max": round(max(latencies_ms), 3),
            "recovery_lease_seconds": lease_seconds,
            "crash_to_recovered_completion_seconds": round(recovery_elapsed, 3),
            "database_bytes": database.stat().st_size,
        }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Measure local SQLite alert-outbox throughput and worker latency."
    )
    parser.add_argument("--count", type=int, default=500, help="unique alerts to enqueue (default: 500)")
    args = parser.parse_args(argv)
    if args.count < 1:
        parser.error("--count must be positive")
    print(json.dumps(run_benchmark(args.count), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
