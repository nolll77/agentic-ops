import hashlib
import logging
from agentic_ops.core.distributed import RedisClient

logger = logging.getLogger("Idempotency")

def compute_semantic_fingerprint(tenant: str, environment: str, service: str, risk_id: str) -> str:
    """
    Calcule une empreinte sémantique de l'incident. 
    (Réponse Audit: La clé doit être métier, pas seulement technique).
    """
    base = f"{tenant}:{environment}:{service}:{risk_id}"
    return hashlib.sha256(base.encode()).hexdigest()

def acquire_idempotency_lock(fingerprint: str, ttl_seconds: int = 3600) -> bool:
    """
    Tente d'acquérir un verrou distribué atomique sur Redis (SET NX).
    Si False, l'incident est déjà en cours de traitement par un autre réplica (ou récemment traité).
    """
    redis = RedisClient.get_client()
    lock_key = f"lock:incident:{fingerprint}"
    
    # SET NX (Not eXists) EX (Expire)
    acquired = redis.set(lock_key, "LOCKED", nx=True, ex=ttl_seconds)
    if not acquired:
        logger.warning(f"🔒 [IDEMPOTENCE] Verrou impossible à obtenir pour {fingerprint[:8]} (Doublon ou en cours)")
        return False
    return True
