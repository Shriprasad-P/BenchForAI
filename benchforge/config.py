"""Runtime configuration. Paths are cwd-relative unless BENCHFORGE_BENCHMARKS is set."""

from __future__ import annotations

import os
from pathlib import Path

from benchforge import SCHEMA_VERSION

DEFAULT_TIMEOUT_SECONDS = 1200
DEFAULT_DOCKERFILE = "Dockerfile"


def benchmarks_dir() -> Path:
    override = os.environ.get("BENCHFORGE_BENCHMARKS")
    if override:
        return Path(override).expanduser().resolve()
    return (Path.cwd() / "benchmarks").resolve()


def artifacts_dir() -> Path:
    override = os.environ.get("BENCHFORGE_ARTIFACTS")
    if override:
        return Path(override).expanduser().resolve()
    return (Path.cwd() / "artifacts").resolve()


def schema_version() -> str:
    return SCHEMA_VERSION
