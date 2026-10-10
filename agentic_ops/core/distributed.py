import os
import logging
from redis import Redis
from redis.exceptions import ConnectionError

logger = logging.getLogger("DistributedState")

class RedisClient:
    _instance = None
    
    @classmethod
    def get_client(cls):
        if cls._instance is None:
            redis_host = os.environ.get("REDIS_HOST", "localhost")
            redis_port = int(os.environ.get("REDIS_PORT", 6379))
            environment = os.environ.get("ENVIRONMENT", "development")
            try:
                client = Redis(host=redis_host, port=redis_port, decode_responses=True, socket_connect_timeout=2)
                client.ping()
                cls._instance = client
            except ConnectionError as e:
                if environment == "production":
                    logger.error("🚨 Redis injoignable en PRODUCTION. Arrêt d'urgence (Fail-Closed).")
                    raise RuntimeError(f"Le cluster Redis (coordination d'état) est critique en production. Erreur: {e}")
                else:
                    logger.warning("⚠️ Redis injoignable, bascule sur fakeredis (MODE TEST).")
                    import fakeredis
                    cls._instance = fakeredis.FakeRedis(decode_responses=True)
        return cls._instance
