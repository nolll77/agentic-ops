import json
import hmac
import logging
import os

from fastapi import APIRouter, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from agentic_ops.core.alert_outbox import AlertOutbox
from agentic_ops.core.alert_processing import AlertClassificationStore

log = logging.getLogger(__name__)
router = APIRouter(tags=["Grafana Webhook"])
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


def _webhook_secrets() -> tuple[str, ...]:
    return tuple(
        secret
        for secret in (
            os.environ.get("GRAFANA_WEBHOOK_SECRET", ""),
            os.environ.get("GRAFANA_WEBHOOK_SECRET_PREVIOUS", ""),
        )
        if len(secret) >= 32
    )


def _valid_webhook_token(request: Request, secrets: tuple[str, ...]) -> bool:
    authorization = request.headers.get("authorization", "")
    bearer = authorization[7:] if authorization.lower().startswith("bearer ") else ""
    candidate = request.headers.get("x-grafana-token", "") or bearer
    matches = [hmac.compare_digest(candidate, secret) for secret in secrets]
    return bool(candidate) and any(matches)


def get_outbox(request: Request) -> AlertOutbox:
    outbox = getattr(request.app.state, "alert_outbox", None)
    if outbox is None:
        path = os.environ.get("ALERT_OUTBOX_DB_PATH", "state/alerts.db")
        outbox = AlertOutbox(path)
        request.app.state.alert_outbox = outbox
    return outbox


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/webhook/alerts", status_code=202)
async def receive_alerts(request: Request) -> JSONResponse:
    secrets = _webhook_secrets()
    if not secrets:
        raise HTTPException(status_code=503, detail="Grafana webhook authentication is not configured")
    if not _valid_webhook_token(request, secrets):
        raise HTTPException(status_code=401, detail="unauthorized")

    body = await read_limited_body(request)
    try:
        alerts = parse_grafana_alerts(body)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    records, duplicates = get_outbox(request).enqueue(alerts)
    log.info(
        "persisted Grafana webhook alerts=%d duplicates=%d",
        len(records) - duplicates,
        duplicates,
    )
    return JSONResponse(
        status_code=202,
        content={
            "status": "accepted",
            "alerts_received": len(alerts),
            "accepted": len(records) - duplicates,
            "duplicates": duplicates,
            "tracking_ids": [record.tracking_id for record in records],
        },
    )


@router.get("/api/alerts/{tracking_id}")
async def alert_status(tracking_id: str, request: Request) -> dict[str, object]:
    outbox = get_outbox(request)
    record = outbox.get(tracking_id)
    if record is None:
        raise HTTPException(status_code=404, detail="alert not found")
    result: dict[str, object] = {
        "tracking_id": record.tracking_id,
        "status": record.status,
        "attempts": record.attempts,
        "created_at": record.created_at,
        "last_error": record.last_error,
    }
    classification = AlertClassificationStore(outbox.path).get(tracking_id)
    if classification is not None:
        result["triage"] = {
            "status": classification.triage_status,
            "alert_name": classification.alert_name,
            "risk_id": classification.risk_id,
            "mapping_version": classification.mapping_version,
            "classified_at": classification.classified_at,
            "episode_id": classification.episode_id,
        }
    return result


app.include_router(router)
