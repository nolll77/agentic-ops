import hashlib

def compute_dedup_key(risk_id: str, signal_source: str, environment: str, detection_window: str) -> str:
    """Calcul de clé d'idempotence stricte (SHA-256) pour éviter le traitement en double."""
    canonical_string = f"{risk_id}|{signal_source}|{environment}|{detection_window}"
    return hashlib.sha256(canonical_string.encode('utf-8')).hexdigest()
