import hashlib
import hmac
import time
import pytest
from agentic_ops.entrypoints.slack_verify import Reject, verify_slack


def compute_signature(secret: str, body: bytes, timestamp: int) -> str:
    base = b"v0:" + str(timestamp).encode() + b":" + body
    return "v0=" + hmac.new(secret.encode(), base, hashlib.sha256).hexdigest()


def test_verify_slack_no_secret_raises_500():
    now = time.time()
    with pytest.raises(Reject) as exc:
        verify_slack(b"test body", str(int(now)), "v0=dummy", secrets=[], now=now)
    assert exc.value.status == 500
    assert "secret absent" in exc.value.why


def test_verify_slack_missing_headers_raises_401():
    now = time.time()
    secrets = ["my_test_secret"]
    with pytest.raises(Reject) as exc:
        verify_slack(b"test body", None, "v0=dummy", secrets=secrets, now=now)
    assert exc.value.status == 401
    assert "en-têtes manquants" in exc.value.why

    with pytest.raises(Reject) as exc:
        verify_slack(b"test body", str(int(now)), None, secrets=secrets, now=now)
    assert exc.value.status == 401
    assert "en-têtes manquants" in exc.value.why


def test_verify_slack_invalid_timestamp_raises_400():
    now = time.time()
    secrets = ["my_test_secret"]
    with pytest.raises(Reject) as exc:
        verify_slack(b"test body", "not_a_number", "v0=dummy", secrets=secrets, now=now)
    assert exc.value.status == 400
    assert "timestamp invalide" in exc.value.why


def test_verify_slack_expired_timestamp_raises_401():
    now = time.time()
    old_ts = int(now - 301)  # > 300s tolerance
    secrets = ["my_test_secret"]
    sig = compute_signature(secrets[0], b"test body", old_ts)
    with pytest.raises(Reject) as exc:
        verify_slack(b"test body", str(old_ts), sig, secrets=secrets, now=now)
    assert exc.value.status == 401
    assert "timestamp hors fenêtre" in exc.value.why


def test_verify_slack_tampered_signature_raises_401():
    now = time.time()
    ts = int(now)
    secrets = ["my_test_secret"]
    tampered_sig = "v0=0000000000000000000000000000000000000000000000000000000000000000"
    with pytest.raises(Reject) as exc:
        verify_slack(b"test body", str(ts), tampered_sig, secrets=secrets, now=now)
    assert exc.value.status == 401
    assert "signature invalide" in exc.value.why


def test_verify_slack_valid_signature_succeeds():
    now = time.time()
    ts = int(now)
    secrets = ["my_test_secret"]
    valid_sig = compute_signature(secrets[0], b"payload=ok", ts)
    # Should not raise
    verify_slack(b"payload=ok", str(ts), valid_sig, secrets=secrets, now=now)
