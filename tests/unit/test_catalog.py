from __future__ import annotations

from pathlib import Path

import pytest
from benchforge.catalog import CatalogError, find_task, list_benchmarks, load_benchmark
from benchforge.validation import validate_instance_id, validate_task_schema

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "benchmarks"


def test_list_and_load_fixture_benchmark(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BENCHFORGE_BENCHMARKS", str(FIXTURES))
    assert list_benchmarks() == ["fixture-v0.1"]
    bench = load_benchmark("fixture-v0.1")
    assert len(bench.tasks) == 1
    assert bench.tasks[0].instance_id == "fixture__tiny-1"


def test_find_task(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BENCHFORGE_BENCHMARKS", str(FIXTURES))
    task = find_task("fixture__tiny-1")
    assert task.gold.patch_path == "gold.patch"
    problems = validate_task_schema(task)
    assert problems == []


def test_missing_task(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BENCHFORGE_BENCHMARKS", str(FIXTURES))
    with pytest.raises(CatalogError, match="not found"):
        find_task("dub__dub-9999")


def test_validate_from_path() -> None:
    path = FIXTURES / "fixture-v0.1" / "tasks" / "fixture__tiny-1.yaml"
    task, problems = validate_instance_id(str(path))
    assert task.instance_id == "fixture__tiny-1"
    assert problems == []
