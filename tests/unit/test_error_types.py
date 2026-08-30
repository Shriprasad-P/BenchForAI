from __future__ import annotations

from benchforge.schemas.result import ErrorType, EvalResult, RunStatus


def test_error_types_are_stable() -> None:
    expected = {
        "PATCH_APPLY_FAILED",
        "BUILD_FAILED",
        "TEST_FAILED",
        "TIMEOUT",
        "MODEL_FAILED",
        "ENVIRONMENT_FAILED",
        "INVALID_TASK",
        "HARNESS_ERROR",
    }
    assert {item.value for item in ErrorType} == expected


def test_result_defaults() -> None:
    result = EvalResult(
        instance_id="fixture__tiny-1",
        model="mock",
        run_id="run-1",
        status=RunStatus.FAILED,
        error_type=ErrorType.HARNESS_ERROR,
        error_message="not implemented",
    )
    assert result.resolved is False
    assert result.patch_applied is False
    assert result.fail_to_pass_passed == 0
    assert result.error_type is ErrorType.HARNESS_ERROR
