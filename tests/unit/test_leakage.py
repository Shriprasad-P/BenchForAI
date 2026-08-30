from __future__ import annotations

from benchforge.schemas.context import (
    build_model_context,
    build_task_prompt,
    public_payload_contains_private_keys,
)
from benchforge.schemas.task import CommandSpec, EvalSuite, Gold, Issue, Repository, TaskInstance


def _private_task() -> TaskInstance:
    return TaskInstance(
        instance_id="dub__dub-1234",
        repository=Repository(owner="dubinc", name="dub", url="https://github.com/dubinc/dub"),
        base_commit="abc123def",
        issue=Issue(
            number=1234,
            title="broken redirect",
            body="Query params are dropped on redirect.",
        ),
        tests=EvalSuite(
            fail_to_pass=[
                CommandSpec(
                    name="HIDDEN_EVAL_TOKEN",
                    command="pytest tests/test_hidden_eval_token.py",
                )
            ],
            pass_to_pass=[CommandSpec(name="regression", command="pytest tests/test_ok.py")],
        ),
        gold=Gold(
            fix_commit="GOLD_FIX_COMMIT_TOKEN",
            patch_path="gold.patch",
            patch="diff --git a/secret.py b/secret.py\n+GOLD_PATCH_BODY_TOKEN\n",
        ),
    )


def test_public_view_omits_gold_and_tests() -> None:
    task = _private_task()
    public = task.to_public().model_dump(mode="json")
    leaked = public_payload_contains_private_keys(public)
    assert leaked == []
    blob = str(public)
    assert "GOLD_FIX_COMMIT_TOKEN" not in blob
    assert "GOLD_PATCH_BODY_TOKEN" not in blob
    assert "HIDDEN_EVAL_TOKEN" not in blob
    assert "fail_to_pass" not in blob
    assert "gold" not in blob


def test_model_context_omits_private_fields() -> None:
    task = _private_task()
    ctx = build_model_context(task)
    dumped = ctx.model_dump_json()
    prompt = build_task_prompt(task)
    for forbidden in (
        "GOLD_FIX_COMMIT_TOKEN",
        "GOLD_PATCH_BODY_TOKEN",
        "HIDDEN_EVAL_TOKEN",
        "gold.patch",
        "fail_to_pass",
        "pass_to_pass",
    ):
        assert forbidden not in dumped
        assert forbidden not in prompt
    assert "broken redirect" in prompt
    assert "abc123def" in prompt
    assert "Query params are dropped" in prompt
