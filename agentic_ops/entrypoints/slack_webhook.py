import json, logging
from urllib.parse import parse_qs
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from agentic_ops.core.approvals import Result
from .slack_verify import Reject, verify_slack

log = logging.getLogger("slack_webhook")
router = APIRouter()

_HTTP = {Result.RECORDED: (200, "approbation enregistrée"), Result.CLAIMED: (200, "quorum atteint, exécution durablement mise en file"),
         Result.DENIED: (200, "refusé"), Result.DUPLICATE: (200, "déjà compté"),
         Result.EXPIRED: (410, "demande expirée"), Result.HASH_MISMATCH: (409, "action différente de celle demandée"),
         Result.DIVERGED: (409, "l'épisode a changé depuis la demande"), Result.CLOSED: (409, "demande déjà clôturée"),
         Result.UNKNOWN: (404, "demande inconnue"), Result.SELF_APPROVAL: (403, "auto-approbation interdite"),
         Result.UNAUTHORIZED: (403, "rôle non autorisé"),
         Result.INVALID_DECISION: (400, "décision invalide")}

def get_deps(request: Request):
    return request.app.state.hitl

@router.post("/slack/interactive")
async def interactive(request: Request, d=Depends(get_deps)):
    body = await request.body()
    try:
        verify_slack(body, request.headers.get("X-Slack-Request-Timestamp"),
                     request.headers.get("X-Slack-Signature"), d.secrets, d.clock())
    except Reject as r:
        log.warning("slack reject: %s", r.why)
        return JSONResponse({"error": r.why}, status_code=r.status)

    if not d.repo.register_signature(request.headers.get("X-Slack-Signature", "")):
        return JSONResponse({"status": "duplicate_ignored"}, status_code=200)

    try:
        payload = json.loads(parse_qs(body.decode())["payload"][0])
        user = payload["user"]["id"]
        act = payload["actions"][0]
        episode_id, claimed_hash = act["value"].split(":", 1)
        decision = {"approve": "approve", "deny": "deny"}[act["action_id"]]
    except (KeyError, IndexError, ValueError, json.JSONDecodeError):
        return JSONResponse({"error": "payload invalide"}, status_code=400)

    ep = d.orchestrator.load_episode(episode_id)
    if ep is None:
        return JSONResponse({"error": "demande inconnue"}, status_code=404)
    level = d.policy.level_of(ep)
    group = d.approvers.group_of(user, level)
    if group is None:
        log.warning("approbateur non autorisé: %s (épisode %s)", user, episode_id)
        return JSONResponse({"error": "non autorisé"}, status_code=403)
    result, _ = d.repo.decide(episode_id, user, group, decision, claimed_hash,
                              current_hash=d.orchestrator.current_proposal_hash(ep),
                              eligible_group_for=lambda approver: d.approvers.group_of(approver, level))
    code, msg = _HTTP.get(result, (500, "erreur inconnue"))
    if result is Result.CLAIMED:
        log.info("approval %s reached quorum; execution claim persisted in outbox", episode_id)
    log.info("approval %s user=%s result=%s", episode_id, user, result.value)
    return JSONResponse({"status": msg}, status_code=code)
