from __future__ import annotations

from abc import ABC, abstractmethod

from ..models import BenchmarkCase, ModelResponse


class ModelAdapter(ABC):
    @abstractmethod
    def run_case(self, case: BenchmarkCase) -> ModelResponse:
        """Run one benchmark case and return a structured response."""
