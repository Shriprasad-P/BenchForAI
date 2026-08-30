from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class RunStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ErrorType(StrEnum):
    PATCH_APPLY_FAILED = "PATCH_APPLY_FAILED"
    BUILD_FAILED = "BUILD_FAILED"
    TEST_FAILED = "TEST_FAILED"
    TIMEOUT = "TIMEOUT"
    MODEL_FAILED = "MODEL_FAILED"
    ENVIRONMENT_FAILED = "ENVIRONMENT_FAILED"
    INVALID_TASK = "INVALID_TASK"
    HARNESS_ERROR = "HARNESS_ERROR"


class EvalResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    instance_id: str
    model: str
    agent: str | None = None
    run_id: str
    status: RunStatus
    resolved: bool = False
    patch_applied: bool = False
    build_success: bool | None = None
    fail_to_pass_total: int = 0
    fail_to_pass_passed: int = 0
    pass_to_pass_total: int = 0
    pass_to_pass_passed: int = 0
    regressions: int = 0
    runtime_seconds: float = 0.0
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    estimated_cost: float = 0.0
    files_changed: int = 0
    lines_added: int = 0
    lines_removed: int = 0
    error_type: ErrorType | None = None
    error_message: str | None = None
    timestamp: datetime = Field(default_factory=datetime.now)
