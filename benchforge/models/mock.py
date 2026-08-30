from __future__ import annotations

from pathlib import Path

from benchforge.models.base import ModelAdapter, ModelOutput
from benchforge.schemas.context import ModelContext


class MockModelAdapter(ModelAdapter):
    """Deterministic adapter for harness tests. No network, no paid APIs."""

    name = "mock"

    def __init__(self, patch: str = "", raw_response: str | None = None) -> None:
        self._patch = patch
        self._raw_response = raw_response if raw_response is not None else patch

    def solve(
        self,
        task_prompt: str,
        workspace_path: Path,
        context: ModelContext,
    ) -> ModelOutput:
        if not task_prompt.strip():
            raise ValueError("task_prompt must not be empty")
        if not workspace_path:
            raise ValueError("workspace_path is required")
        return ModelOutput(
            patch=self._patch,
            raw_response=self._raw_response,
            input_tokens=len(task_prompt.split()),
            output_tokens=len(self._patch.split()) if self._patch else 0,
            estimated_cost=0.0,
            metadata={
                "adapter": self.name,
                "instance_id": context.instance_id,
            },
        )
