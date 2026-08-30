from __future__ import annotations

import json

import typer

from benchforge.catalog import CatalogError, find_task
from benchforge.schemas.context import build_model_context, public_payload_contains_private_keys


def inspect_task(instance_id: str, include_private: bool = False) -> str:
    task = find_task(instance_id)
    if include_private:
        payload = task.model_dump(mode="json")
        return json.dumps(payload, indent=2)

    public = task.to_public().model_dump(mode="json")
    leaked = public_payload_contains_private_keys(public)
    if leaked:
        raise CatalogError(f"Public view leaked private keys: {leaked}")
    context = build_model_context(task)
    return json.dumps(
        {
            "task": public,
            "model_context": context.model_dump(mode="json"),
        },
        indent=2,
    )


def inspect_cmd(
    instance_id: str = typer.Argument(..., help="Task instance_id, e.g. dub__dub-1234"),
    include_private: bool = typer.Option(
        False,
        "--include-private",
        help="Include gold patch metadata and hidden tests. Never send this to a model.",
    ),
) -> None:
    try:
        typer.echo(inspect_task(instance_id, include_private=include_private))
    except CatalogError as exc:
        typer.secho(str(exc), fg=typer.colors.RED, err=True)
        raise typer.Exit(1) from exc
