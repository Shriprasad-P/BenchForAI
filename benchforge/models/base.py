from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from benchforge.schemas.context import ModelContext


class ModelOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    patch: str
    raw_response: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    estimated_cost: float = 0.0
    metadata: dict[str, str] = Field(default_factory=dict)


class ModelAdapter(ABC):
    """Provider-neutral solver. Implementations must not receive gold or hidden tests."""

    name: str

    @abstractmethod
    def solve(
        self,
        task_prompt: str,
        workspace_path: Path,
        context: ModelContext,
    ) -> ModelOutput:
        raise NotImplementedError
