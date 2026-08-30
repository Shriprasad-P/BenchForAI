"""Load benchmark.yaml + tasks/*.yaml from disk. SQLite persistence is Phase 5."""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import ValidationError

from benchforge.config import benchmarks_dir
from benchforge.schemas.benchmark import Benchmark
from benchforge.schemas.task import Repository, TaskInstance


class CatalogError(ValueError):
    pass


def _read_yaml(path: Path) -> dict:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise CatalogError(f"Cannot read {path}: {exc}") from exc
    data = yaml.safe_load(text)
    if not isinstance(data, dict):
        raise CatalogError(f"{path} must contain a YAML mapping")
    return data


def load_task_file(path: Path) -> TaskInstance:
    data = _read_yaml(path)
    try:
        return TaskInstance.model_validate(data)
    except ValidationError as exc:
        raise CatalogError(f"Invalid task file {path}:\n{exc}") from exc


def _load_benchmark_meta(path: Path) -> dict:
    data = _read_yaml(path)
    data.pop("tasks", None)
    return data


def load_benchmark(benchmark_id: str, root: Path | None = None) -> Benchmark:
    root = root or benchmarks_dir()
    bench_dir = root / benchmark_id
    meta_path = bench_dir / "benchmark.yaml"
    if not meta_path.is_file():
        raise CatalogError(f"Benchmark '{benchmark_id}' not found at {meta_path}")

    meta = _load_benchmark_meta(meta_path)
    tasks_dir = bench_dir / "tasks"
    tasks: list[TaskInstance] = []
    if tasks_dir.is_dir():
        for path in sorted(tasks_dir.glob("*.yaml")):
            tasks.append(load_task_file(path))

    try:
        repository = Repository.model_validate(meta["repository"])
        return Benchmark(
            id=meta.get("id", benchmark_id),
            schema_version=str(meta.get("schema_version", "0.1")),
            repository=repository,
            description=meta.get("description", ""),
            tasks=tasks,
        )
    except (ValidationError, KeyError) as exc:
        raise CatalogError(f"Invalid benchmark.yaml at {meta_path}: {exc}") from exc


def list_benchmarks(root: Path | None = None) -> list[str]:
    root = root or benchmarks_dir()
    if not root.is_dir():
        return []
    ids: list[str] = []
    for child in sorted(root.iterdir()):
        if child.is_dir() and (child / "benchmark.yaml").is_file():
            ids.append(child.name)
    return ids


def find_task(instance_id: str, root: Path | None = None) -> TaskInstance:
    root = root or benchmarks_dir()
    for benchmark_id in list_benchmarks(root):
        benchmark = load_benchmark(benchmark_id, root)
        for task in benchmark.tasks:
            if task.instance_id == instance_id:
                return task
    raise CatalogError(f"Task '{instance_id}' not found under {root}")
