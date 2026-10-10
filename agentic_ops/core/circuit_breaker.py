import logging
from datetime import datetime, timedelta

logger = logging.getLogger("CircuitBreaker")

class LLMCircuitBreaker:
    """
    FinOps/SecOps Circuit Breaker pour le Control Plane.
    Coupe les appels LLM si une limite de requêtes ou de budget est atteinte 
    sur une fenêtre glissante.
    """
    def __init__(self, max_calls_per_hour: int = 100):
        self.max_calls_per_hour = max_calls_per_hour
        self.call_timestamps = []
        self._tripped = False

    def record_call(self):
        now = datetime.utcnow()
        self.call_timestamps.append(now)
        self._cleanup(now)
        
        if len(self.call_timestamps) > self.max_calls_per_hour:
            if not self._tripped:
                logger.critical(f"🔥 [CIRCUIT BREAKER TRIPPED] Limite de {self.max_calls_per_hour} appels LLM/h dépassée. Mode dégradé activé (FinOps/SecOps).")
                self._tripped = True
                
    def is_tripped(self) -> bool:
        self._cleanup(datetime.utcnow())
        if self._tripped and len(self.call_timestamps) <= self.max_calls_per_hour:
            logger.info("🟢 [CIRCUIT BREAKER RESET] Le budget horaire est de nouveau sain. Reprise des appels LLM.")
            self._tripped = False
        return self._tripped
        
    def _cleanup(self, now: datetime):
        cutoff = now - timedelta(hours=1)
        self.call_timestamps = [t for t in self.call_timestamps if t > cutoff]

# Singleton pour l'orchestrateur
global_circuit_breaker = LLMCircuitBreaker(max_calls_per_hour=50)
