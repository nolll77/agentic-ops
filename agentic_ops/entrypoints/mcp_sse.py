"""
`GET /mcp/events` — Server-Sent Events transport for the MCP gateway (Phase 1).

Wire format (one SSE stream per client, protected by the same auth middleware as `/mcp`):
  retry: 3000
  event: endpoint        data: {"sessionId": "...", "post": "/mcp", "header": "Mcp-Session-Id", ...}
  event: telemetry       data: {"uri": "mlops://telemetry/live/<channel>", "snapshot": {...}}   (id = event id)
  event: message         data: JSON-RPC (server requests such as sampling/createMessage, and
                               `notifications/resources/updated` for URIs the session subscribed to)
  : ping                 heartbeat comment, every MCP_SSE_HEARTBEAT_SECONDS (default 15)

Reconnection: send `Last-Event-ID: <n>` and every retained telemetry event with a higher id is
replayed. Without it the client first receives the latest known snapshot per channel.

Back-pressure: each client has a bounded queue with drop-oldest (see `telemetry_stream`), so a
slow reader never blocks the control plane. `data:` payloads are compact JSON on a single line,
so a snapshot value can never inject an SSE field.
"""

from __future__ import annotations

import asyncio
import json
import os
from typing import Any, AsyncIterator, Dict, Iterable, List, Optional

from fastapi import Request
from fastapi.responses import JSONResponse, Response, StreamingResponse

from agentic_ops.core.telemetry_stream import (
    CHANNELS,
    _CLOSE,
    TelemetryBroker,
    TelemetryEvent,
    TelemetryPoller,
    channel_uri,
    get_broker,
    get_poller,
)
from agentic_ops.entrypoints.mcp_transport import (
    SESSION_HEADER,
    SessionLimitReached,
    SessionRegistry,
    get_registry,
)

RETRY_MS = 3000


def heartbeat_seconds() -> float:
    try:
        return max(0.05, float(os.environ.get("MCP_SSE_HEARTBEAT_SECONDS", "15")))
    except ValueError:
        return 15.0


def format_sse(data: Any, *, event: Optional[str] = None, event_id: Optional[int] = None) -> str:
    payload = json.dumps(data, separators=(",", ":"), ensure_ascii=True)
    assert "\n" not in payload and "\r" not in payload  # json.dumps escapes them; belt and braces
    lines: List[str] = []
    if event_id is not None:
        lines.append(f"id: {int(event_id)}")
    if event is not None:
        lines.append(f"event: {event}")
    lines.append(f"data: {payload}")
    return "\n".join(lines) + "\n\n"


def _telemetry_frames(event: TelemetryEvent, subscriptions: Iterable[str]) -> List[str]:
    uri = channel_uri(event.snapshot.channel)
    frames = [
        format_sse(
            {"uri": uri, "snapshot": event.snapshot.model_dump(mode="json")},
            event="telemetry",
            event_id=event.id,
        )
    ]
    if uri in subscriptions:
        frames.append(
            format_sse(
                {"jsonrpc": "2.0", "method": "notifications/resources/updated", "params": {"uri": uri}},
                event="message",
            )
        )
    return frames


async def event_stream(
    *,
    channels: List[str],
    last_event_id: Optional[int],
    broker: Optional[TelemetryBroker] = None,
    registry: Optional[SessionRegistry] = None,
    poller: Optional[TelemetryPoller] = None,
    heartbeat: Optional[float] = None,
) -> AsyncIterator[str]:
    broker = broker if broker is not None else get_broker()
    registry = registry if registry is not None else get_registry()
    poller = poller if poller is not None else get_poller()
    heartbeat = heartbeat if heartbeat is not None else heartbeat_seconds()
    loop = asyncio.get_running_loop()

    outbox: "asyncio.Queue[Dict[str, Any]]" = asyncio.Queue(maxsize=16)
    try:
        session = registry.create(loop, outbox)
    except SessionLimitReached as exc:
        yield format_sse({"error": str(exc), "status": "SSE_SESSION_LIMIT_REACHED"}, event="error")
        return

    sub, initial = broker.subscribe(channels, last_event_id)
    tel_task: Optional["asyncio.Future[Any]"] = None
    out_task: Optional["asyncio.Future[Any]"] = None
    try:
        poller.ensure_running()
        yield f"retry: {RETRY_MS}\n\n"
        yield format_sse(
            {
                "sessionId": session.session_id,
                "post": "/mcp",
                "header": SESSION_HEADER,
                "channels": list(channels),
                "resources": [channel_uri(c) for c in channels],
            },
            event="endpoint",
        )
        for event in initial:
            for frame in _telemetry_frames(event, session.subscriptions):
                yield frame
        if sub.closed:
            return

        tel_task = asyncio.ensure_future(sub.queue.get())
        out_task = asyncio.ensure_future(outbox.get())
        while True:
            done, _ = await asyncio.wait({tel_task, out_task}, timeout=heartbeat, return_when=asyncio.FIRST_COMPLETED)
            if not done:
                yield ": ping\n\n"
                continue
            if out_task in done:
                message = out_task.result()
                out_task = asyncio.ensure_future(outbox.get())
                yield format_sse(message, event="message")
            if tel_task in done:
                item = tel_task.result()
                if item is _CLOSE:
                    return
                tel_task = asyncio.ensure_future(sub.queue.get())
                for frame in _telemetry_frames(item, session.subscriptions):
                    yield frame
    finally:
        for task in (tel_task, out_task):
            if task is not None and not task.done():
                task.cancel()
        broker.unsubscribe(sub)
        registry.remove(session.session_id)


def parse_channels(raw: Optional[str]) -> List[str]:
    if raw is None or not raw.strip():
        return list(CHANNELS)
    wanted = [c.strip() for c in raw.split(",") if c.strip()]
    unknown = [c for c in wanted if c not in CHANNELS]
    if unknown or not wanted:
        raise ValueError(f"Unknown channel(s) {unknown or raw!r}; valid channels: {', '.join(CHANNELS)}")
    return list(dict.fromkeys(wanted))


def parse_last_event_id(raw: Optional[str]) -> Optional[int]:
    if raw is None:
        return None
    try:
        value = int(raw.strip())
    except ValueError:
        return None
    return value if value >= 0 else None


async def events_response(request: Request) -> Response:
    try:
        channels = parse_channels(request.query_params.get("channels"))
    except ValueError as exc:
        return JSONResponse({"error": str(exc), "status": "INVALID_CHANNELS"}, status_code=400)

    registry = get_registry()
    if len(registry) >= registry.max_sessions:
        return JSONResponse(
            {"error": f"Too many concurrent SSE sessions (max {registry.max_sessions}).", "status": "SSE_SESSION_LIMIT_REACHED"},
            status_code=503,
            headers={"Retry-After": "5"},
        )

    stream = event_stream(
        channels=channels,
        last_event_id=parse_last_event_id(request.headers.get("last-event-id")),
    )
    return StreamingResponse(
        stream,
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"},
    )
