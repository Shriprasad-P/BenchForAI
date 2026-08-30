from __future__ import annotations

import typer

PHASE2 = (
    "The evaluation runner is not implemented yet (Phase 2). "
    "Phase 1 supports listing, inspecting, and schema-validating tasks."
)


def run_cmd(
    benchmark: str = typer.Option(..., "--benchmark", help="Benchmark id, e.g. dub-v0.1"),
    model: str = typer.Option("mock", "--model", help="Adapter name (only 'mock' is registered)"),
    instance: str | None = typer.Option(None, "--instance", help="Optional single instance_id"),
) -> None:
    _ = (benchmark, model, instance)
    typer.secho(PHASE2, fg=typer.colors.YELLOW, err=True)
    raise typer.Exit(2)
