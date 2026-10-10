import multiprocessing
import logging
from typing import Any
import time

from pydantic import BaseModel

logger = logging.getLogger("AgenticSecurity")

class SecurityException(Exception):
    pass

def _worker_wrapper(queue: multiprocessing.Queue, func, kwargs):
    try:
        result = func(**kwargs)
        queue.put(("SUCCESS", result))
    except Exception as e:
        queue.put(("ERROR", e))

class AgentTool:
    """
    Interface de base pour tous les outils.
    Intègre désormais le Sandboxing STRICT par processus OS (multiprocessing + SIGTERM).
    """
    name: str
    description: str
    args_schema: type[BaseModel]
    
    requires_approval: bool = False
    timeout_seconds: int = 15

    def run(self, **kwargs) -> Any:
        is_approved = kwargs.pop("approved_by_admin", False)
        validated_args = self.args_schema(**kwargs)
        
        if self.requires_approval and not is_approved:
            logger.warning(f"🔒 Bloqué par Least Privilege : L'outil {self.name} nécessite une approbation.")
            raise SecurityException(
                f"Permission refusée. L'outil '{self.name}' nécessite une élévation de privilège."
            )

        # 3. Vrai Sandboxing (Process Isolation) P0 Fix
        queue = multiprocessing.Queue()
        process = multiprocessing.Process(
            target=_worker_wrapper,
            args=(queue, self._execute, validated_args.model_dump())
        )
        process.start()
        
        process.join(self.timeout_seconds)
        
        if process.is_alive():
            logger.error(f"⏳ Timeout : L'outil {self.name} a dépassé {self.timeout_seconds}s. KILL OS EN COURS.")
            process.terminate()
            process.join()  # S'assure que les ressources sont libérées
            raise SecurityException(
                f"Timeout de {self.timeout_seconds}s dépassé pour l'outil {self.name}. Processus tué."
            )
            
        if not queue.empty():
            status, result = queue.get()
            if status == "ERROR":
                raise result
            return result
            
        raise SecurityException("Le processus a terminé sans renvoyer de résultat.")

    def _execute(self, **kwargs) -> Any:
        raise NotImplementedError("Subclasses must implement _execute")
