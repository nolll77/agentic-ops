import json
import logging

from fastapi import FastAPI, HTTPException, Request

log = logging.getLogger(__name__)
app = FastAPI(title="Agentic-Ops Grafana webhook")
MAX_REQUEST_BYTES = 1_048_576


def parse_grafana_alerts(body: bytes) -> list[dict]:
    try:
        payload = json.loads(body)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ValueError("body must be valid JSON") from exc

    if not isinstance(payload, dict):
        raise ValueError("JSON body must be an object")
    alerts = payload.get("alerts")
    if not isinstance(alerts, list):
        raise ValueError("JSON body must contain an alerts array")
    if any(not isinstance(alert, dict) for alert in alerts):
        raise ValueError("each alert must be an object")
    return alerts


async def read_limited_body(request: Request) -> bytes:
    content_length = request.headers.get("content-length")
    if content_length is not None:
        try:
            declared_size = int(content_length)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="invalid Content-Length") from exc
        if declared_size < 0:
            raise HTTPException(status_code=400, detail="invalid Content-Length")
        if declared_size > MAX_REQUEST_BYTES:
            raise HTTPException(status_code=413, detail="request body too large")

    body = bytearray()
    async for chunk in request.stream():
        body.extend(chunk)
        if len(body) > MAX_REQUEST_BYTES:
            raise HTTPException(status_code=413, detail="request body too large")
    return bytes(body)


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/webhook/alerts", status_code=202)
async def receive_alerts(request: Request) -> dict[str, int | str]:
    body = await read_limited_body(request)
    try:
        alerts = parse_grafana_alerts(body)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    log.info("received Grafana webhook with %d alert(s)", len(alerts))
    return {"status": "received", "alerts_received": len(alerts)}
