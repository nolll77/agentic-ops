"""
Live telemetry fan-out for the MCP gateway (Phase 1 of the MCP roadmap).

Design goals (and honest limits):
  * Non-blocking: publishers never wait on subscribers. Each subscriber owns a bounded
    queue with a *drop-oldest* policy, so a slow SSE client can never stall the control plane.
  * Thread-safe publish: collectors run in worker threads (network I/O), subscribers live on
    the asyncio event loop. Delivery is marshalled with `loop.call_soon_threadsafe`.
  * In-process only: state lives in this Python process. With several uvicorn workers each
    worker has its own broker; this is a single-worker design.
  * No fabricated data. Every snapshot is labelled with its `source`. When no live source is
    configured the drift channel emits an explicit `simulated` baseline, never fake "live" drift.
  * What is really measured: the `latency` channel reports the latency of Agentic-Ops' OWN LLM
    calls (Prometheus histogram `agentic_ops_llm_latency_seconds`), NOT the P95/P99 of a
    production model under observation. The `drift` channel relays `drift_share` /
    drifted-column counts from the Evidently report exposed by `CacPullCollector`; it does not
    compute Wasserstein / Kolmogorov-Smirnov distances itself.
"""

from __future__ import annotations

import asyncio
import collections
import logging
import os
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Deque, Dict, Iterable, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

log = logging.getLogger(__name__)

CHANNELS = ("drift", "latency")
TELEMETRY_URI_PREFIX = "mlops://telemetry/live/"


def channel_uri(channel: str) -> str:
    return f"{TELEMETRY_URI_PREFIX}{channel}"


def uri_channel(uri: str) -> Optional[str]:
    if uri.startswith(TELEMETRY_URI_PREFIX):
        name = uri[len(TELEMETRY_URI_PREFIX):]
        if name in CHANNELS:
            return name
    return None


class TelemetrySnapshot(BaseModel):
    """Strict schema for every telemetry event (roadmap criterion: no schema drift)."""

    model_config = ConfigDict(extra="forbid")

    channel: Literal["drift", "latency"]
    source: Literal["cac_pull", "agentic_ops_local", "simulated"]
    scope: str
    observed_at: datetime
    metrics: Dict[str, Optional[float]] = Field(default_factory=dict)
    labels: Dict[str, str] = Field(default_factory=dict)
    note: Optional[str] = None


@dataclass(frozen=True)
class TelemetryEvent:
    id: int
    snapshot: TelemetrySnapshot
    published_perf: float = field(default_factory=time.perf_counter)


_CLOSE = object()


class Subscriber:
    """One consumer. `offer` runs on the consumer's own event loop thread."""

    def __init__(self, channels: Iterable[str], loop: asyncio.AbstractEventLoop, maxsize: int):
        self.channels = frozenset(channels)
        self.loop = loop
        self.queue: "asyncio.Queue[Any]" = asyncio.Queue(maxsize=maxsize)
        self.dropped = 0
        self.closed = False

    def _make_room(self) -> None:
        if self.queue.full():
            try:
                self.queue.get_nowait()
                self.dropped += 1
            except asyncio.QueueEmpty:  # pragma: no cover - race-free on a single loop thread
                pass

    def offer(self, event: Any) -> None:
        if self.closed and event is not _CLOSE:
            return
        self._make_room()
        self.queue.put_nowait(event)

    def close(self) -> None:
        self.closed = True
        self._make_room()
        self.queue.put_nowait(_CLOSE)


class TelemetryBroker:
    def __init__(self, history: int = 256, subscriber_queue: int = 64):
        self._lock = threading.Lock()
        self._subs: List[Subscriber] = []
        self._history: Deque[TelemetryEvent] = collections.deque(maxlen=history)
        self._latest: Dict[str, TelemetryEvent] = {}
        self._next_id = 0
        self._subscriber_queue = subscriber_queue
        self._closed = False

    # ---- producer side (any thread) -------------------------------------------------
    def publish(self, snapshot: TelemetrySnapshot) -> TelemetryEvent:
        with self._lock:
            self._next_id += 1
            event = TelemetryEvent(id=self._next_id, snapshot=snapshot)
            self._history.append(event)
            self._latest[snapshot.channel] = event
            targets = [s for s in self._subs if snapshot.channel in s.channels]
        for sub in targets:
            self._deliver(sub, event)
        return event

    def _deliver(self, sub: Subscriber, event: Any) -> None:
        try:
            sub.loop.call_soon_threadsafe(sub.offer, event)
        except RuntimeError:  # consumer loop already closed: forget it
            with self._lock:
                if sub in self._subs:
                    self._subs.remove(sub)

    # ---- consumer side ---------------------------------------------------------------
    def subscribe(
        self,
        channels: Iterable[str],
        last_event_id: Optional[int] = None,
    ) -> "tuple[Subscriber, List[TelemetryEvent]]":
        """Register a consumer and return (subscriber, initial events).

        Initial events are taken atomically with registration, so nothing can be missed or
        duplicated between the replay and the live feed. Without `last_event_id` the consumer
        receives the latest known snapshot per channel; with it, every retained newer event.
        """
        wanted = [c for c in channels if c in CHANNELS]
        loop = asyncio.get_running_loop()
        sub = Subscriber(wanted, loop, self._subscriber_queue)
        with self._lock:
            if self._closed:
                sub.closed = True
                return sub, []
            if last_event_id is None:
                initial = sorted(
                    (e for c, e in self._latest.items() if c in sub.channels), key=lambda e: e.id
                )
            else:
                initial = [
                    e for e in self._history if e.id > last_event_id and e.snapshot.channel in sub.channels
                ]
            self._subs.append(sub)
        return sub, initial

    def unsubscribe(self, sub: Subscriber) -> None:
        with self._lock:
            if sub in self._subs:
                self._subs.remove(sub)

    @property
    def subscriber_count(self) -> int:
        with self._lock:
            return len(self._subs)

    def latest(self, channel: str) -> Optional[TelemetryEvent]:
        with self._lock:
            return self._latest.get(channel)

    @property
    def closed(self) -> bool:
        return self._closed

    def close(self) -> None:
        """Terminate every subscription (their generators end cleanly)."""
        with self._lock:
            self._closed = True
            targets = list(self._subs)
            self._subs.clear()
        for sub in targets:
            self._deliver(sub, _CLOSE)


# ---------------------------------------------------------------------------------------
# Snapshot collectors (blocking: call them from a worker thread, never the event loop)
# ---------------------------------------------------------------------------------------


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _histogram_quantile(buckets: List["tuple[float, float]"], q: float) -> Optional[float]:
    """Prometheus-style quantile estimate by linear interpolation inside the bucket."""
    if not buckets:
        return None
    total = buckets[-1][1]
    if total <= 0:
        return None
    rank = q * total
    prev_bound, prev_count = 0.0, 0.0
    for bound, cumulative in buckets:
        if cumulative >= rank:
            if bound == float("inf"):
                return prev_bound  # open-ended bucket: best honest lower bound
            span = cumulative - prev_count
            if span <= 0:
                return bound
            return prev_bound + (bound - prev_bound) * ((rank - prev_count) / span)
        prev_bound, prev_count = bound, cumulative
    return prev_bound


def collect_latency_snapshot(histogram: Any = None) -> TelemetrySnapshot:
    """Latency of Agentic-Ops' own LLM calls, aggregated over every label set."""
    if histogram is None:
        from agentic_ops.adapters.llm_protocol import LLM_LATENCY

        histogram = LLM_LATENCY
    per_bound: Dict[float, float] = collections.defaultdict(float)
    count = 0.0
    total = 0.0
    for metric in histogram.collect():
        for sample in metric.samples:
            if sample.name.endswith("_bucket"):
                per_bound[float(sample.labels["le"])] += sample.value
            elif sample.name.endswith("_count"):
                count += sample.value
            elif sample.name.endswith("_sum"):
                total += sample.value
    buckets = sorted(per_bound.items())
    metrics: Dict[str, Optional[float]] = {
        "llm_calls_total": count,
        "llm_latency_seconds_sum": total,
        "llm_latency_seconds_mean": (total / count) if count else None,
        "llm_latency_seconds_p50_est": _histogram_quantile(buckets, 0.50),
        "llm_latency_seconds_p95_est": _histogram_quantile(buckets, 0.95),
        "llm_latency_seconds_p99_est": _histogram_quantile(buckets, 0.99),
    }
    return TelemetrySnapshot(
        channel="latency",
        source="agentic_ops_local",
        scope="agentic_ops_llm_calls",
        observed_at=_now(),
        metrics=metrics,
        labels={"estimation": "histogram_bucket_interpolation"},
        note=(
            "Latency of Agentic-Ops' own LLM calls, NOT the latency of a production model "
            "under observation."
        ),
    )


def _simulated_drift() -> TelemetrySnapshot:
    return TelemetrySnapshot(
        channel="drift",
        source="simulated",
        scope="simulated_baseline",
        observed_at=_now(),
        metrics={"drift_share": 0.0, "n_drifted_columns": 0.0},
        note=(
            "No live drift source is configured (MCP_TELEMETRY_SOURCE != 'cac_pull'). "
            "This is a constant simulated baseline, not a measurement."
        ),
    )


def collect_drift_snapshot(collector_factory: Optional[Callable[[], Any]] = None) -> TelemetrySnapshot:
    """Relay the Evidently drift report from the target platform, or a labelled baseline.

    The remote pull is strictly opt-in (`MCP_TELEMETRY_SOURCE=cac_pull`); by default nothing
    leaves the process.
    """
    if os.environ.get("MCP_TELEMETRY_SOURCE", "simulated").strip().lower() != "cac_pull":
        return _simulated_drift()
    try:
        if collector_factory is None:
            from agentic_ops.adapters.cac_pull_collector import CacPullCollector
            from agentic_ops.cli.main import _is_port_open

            use_proxy = _is_port_open("127.0.0.1", 1055)
            collector = CacPullCollector(use_proxy_for_vps=use_proxy, timeout=3.5)
        else:
            collector = collector_factory()
        snap = collector.collect_all()
    except Exception as exc:  # network/proxy failure must never kill the poller
        log.warning("drift collection failed: %s", exc)
        return TelemetrySnapshot(
            channel="drift",
            source="cac_pull",
            scope="remote_evidently_report",
            observed_at=_now(),
            metrics={"drift_share": None, "n_drifted_columns": None},
            labels={"status": "COLLECTOR_ERROR"},
            note=f"{type(exc).__name__}: {exc}"[:300],
        )
    report = getattr(snap, "drift_report", None)
    prom = getattr(snap, "prometheus", None)
    drift_share = getattr(report, "drift_share", None)
    if drift_share is None:
        drift_share = getattr(prom, "drift_share", None)
    n_cols = float(len(report.drifted_columns)) if report is not None else None
    return TelemetrySnapshot(
        channel="drift",
        source="cac_pull",
        scope="remote_evidently_report",
        observed_at=_now(),
        metrics={"drift_share": drift_share, "n_drifted_columns": n_cols},
        labels={"status": str(getattr(getattr(snap, "status", ""), "value", getattr(snap, "status", "")))},
        note=None if drift_share is not None else "Remote target reachable but exposed no drift_share.",
    )


COLLECTORS: Dict[str, Callable[[], TelemetrySnapshot]] = {
    "drift": collect_drift_snapshot,
    "latency": collect_latency_snapshot,
}


# ---------------------------------------------------------------------------------------
# Poller: runs only while somebody is listening
# ---------------------------------------------------------------------------------------


def poll_interval_seconds() -> float:
    try:
        return max(1.0, float(os.environ.get("MCP_TELEMETRY_INTERVAL_SECONDS", "15")))
    except ValueError:
        return 15.0


class TelemetryPoller:
    def __init__(self, broker: TelemetryBroker, interval: Optional[float] = None):
        self.broker = broker
        self.interval = interval
        self._task: Optional["asyncio.Task[None]"] = None

    @property
    def running(self) -> bool:
        return self._task is not None and not self._task.done()

    def ensure_running(self) -> None:
        if not self.running:
            self._task = asyncio.get_running_loop().create_task(self._run())

    async def poll_once(self) -> None:
        for channel, collect in COLLECTORS.items():
            if self.broker.closed:
                return
            try:
                # Blocking I/O (HTTP via Tailscale, Prometheus registry walk) stays off the loop.
                snapshot = await asyncio.to_thread(collect)
            except Exception:  # pragma: no cover - collectors already guard themselves
                log.exception("telemetry collector %s crashed", channel)
                continue
            self.broker.publish(snapshot)

    async def _run(self) -> None:
        try:
            while not self.broker.closed:
                await self.poll_once()
                await asyncio.sleep(self.interval if self.interval is not None else poll_interval_seconds())
                if self.broker.subscriber_count == 0:
                    return  # nobody listening: stop polling remote targets
        except asyncio.CancelledError:  # pragma: no cover
            raise


_broker = TelemetryBroker()
_poller = TelemetryPoller(_broker)


def get_broker() -> TelemetryBroker:
    return _broker


def get_poller() -> TelemetryPoller:
    return _poller


def set_broker_for_tests(broker: TelemetryBroker) -> None:
    global _broker, _poller
    _broker = broker
    _poller = TelemetryPoller(broker)


def read_channel_snapshot(channel: str) -> Dict[str, Any]:
    """Latest cached snapshot for `resources/read`, or one on-demand collection."""
    event = get_broker().latest(channel)
    if event is None:
        snapshot = COLLECTORS[channel]()
        event = get_broker().publish(snapshot)
    payload = event.snapshot.model_dump(mode="json")
    payload["event_id"] = event.id
    payload["age_seconds"] = round(max(0.0, (_now() - event.snapshot.observed_at).total_seconds()), 3)
    return payload
