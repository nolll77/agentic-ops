"""
Interface minimale, dérivée uniquement du besoin réel de DATA-042.
Ne pas anticiper Datadog/SageMaker ici.
"""

from __future__ import annotations

from typing import Protocol

from agentic_ops.core.contracts import Signal


class ObservabilityAdapter(Protocol):
    def get_signal(self, signal_id: str) -> Signal: ...
