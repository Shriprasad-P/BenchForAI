"""Schema-only task checks. Environment/gold execution validation is Phase 4."""

from __future__ import annotations

from pathlib import Path

from pydantic import ValidationError

from benchforge.catalog import CatalogError, find_task, load_task_file
from benchforge.schemas.task import TaskInstance


def validate_task_schema(task: TaskInstance) -> list[str]:
    """Return human-readable problems. Empty list means the metadata schema is usable."""
    problems: list[str] = []
    if not task.tests.fail_to_pass:
        problems.append("no FAIL_TO_PASS tests defined")
    if not task.gold.fix_commit.strip():
        problems.append("gold.fix_commit is empty")
    if not task.gold.patch_path.strip() and not (task.gold.patch or "").strip():
        problems.append("gold patch_path and inline patch are both empty")
    if task.metadata.verified:
        problems.append(
            "metadata.verified is true, but execution validation is not implemented yet (Phase 4)"
        )
    return problems


def validate_instance_id(instance_id: str) -> tuple[TaskInstance, list[str]]:
    path = Path(instance_id)
    if path.is_file():
        task = load_task_file(path)
    else:
        try:
            task = find_task(instance_id)
        except CatalogError:
            raise
    try:
        TaskInstance.model_validate(task.model_dump())
    except ValidationError as exc:
        return task, [str(exc)]
    return task, validate_task_schema(task)
