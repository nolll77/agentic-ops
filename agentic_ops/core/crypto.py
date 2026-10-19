import json
import hmac
import hashlib
import os
import logging
from typing import Any, Dict

logger = logging.getLogger("TrustLedgerCrypto")

# Clé de signature (Simule un KMS externe AWS/GCP ou HMAC-SHA512 dédié)
# Supporte à la fois LEDGER_SECRET_KEY et EVIDENCE_STORE_HMAC_KEY (documenté dans .env.example)
_raw_key = os.environ.get("LEDGER_SECRET_KEY") or os.environ.get("EVIDENCE_STORE_HMAC_KEY")
if not _raw_key:
    if os.environ.get("AGENTIC_OPS_ENV") == "production" or os.environ.get("ENVIRONMENT") == "production":
        raise RuntimeError(
            "[FAIL-CLOSED] Neither LEDGER_SECRET_KEY nor EVIDENCE_STORE_HMAC_KEY is configured in production. "
            "Refusing to initialize cryptographic signer with insecure dummy key."
        )
    _raw_key = "dummy_kms_key_for_testing"

LEDGER_SECRET_KEY = _raw_key.encode("utf-8")

def get_canonical_json(data: Dict[str, Any]) -> str:
    """
    Génère une représentation canonique stricte du dictionnaire (Réponse Audit).
    Indispensable pour garantir que le hash ne change pas selon l'ordre des clés
    ou le formatage des espaces.
    """
    return json.dumps(data, sort_keys=True, separators=(',', ':'))

def sign_payload(canonical_payload: str) -> str:
    """
    Génère une signature cryptographique immuable (HMAC-SHA512).
    Un attaquant ayant accès au disque ne peut pas regénérer cette signature
    sans posséder la LEDGER_SECRET_KEY.
    """
    return hmac.new(
        LEDGER_SECRET_KEY,
        canonical_payload.encode('utf-8'),
        hashlib.sha512
    ).hexdigest()

def verify_signature(canonical_payload: str, signature: str) -> bool:
    """Vérifie l'intégrité et l'authenticité de la preuve."""
    expected = sign_payload(canonical_payload)
    return hmac.compare_digest(expected, signature)
