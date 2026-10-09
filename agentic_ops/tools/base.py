import concurrent.futures
import logging
from typing import Any

from pydantic import BaseModel

logger = logging.getLogger("AgenticSecurity")


class SecurityException(Exception):
    pass


class AgentTool:
    """
    Interface de base pour tous les outils.
    Intègre désormais le Sandboxing, le Least Privilege et les Timeouts (P0 MLOps).
    """

    name: str
    description: str
    args_schema: type[BaseModel]
    
    # [ALERTE MLOPS] Least Privilege Configuration
    requires_approval: bool = False
    timeout_seconds: int = 15

    def run(self, **kwargs) -> Any:
        # Extraction du contexte de sécurité en amont de Pydantic
        is_approved = kwargs.pop("approved_by_admin", False)

        # 1. Validation Pydantic (Anti-hallucination)
        validated_args = self.args_schema(**kwargs)
        
        # 2. Sandboxing & Least Privilege
        if self.requires_approval and not is_approved:
            logger.warning(f"🔒 Bloqué par Least Privilege : L'outil {self.name} nécessite une approbation.")
            raise SecurityException(
                f"Permission refusée. L'outil '{self.name}' nécessite une élévation de privilège."
            )

        # 3. Timeouts (Isolation des ressources)
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(self._execute, **validated_args.model_dump())
                return future.result(timeout=self.timeout_seconds)
        except concurrent.futures.TimeoutError:
            logger.error(f"⏳ Timeout : L'outil {self.name} a dépassé les {self.timeout_seconds}s.")
            raise SecurityException(
                f"Timeout de {self.timeout_seconds}s dépassé pour l'outil {self.name}."
            )

    def _execute(self, **kwargs) -> Any:
        raise NotImplementedError("Subclasses must implement _execute")
