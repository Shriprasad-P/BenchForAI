# BenchForge

Reproducible evaluation harness for AI coding models and coding agents on **real repository issues**.

BenchForge is not a coding assistant. It measures whether a model can produce a patch that actually fixes a historical bug in an existing codebase, using maintainer tests as the ground truth.

It is inspired by software-engineering benchmarks such as SWE-bench, with a narrower first goal: make **repository-specific** benchmark construction and evaluation straightforward. The first target corpus is [dub](https://github.com/dubinc/dub) (`dub-v0.1`).

No model performance numbers are claimed yet. The harness that would produce them is not implemented in v0.1.

## Why this exists

Leaderboard demos and chat transcripts are not evaluations. They are not pinned to a commit, they are not isolated, and they are easy to contaminate with the answer.

A coding model is useful in production only if it can:

1. Read a real issue as a developer would have seen it.
2. Change an existing repository at a known commit.
3. Pass tests that encoded the bug, without breaking tests that already passed.

Subjective “it looks right” review cannot do that. Automated FAIL_TO_PASS / PASS_TO_PASS checks can.

## How a benchmark instance works

A task is reconstructed from a historical issue that maintainers already fixed:

1. Take a closed issue and the PR/commit that resolved it.
2. Check out the commit **immediately before** the fix (`base_commit`).
3. Keep the issue title/body as the model-facing prompt.
4. Hide the gold patch, future commits, and evaluation tests from the model.
5. Apply a candidate patch.
6. Run bug tests and regression tests.
7. Mark the instance **RESOLVED** only if every required check passes.

`metadata.verified` must not be set just because YAML exists. Execution validation (Phase 4) is what promotes a candidate into a trusted task.

### FAIL_TO_PASS

Tests that demonstrate the original bug.

| When | Expected |
| --- | --- |
| Before candidate patch | FAIL |
| After a correct patch | PASS |

### PASS_TO_PASS

Regression tests that already passed at `base_commit`.

| When | Expected |
| --- | --- |
| Before candidate patch | PASS |
| After candidate patch | PASS |

An instance is **RESOLVED** only if the patch applies, the project builds when a build step exists, every FAIL_TO_PASS test passes, every PASS_TO_PASS test still passes, and the run finishes within the configured timeout. Partial credit is recorded in metrics; it is not a resolve.

## Architecture (v0.1)

```
GitHub repo  →  (mining: later)  →  task YAML
                                      │
                 public view ─────────┼──► model adapter ──► patch
                 private view ────────┘
                                      │
                         (harness: later) Docker + tests ──► EvalResult
```

| Package | Role in v0.1 |
| --- | --- |
| `benchforge/schemas` | Task, public task, result, error types, sanitized `ModelContext` |
| `benchforge/catalog.py` | Load `benchmarks/<id>/benchmark.yaml` and `tasks/*.yaml` |
| `benchforge/models` | `ModelAdapter` ABC, `MockModelAdapter`, registry |
| `benchforge/cli` | List / inspect / schema-validate. `run` and `mine` refuse until later phases |
| `benchforge/validation.py` | Schema-level checks only |
| `tests/fixtures/tiny_repo` | Tiny buggy Python package + gold patch for later harness tests |

Private fields (`gold`, FAIL_TO_PASS / PASS_TO_PASS commands, `verified`) are stripped by `TaskInstance.to_public()` and `build_model_context()`. Default `benchforge task inspect` prints only that public payload.

Model providers are adapters. v0.1 ships **mock** only. Paid APIs are intentionally absent.

## CLI

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

benchforge benchmark list
benchforge task inspect fixture__tiny-1   # after pointing BENCHFORGE_BENCHMARKS at a catalog
benchforge task inspect dub__dub-1234 --include-private   # humans only; never send to a model
benchforge task validate path/to/task.yaml
benchforge adapters
```

Evaluation, result storage, and GitHub mining commands exist but exit with a clear “not implemented” status:

```bash
benchforge run --benchmark dub-v0.1 --model mock
benchforge run --benchmark dub-v0.1 --model mock --instance dub__dub-1234
benchforge results show <run-id>
benchforge results summary <benchmark-run-id>
benchforge mine --repo dubinc/dub
```

Set `BENCHFORGE_BENCHMARKS` to override the catalog directory (default: `./benchmarks`).

## Adding a task by hand

Create `benchmarks/<benchmark-id>/tasks/<instance_id>.yaml` matching the `TaskInstance` schema. Minimum shape:

```yaml
instance_id: owner__repo-1234
schema_version: "0.1"
repository:
  owner: owner
  name: repo
  url: https://github.com/owner/repo
base_commit: "<commit before the fix>"
issue:
  number: 1234
  title: "..."
  body: "..."
environment:
  dockerfile: Dockerfile
  timeout_seconds: 1200
tests:
  fail_to_pass:
    - name: test_bug
      command: pytest tests/test_bug.py
  pass_to_pass:
    - name: test_regression
      command: pytest tests/test_ok.py
gold:
  fix_commit: "<fixing commit>"
  patch_path: gold.patch
metadata:
  category: backend
  difficulty: medium
  verified: false
```

Keep `gold.patch` next to the task or elsewhere on disk; do not put the patch body in the model prompt. `dub-v0.1` currently has **zero** verified tasks.

## Adding a model adapter

1. Subclass `benchforge.models.base.ModelAdapter`.
2. Implement `solve(task_prompt, workspace_path, context) -> ModelOutput`.
3. Register it with `benchforge.models.registry.register("name", factory)`.
4. Use only `ModelContext` / `PublicTask`. Never read `task.gold` or `task.tests` in the adapter.

Until Phase 2, `solve` is only exercised in unit tests (the mock adapter).

## Current status

**BenchForge v0.1 (Phase 1).** Schemas, catalog, CLI inspect/validate, mock adapter, leakage tests, and a local fixture repository.

Not in this version: workspace checkout, patch apply, Docker evaluation, gold-patch validation, SQLite result store, metric aggregation, GitHub mining, or Dub tasks.

## Roadmap

| Phase | Work |
| --- | --- |
| 2 | Workspace, git checkout, patch apply, FAIL_TO_PASS / PASS_TO_PASS on the local fixture |
| 3 | Docker-isolated execution, resource limits, network off during tests |
| 4 | Execution validator (baseline fail/pass, gold apply, determinism) |
| 5 | SQLite runs, artifacts, benchmark-level metrics |
| 6 | GitHub candidate mining for `dubinc/dub` (candidates ≠ verified tasks) |
| 7 | Manually verified `dub-v0.1` instances |

## Development

```bash
pip install -e ".[dev]"
ruff check benchforge tests
ruff format benchforge tests
pytest
```

Python 3.12+ is required.
