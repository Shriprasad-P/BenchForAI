from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator

from benchforge import SCHEMA_VERSION
from benchforge.config import DEFAULT_DOCKERFILE, DEFAULT_TIMEOUT_SECONDS


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Repository(_Strict):
    owner: str
    name: str
    url: str

    @field_validator("owner", "name")
    @classmethod
    def _non_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must be non-empty")
        return value.strip()


class Issue(_Strict):
    number: int = Field(ge=1)
    title: str
    body: str


class Environment(_Strict):
    dockerfile: str = DEFAULT_DOCKERFILE
    timeout_seconds: int = Field(default=DEFAULT_TIMEOUT_SECONDS, ge=1)
    build_command: str | None = None


class CommandSpec(_Strict):
    """Hidden evaluation command. Never include in model-facing context."""

    name: str
    command: str


class EvalSuite(_Strict):
    fail_to_pass: list[CommandSpec] = Field(default_factory=list)
    pass_to_pass: list[CommandSpec] = Field(default_factory=list)


class Gold(_Strict):
    """Maintainer solution. Never include in model-facing context."""

    fix_commit: str
    patch_path: str
    patch: str | None = None


class TaskMetadata(_Strict):
    category: str | None = None
    difficulty: str | None = None
    verified: bool = False
    notes: str | None = None


class PublicTask(_Strict):
    """Subset of a task that is safe to show an evaluated model."""

    instance_id: str
    schema_version: str
    repository: Repository
    base_commit: str
    issue: Issue
    environment: Environment


class TaskInstance(_Strict):
    """Full benchmark instance, including private evaluation fields."""

    instance_id: str
    schema_version: str = SCHEMA_VERSION
    repository: Repository
    base_commit: str
    issue: Issue
    environment: Environment = Field(default_factory=Environment)
    tests: EvalSuite = Field(default_factory=EvalSuite)
    gold: Gold
    metadata: TaskMetadata = Field(default_factory=TaskMetadata)

    @field_validator("instance_id")
    @classmethod
    def _instance_id_shape(cls, value: str) -> str:
        if "__" not in value or not value.split("-")[-1].isdigit():
            raise ValueError(
                "instance_id must look like '{owner}__{repo}-{issue}', e.g. dub__dub-1234"
            )
        return value

    @field_validator("base_commit")
    @classmethod
    def _base_commit_present(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("base_commit must be a non-empty git revision")
        return value.strip()

    def to_public(self) -> PublicTask:
        return PublicTask(
            instance_id=self.instance_id,
            schema_version=self.schema_version,
            repository=self.repository,
            base_commit=self.base_commit,
            issue=self.issue,
            environment=self.environment,
        )
