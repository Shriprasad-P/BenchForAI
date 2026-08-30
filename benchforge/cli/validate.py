from __future__ import annotations

import typer

from benchforge.catalog import CatalogError
from benchforge.validation import validate_instance_id


def validate_cmd(
    instance_id: str = typer.Argument(..., help="Task instance_id or path to a task YAML file"),
) -> None:
    """Schema-level validation only. Docker/git/gold execution checks are Phase 4."""
    try:
        task, problems = validate_instance_id(instance_id)
    except CatalogError as exc:
        typer.secho(str(exc), fg=typer.colors.RED, err=True)
        raise typer.Exit(1) from exc

    typer.echo(f"instance_id: {task.instance_id}")
    typer.echo("schema: valid")
    if problems:
        typer.secho("quality checks:", fg=typer.colors.YELLOW)
        for problem in problems:
            typer.echo(f"  - {problem}")
        raise typer.Exit(2)

    typer.secho(
        "schema checks passed (execution validation is not implemented yet)",
        fg=typer.colors.GREEN,
    )
