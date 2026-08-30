from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from benchforge import SCHEMA_VERSION
from benchforge.schemas.task import Repository, TaskInstance


class Benchmark(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    schema_version: str = SCHEMA_VERSION
    repository: Repository
    description: str = ""
    tasks: list[TaskInstance] = Field(default_factory=list)
