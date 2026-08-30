from __future__ import annotations

from pathlib import Path

import pytest
from benchforge.models.base import ModelAdapter
from benchforge.models.mock import MockModelAdapter
from benchforge.models.registry import get_adapter, list_adapters
from benchforge.schemas.context import ModelContext, build_model_context
from benchforge.schemas.task import Gold, Issue, Repository, TaskInstance


def _context() -> ModelContext:
    task = TaskInstance(
        instance_id="fixture__tiny-1",
        repository=Repository(
            owner="fixture", name="tiny", url="https://example.invalid/fixture/tiny"
        ),
        base_commit="aaa",
        issue=Issue(number=1, title="add is wrong", body="add(2,3) should be 5"),
        gold=Gold(fix_commit="bbb", patch_path="gold.patch"),
    )
    return build_model_context(task)


def test_mock_is_registered() -> None:
    assert "mock" in list_adapters()
    adapter = get_adapter("mock", patch="diff --git a/x b/x\n")
    assert isinstance(adapter, ModelAdapter)
    assert isinstance(adapter, MockModelAdapter)


def test_unknown_adapter() -> None:
    with pytest.raises(KeyError, match="Unknown model adapter"):
        get_adapter("openai")


def test_mock_returns_configured_patch(tmp_path: Path) -> None:
    ctx = _context()
    adapter = MockModelAdapter(patch="+fixed")
    out = adapter.solve(ctx.task_prompt, tmp_path, ctx)
    assert out.patch == "+fixed"
    assert out.estimated_cost == 0.0
    assert out.metadata["instance_id"] == "fixture__tiny-1"
    assert out.input_tokens > 0


def test_mock_rejects_empty_prompt(tmp_path: Path) -> None:
    ctx = _context()
    adapter = MockModelAdapter()
    with pytest.raises(ValueError, match="task_prompt"):
        adapter.solve("   ", tmp_path, ctx)
