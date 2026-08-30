"""Leakage-safe model context. Only information available at the base commit."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from benchforge.schemas.task import TaskInstance

_PRIVATE_FIELD_NAMES = frozenset(
    {
        "gold",
        "fix_commit",
        "patch_path",
        "fail_to_pass",
        "pass_to_pass",
        "verified",
        "tests",
    }
)


class ModelContext(BaseModel):
    model_config = ConfigDict(extra="forbid")

    instance_id: str
    repository_url: str
    base_commit: str
    issue_number: int
    issue_title: str
    issue_body: str
    task_prompt: str
    extra: dict[str, str] = Field(default_factory=dict)


def build_task_prompt(task: TaskInstance) -> str:
    public = task.to_public()
    return (
        f"Repository: {public.repository.url}\n"
        f"Base commit: {public.base_commit}\n"
        f"Issue #{public.issue.number}: {public.issue.title}\n\n"
        f"{public.issue.body.strip()}\n"
    )


def build_model_context(task: TaskInstance) -> ModelContext:
    """Build the only context an evaluated model is allowed to see."""
    public = task.to_public()
    return ModelContext(
        instance_id=public.instance_id,
        repository_url=str(public.repository.url),
        base_commit=public.base_commit,
        issue_number=public.issue.number,
        issue_title=public.issue.title,
        issue_body=public.issue.body,
        task_prompt=build_task_prompt(task),
    )


def public_payload_contains_private_keys(payload: dict) -> list[str]:
    found: list[str] = []

    def walk(obj: object) -> None:
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key in _PRIVATE_FIELD_NAMES:
                    found.append(str(key))
                walk(value)
        elif isinstance(obj, list):
            for item in obj:
                walk(item)

    walk(payload)
    return found
