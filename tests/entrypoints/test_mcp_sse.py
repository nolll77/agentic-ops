"""Tests for Phase 1 SSE transport (`GET /mcp/events`), live telemetry resources, and 50-client fan-out."""

from __future__ import annotations

import asyncio
import json
import statistics
import time
from datetime import datetime, timezone
from types import SimpleNamespace
from typing import Any, Dict, List, Tuple

import httpx
import pytest
from prometheus_client import CollectorRegistry, Histogram
from pydantic import ValidationError

from agentic_ops.cli.main import app
from agentic_ops.core.telemetry_stream import (
    TelemetryBroker,
    TelemetryPoller,
    TelemetrySnapshot,
    collect_drift_snapshot,
    collect_latency_snapshot,
    set_broker_for_tests,
)
from agentic_ops.entrypoints.mcp_server import handle_mcp_jsonrpc
from agentic_ops.entrypoints.mcp_sse import event_stream, format_sse, parse_channels, parse_last_event_id
from agentic_ops.entrypoints.mcp_transport import (
    SESSION_HEADER,
    SessionRegistry,
    bind_channel,
    set_registry_for_tests,
)

AUTH_HEADERS = {"X-API-Key": "test-admin-key-" + "a" * 32}


def _parse_sse_block(block: str) -> Tuple[str | None, str | None, str | None]:
    """Return (event_type, event_id, data_str) for one SSE frame."""
    event_type = None
    event_id = None
    data_lines: List[str] = []
    for line in block.splitlines():
        if line.startswith(":"):
            continue
        if line.startswith("event:"):
            event_type = line.split(":", 1)[1].strip()
        elif line.startswith("id:"):
            event_id = line.split(":", 1)[1].strip()
        elif line.startswith("data:"):
            data_lines.append(line.split(":", 1)[1].strip())
    return event_type, event_id, ("\n".join(data_lines) if data_lines else None)


@pytest.fixture(autouse=True)
def _isolated_broker_and_registry():
    broker = TelemetryBroker(history=64, subscriber_queue=32)
    registry = SessionRegistry(max_sessions=100)
    set_broker_for_tests(broker)
    set_registry_for_tests(registry)
    yield broker, registry
    broker.close()


def test_telemetry_snapshot_strict_schema_forbids_extra_fields():
    snap = TelemetrySnapshot(
        channel="drift",
        source="simulated",
        scope="unit_test",
        observed_at=datetime.now(timezone.utc),
        metrics={"drift_share": 0.12},
    )
    assert snap.channel == "drift"

    with pytest.raises(ValidationError):
        TelemetrySnapshot(
            channel="drift",
            source="simulated",
            scope="unit_test",
            observed_at=datetime.now(timezone.utc),
            unexpected_extra_field="forbidden",  # type: ignore[call-arg]
        )


def test_honest_drift_and_latency_collectors_and_mcp_resources(monkeypatch):
    # 1. Default drift source is explicitly labelled "simulated"
    monkeypatch.delenv("MCP_TELEMETRY_SOURCE", raising=False)
    drift_res = handle_mcp_jsonrpc(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "resources/read",
            "params": {"uri": "mlops://telemetry/live/drift"},
        }
    )
    drift_payload = json.loads(drift_res["result"]["contents"][0]["text"])
    assert drift_payload["source"] == "simulated"
    assert "constant simulated baseline" in drift_payload["note"]
    assert drift_payload["event_id"] >= 1

    # 2. Opt-in cac_pull relays real DriftReportSnapshot without fabricating KS/Wasserstein
    monkeypatch.setenv("MCP_TELEMETRY_SOURCE", "cac_pull")
    fake_snap = SimpleNamespace(
        status="ONLINE",
        drift_report=SimpleNamespace(drift_share=0.375, drifted_columns=["col_a", "col_b", "col_c"]),
        prometheus=None,
    )
    live_snap = collect_drift_snapshot(collector_factory=lambda: SimpleNamespace(collect_all=lambda: fake_snap))
    assert live_snap.source == "cac_pull"
    assert live_snap.metrics["drift_share"] == 0.375
    assert live_snap.metrics["n_drifted_columns"] == 3.0

    # 3. Collector network error degrades gracefully into COLLECTOR_ERROR snapshot
    def _boom():
        raise RuntimeError("SOCKS5 unreachable")

    err_snap = collect_drift_snapshot(collector_factory=lambda: SimpleNamespace(collect_all=_boom))
    assert err_snap.source == "cac_pull"
    assert err_snap.labels["status"] == "COLLECTOR_ERROR"
    assert err_snap.metrics["drift_share"] is None

    # 4. Latency collector interpolates quantiles from Histogram and labels local scope honestly
    reg = CollectorRegistry()
    hist = Histogram(
        "test_llm_latency_seconds",
        "Test latency",
        buckets=(0.1, 0.5, 1.0, 2.0),
        registry=reg,
    )
    for v in (0.05, 0.2, 0.3, 0.4, 1.5):
        hist.observe(v)
    lat_snap = collect_latency_snapshot(histogram=hist)
    assert lat_snap.source == "agentic_ops_local"
    assert lat_snap.scope == "agentic_ops_llm_calls"
    assert "NOT the latency of a production model" in (lat_snap.note or "")
    assert lat_snap.metrics["llm_calls_total"] == 5.0
    assert lat_snap.metrics["llm_latency_seconds_p50_est"] is not None
    assert lat_snap.metrics["llm_latency_seconds_p95_est"] is not None

    lat_res = handle_mcp_jsonrpc(
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "resources/read",
            "params": {"uri": "mlops://telemetry/live/latency"},
        }
    )
    lat_payload = json.loads(lat_res["result"]["contents"][0]["text"])
    assert lat_payload["source"] == "agentic_ops_local"


def test_sse_helpers_prevent_injection_and_validate_params():
    frame = format_sse({"note": "line1\ndata: injected\r\n"}, event="telemetry", event_id=7)
    # Must contain strictly one `data:` line followed by blank line
    lines = [ln for ln in frame.splitlines() if ln]
    assert lines[0] == "id: 7"
    assert lines[1] == "event: telemetry"
    assert len([ln for ln in lines if ln.startswith("data:")]) == 1

    assert parse_channels(None) == ["drift", "latency"]
    assert parse_channels("drift,drift,latency") == ["drift", "latency"]
    with pytest.raises(ValueError):
        parse_channels("unknown_channel")

    assert parse_last_event_id("42") == 42
    assert parse_last_event_id("-1") is None
    assert parse_last_event_id("abc") is None


@pytest.mark.anyio
async def test_http_mcp_events_auth_and_validation_gates(monkeypatch):
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        # 1. Missing X-API-Key -> 401
        r_no_auth = await ac.get("/mcp/events")
        assert r_no_auth.status_code == 401

        # 2. Invalid X-API-Key -> 401
        r_bad_auth = await ac.get("/mcp/events", headers={"X-API-Key": "wrong-key"})
        assert r_bad_auth.status_code == 401

        # 3. Invalid channel query -> 400
        r_bad_chan = await ac.get("/mcp/events?channels=cpu", headers=AUTH_HEADERS)
        assert r_bad_chan.status_code == 400
        assert r_bad_chan.json()["status"] == "INVALID_CHANNELS"

        # 4. Session limit reached -> 503 with Retry-After
        tiny_reg = SessionRegistry(max_sessions=1)
        tiny_reg.create(asyncio.get_running_loop(), asyncio.Queue())
        set_registry_for_tests(tiny_reg)
        r_limit = await ac.get("/mcp/events", headers=AUTH_HEADERS)
        assert r_limit.status_code == 503
        assert r_limit.headers.get("retry-after") == "5"
        assert r_limit.json()["status"] == "SSE_SESSION_LIMIT_REACHED"

        # 5. Unconfigured ADMIN_API_KEY -> 503 fail-closed
        monkeypatch.delenv("ADMIN_API_KEY", raising=False)
        r_unconf = await ac.get("/mcp/events", headers=AUTH_HEADERS)
        assert r_unconf.status_code == 503


@pytest.mark.anyio
async def test_sse_stream_endpoint_heartbeat_replay_and_subscriptions():
    broker = TelemetryBroker(history=32, subscriber_queue=16)
    registry = SessionRegistry(max_sessions=10)
    # Idle poller (long interval) so we control exact published events
    poller = TelemetryPoller(broker, interval=60.0)

    # Pre-publish two events so initial connect sees latest and Last-Event-ID replays newer
    e1 = broker.publish(
        TelemetrySnapshot(
            channel="drift",
            source="simulated",
            scope="t1",
            observed_at=datetime.now(timezone.utc),
            metrics={"drift_share": 0.01},
        )
    )
    e2 = broker.publish(
        TelemetrySnapshot(
            channel="drift",
            source="simulated",
            scope="t2",
            observed_at=datetime.now(timezone.utc),
            metrics={"drift_share": 0.02},
        )
    )

    gen = event_stream(
        channels=["drift"],
        last_event_id=None,
        broker=broker,
        registry=registry,
        poller=poller,
        heartbeat=0.05,
    )
    try:
        retry_frame = await anext(gen)
        assert retry_frame == "retry: 3000\n\n"

        ep_frame = await anext(gen)
        ev_type, _, data_raw = _parse_sse_block(ep_frame)
        assert ev_type == "endpoint"
        ep_info = json.loads(data_raw or "{}")
        session_id = ep_info["sessionId"]
        assert ep_info["header"] == SESSION_HEADER

        # Initial frame without Last-Event-ID delivers latest snapshot (e2)
        init_frame = await anext(gen)
        ev_type, ev_id, _ = _parse_sse_block(init_frame)
        assert ev_type == "telemetry"
        assert int(ev_id or "0") >= e2.id

        # Heartbeat ping when idle
        while True:
            frame = await asyncio.wait_for(anext(gen), timeout=0.5)
            if frame == ": ping\n\n":
                break

        # Subscribe to drift resource via bound session channel
        session = registry.get(session_id)
        assert session is not None
        with bind_channel(session):
            init_rpc = handle_mcp_jsonrpc({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
            assert init_rpc["result"]["capabilities"]["resources"]["subscribe"] is True

            sub_rpc = handle_mcp_jsonrpc(
                {
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "resources/subscribe",
                    "params": {"uri": "mlops://telemetry/live/drift"},
                }
            )
            assert sub_rpc["result"] == {}

            # Static resource cannot be subscribed
            bad_sub = handle_mcp_jsonrpc(
                {
                    "jsonrpc": "2.0",
                    "id": 3,
                    "method": "resources/subscribe",
                    "params": {"uri": "agentic-ops://taxonomy/failure-modes"},
                }
            )
            assert "error" in bad_sub

        # Publish e3 -> expect BOTH `event: telemetry` AND `notifications/resources/updated`
        e3 = broker.publish(
            TelemetrySnapshot(
                channel="drift",
                source="simulated",
                scope="t3",
                observed_at=datetime.now(timezone.utc),
                metrics={"drift_share": 0.09},
            )
        )
        seen_telemetry = False
        seen_notification = False
        for _ in range(6):
            frame = await asyncio.wait_for(anext(gen), timeout=0.5)
            if frame == ": ping\n\n":
                continue
            ev_type, ev_id, data_raw = _parse_sse_block(frame)
            if ev_type == "telemetry" and int(ev_id or "0") == e3.id:
                seen_telemetry = True
            elif ev_type == "message" and data_raw:
                msg = json.loads(data_raw)
                if msg.get("method") == "notifications/resources/updated":
                    assert msg["params"]["uri"] == "mlops://telemetry/live/drift"
                    seen_notification = True
            if seen_telemetry and seen_notification:
                break
        assert seen_telemetry and seen_notification
    finally:
        await gen.aclose()

    # Session cleaned up on disconnect
    assert registry.get(session_id) is None

    # Reconnect with Last-Event-ID = e1.id -> replays strictly events > e1.id (including e2 and e3)
    gen_replay = event_stream(
        channels=["drift"],
        last_event_id=e1.id,
        broker=broker,
        registry=registry,
        poller=poller,
        heartbeat=1.0,
    )
    try:
        await anext(gen_replay)  # retry
        await anext(gen_replay)  # endpoint
        replayed_ids: List[int] = []
        while True:
            frame = await asyncio.wait_for(anext(gen_replay), timeout=0.5)
            ev_type, ev_id, _ = _parse_sse_block(frame)
            if ev_type == "telemetry" and ev_id is not None:
                replayed_ids.append(int(ev_id))
                if int(ev_id) >= e3.id:
                    break
        assert e1.id not in replayed_ids
        assert e2.id in replayed_ids
        assert e3.id in replayed_ids
    finally:
        await gen_replay.aclose()


def test_subscribe_without_sse_session_is_rejected_honestly():
    # Stateless initialize declares subscribe=False
    init_res = handle_mcp_jsonrpc({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
    assert init_res["result"]["capabilities"]["resources"]["subscribe"] is False

    sub_res = handle_mcp_jsonrpc(
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "resources/subscribe",
            "params": {"uri": "mlops://telemetry/live/drift"},
        }
    )
    assert "error" in sub_res
    assert "active SSE session" in sub_res["error"]["message"]


@pytest.mark.anyio
async def test_slow_consumer_drop_oldest_backpressure_never_blocks_publisher():
    broker = TelemetryBroker(history=32, subscriber_queue=4)
    sub, _ = broker.subscribe(["drift"])
    try:
        t0 = time.perf_counter()
        for idx in range(25):
            broker.publish(
                TelemetrySnapshot(
                    channel="drift",
                    source="simulated",
                    scope=f"burst-{idx}",
                    observed_at=datetime.now(timezone.utc),
                    metrics={"drift_share": float(idx)},
                )
            )
        await asyncio.sleep(0)  # let call_soon_threadsafe callbacks run
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        assert elapsed_ms < 50.0
        assert sub.queue.qsize() == 4
        assert sub.dropped == 21
        # Remaining items must be the 4 NEWEST events (22, 23, 24, 25)
        kept_ids = [sub.queue.get_nowait().id for _ in range(4)]
        assert kept_ids == [22, 23, 24, 25]
    finally:
        broker.unsubscribe(sub)


@pytest.mark.anyio
async def test_sse_50_concurrent_subscribers_latency_benchmark():
    """Roadmap Phase 1 criterion: < 15 ms fan-out latency with 50 concurrent SSE streams."""
    broker = TelemetryBroker(history=128, subscriber_queue=64)
    registry = SessionRegistry(max_sessions=100)
    poller = TelemetryPoller(broker, interval=120.0)

    n_clients = 50
    n_bursts = 5
    latencies_ms: List[float] = []
    ready = asyncio.Event()
    ready_count = 0

    async def _consumer() -> None:
        nonlocal ready_count
        gen = event_stream(
            channels=["drift"],
            last_event_id=0,
            broker=broker,
            registry=registry,
            poller=poller,
            heartbeat=5.0,
        )
        try:
            await anext(gen)  # retry
            await anext(gen)  # endpoint
            ready_count += 1
            if ready_count == n_clients:
                ready.set()
            received = 0
            while received < n_bursts:
                frame = await asyncio.wait_for(anext(gen), timeout=2.0)
                ev_type, ev_id, _ = _parse_sse_block(frame)
                if ev_type == "telemetry" and ev_id is not None:
                    ev = broker.latest("drift")
                    if ev is not None and ev.id == int(ev_id):
                        latencies_ms.append((time.perf_counter() - ev.published_perf) * 1000.0)
                        received += 1
        finally:
            await gen.aclose()

    tasks = [asyncio.create_task(_consumer()) for _ in range(n_clients)]
    await asyncio.wait_for(ready.wait(), timeout=2.0)

    for b in range(n_bursts):
        broker.publish(
            TelemetrySnapshot(
                channel="drift",
                source="simulated",
                scope=f"bench-{b}",
                observed_at=datetime.now(timezone.utc),
                metrics={"drift_share": 0.01 * b},
            )
        )
        await asyncio.sleep(0.005)

    await asyncio.gather(*tasks)
    assert len(latencies_ms) == n_clients * n_bursts

    sorted_lat = sorted(latencies_ms)
    p50 = statistics.median(sorted_lat)
    p95 = sorted_lat[int(0.95 * (len(sorted_lat) - 1))]
    max_lat = sorted_lat[-1]
    assert p95 < 15.0, f"50-subscriber SSE fan-out p95={p95:.3f}ms exceeded 15ms (p50={p50:.3f}ms, max={max_lat:.3f}ms)"
