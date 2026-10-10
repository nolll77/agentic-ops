import hashlib
import logging
import uuid
from agentic_ops.core.distributed import RedisClient

logger = logging.getLogger("Idempotency")

def compute_semantic_fingerprint(tenant: str, environment: str, service: str, risk_id: str) -> str:
    base = f"{tenant}:{environment}:{service}:{risk_id}"
    return hashlib.sha256(base.encode()).hexdigest()

def acquire_idempotency_lock(fingerprint: str, ttl_seconds: int = 3600) -> str:
    redis = RedisClient.get_client()
    lock_key = f"lock:incident:{fingerprint}"
    owner_id = str(uuid.uuid4())
    
    acquired = redis.set(lock_key, owner_id, nx=True, ex=ttl_seconds)
    if not acquired:
        logger.warning(f"🔒 [IDEMPOTENCE] Verrou impossible à obtenir pour {fingerprint[:8]} (Doublon ou en cours)")
        return ""
    return owner_id

def release_idempotency_lock(fingerprint: str, owner_id: str) -> bool:
    if not owner_id:
        return False
        
    redis = RedisClient.get_client()
    lock_key = f"lock:incident:{fingerprint}"
    
    lua_script = """
    if redis.call("get", KEYS[1]) == ARGV[1] then
        return redis.call("del", KEYS[1])
    else
        return 0
    end
    """
    
    try:
        result = redis.eval(lua_script, 1, lock_key, owner_id)
        if result:
            logger.info(f"🔓 [IDEMPOTENCE] Verrou libéré pour {fingerprint[:8]}")
            return True
        else:
            logger.warning(f"⚠️ [IDEMPOTENCE] Impossible de libérer le verrou pour {fingerprint[:8]} (Expiré ou volé)")
            return False
    except Exception:
        # Fallback for fakeredis tests which might not support eval properly
        if redis.get(lock_key) == owner_id:
            redis.delete(lock_key)
            logger.info(f"🔓 [IDEMPOTENCE] Verrou libéré pour {fingerprint[:8]} (Fallback Test)")
            return True
        return False
