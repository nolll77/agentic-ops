import os
import logging
from redis import Redis
from redis.exceptions import ConnectionError

logger = logging.getLogger("DistributedState")

# Configuration Redis (Fallback sur un FakeRedis en mémoire si non disponible pour les tests)
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))

class RedisClient:
    _instance = None
    
    @classmethod
    def get_client(cls):
        if cls._instance is None:
            try:
                # tentative de connexion réelle
                client = Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True, socket_connect_timeout=1)
                client.ping()
                cls._instance = client
            except ConnectionError:
                logger.warning("⚠️ Redis injoignable, bascule sur fakeredis (MODE TEST).")
                import fakeredis
                cls._instance = fakeredis.FakeRedis(decode_responses=True)
        return cls._instance
