from __future__ import annotations

from pathlib import Path

import pytest
from benchforge.schemas.task import CommandSpec, EvalSuite, Gold, Issue, Repository, TaskInstance
from pydantic import ValidationError

REPO = Repository(owner="dubinc", name="dub", url="https://github.com/dubinc/dub")
ISSUE = Issue(number=1234, title="broken link redirect", body="Redirects drop query params.")
GOLD = Gold(fix_commit="deadbeef", patch_path="gold.patch")


def _task(**overrides: object) -> TaskInstance:
    data: dict = {
        "instance_id": "dub__dub-1234",
        "repository": REPO,
        "base_commit": "abc123",
        "issue": ISSUE,
        "gold": GOLD,
        "tests": EvalSuite(
            fail_to_pass=[
                CommandSpec(name="hidden_eval_xyz", command="pytest tests/test_secret.py")
            ],
            pass_to_pass=[CommandSpec(name="regression", command="pytest tests/test_ok.py")],
        ),
    }
    data.update(overrides)
    return TaskInstance.model_validate(data)


def test_valid_task_roundtrip() -> None:
    task = _task()
    dumped = task.model_dump()
    again = TaskInstance.model_validate(dumped)
    assert again.instance_id == "dub__dub-1234"
    assert again.gold.fix_commit == "deadbeef"


def test_yaml_json_equivalent(tmp_path: Path) -> None:
    import json

    import yaml

    task = _task()
    path = tmp_path / "task.yaml"
    path.write_text(yaml.safe_dump(task.model_dump(mode="json")), encoding="utf-8")
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    from_yaml = TaskInstance.model_validate(loaded)
    from_json = TaskInstance.model_validate(json.loads(task.model_dump_json()))
    assert from_yaml == from_json


def test_rejects_bad_instance_id() -> None:
    with pytest.raises(ValidationError):
        _task(instance_id="not-a-valid-id")


def test_rejects_empty_base_commit() -> None:
    with pytest.raises(ValidationError):
        _task(base_commit="   ")


def test_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        TaskInstance.model_validate(
            {
                "instance_id": "dub__dub-1",
                "repository": REPO.model_dump(),
                "base_commit": "abc",
                "issue": ISSUE.model_dump(),
                "gold": GOLD.model_dump(),
                "secret_hint": "do not allow",
            }
        )
