import hashlib, hmac

class Reject(Exception):
    def __init__(self, status: int, why: str): self.status, self.why = status, why

def verify_slack(body: bytes, ts_header: str | None, sig_header: str | None,
                 secrets: list[str], now: float, tolerance_s: int = 300) -> None:
    if not secrets:
        raise Reject(500, "secret absent")
    if not ts_header or not sig_header:
        raise Reject(401, "en-têtes manquants")
    try:
        ts = int(ts_header)
    except ValueError:
        raise Reject(400, "timestamp invalide")
    if abs(now - ts) > tolerance_s:
        raise Reject(401, "timestamp hors fenêtre")
    base = b"v0:" + ts_header.encode() + b":" + body
    ok = False
    for s in secrets:
        expected = "v0=" + hmac.new(s.encode(), base, hashlib.sha256).hexdigest()
        ok |= hmac.compare_digest(expected, sig_header)
    if not ok:
        raise Reject(401, "signature invalide")
