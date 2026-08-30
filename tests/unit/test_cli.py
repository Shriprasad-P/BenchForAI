from __future__ import annotations

from pathlib import Path

import pytest
from benchforge.cli.main import app
from typer.testing import CliRunner

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "benchmarks"
runner = CliRunner()


def test_help() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "run" in result.stdout
    assert "benchmark" in result.stdout


def test_benchmark_list(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BENCHFORGE_BENCHMARKS", str(FIXTURES))
    result = runner.invoke(app, ["benchmark", "list"])
    assert result.exit_code == 0
    assert "fixture-v0.1" in result.stdout
    assert "1 tasks" in result.stdout


def test_inspect_is_public(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BENCHFORGE_BENCHMARKS", str(FIXTURES))
    result = runner.invoke(app, ["task", "inspect", "fixture__tiny-1"])
    assert result.exit_code == 0
    assert "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb" not in result.stdout
    assert "fail_to_pass" not in result.stdout
    assert "add() subtracts" in result.stdout
    assert "model_context" in result.stdout


def test_inspect_private(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BENCHFORGE_BENCHMARKS", str(FIXTURES))
    result = runner.invoke(app, ["task", "inspect", "fixture__tiny-1", "--include-private"])
    assert result.exit_code == 0
    assert "gold" in result.stdout
    assert "fail_to_pass" in result.stdout


def test_run_not_implemented() -> None:
    result = runner.invoke(app, ["run", "--benchmark", "dub-v0.1", "--model", "mock"])
    assert result.exit_code == 2
    assert "Phase 2" in result.stderr


def test_adapters() -> None:
    result = runner.invoke(app, ["adapters"])
    assert result.exit_code == 0
    assert "mock" in result.stdout
