from __future__ import annotations

import typer

from benchforge import __version__
from benchforge.catalog import CatalogError, list_benchmarks, load_benchmark
from benchforge.cli.inspect import inspect_cmd
from benchforge.cli.run import run_cmd
from benchforge.cli.validate import validate_cmd
from benchforge.models.registry import list_adapters
from benchforge.utils.logging import setup_logging

app = typer.Typer(
    name="benchforge",
    help="Reproducible evaluation harness for AI coding models on real repository issues.",
    no_args_is_help=True,
)
benchmark_app = typer.Typer(help="List and inspect benchmarks.")
task_app = typer.Typer(help="Inspect and schema-validate benchmark tasks.")
results_app = typer.Typer(help="Show stored evaluation results (Phase 5).")

app.add_typer(benchmark_app, name="benchmark")
app.add_typer(task_app, name="task")
app.add_typer(results_app, name="results")


@app.callback()
def _root(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Debug logging"),
) -> None:
    setup_logging(verbose=verbose)


@app.command()
def version() -> None:
    typer.echo(__version__)


@app.command("run")
def run(
    benchmark: str = typer.Option(..., "--benchmark", help="Benchmark id, e.g. dub-v0.1"),
    model: str = typer.Option("mock", "--model", help="Adapter name"),
    instance: str | None = typer.Option(None, "--instance", help="Optional single instance_id"),
) -> None:
    run_cmd(benchmark=benchmark, model=model, instance=instance)


@app.command("mine")
def mine(
    repo: str = typer.Option(..., "--repo", help="GitHub owner/name, e.g. dubinc/dub"),
) -> None:
    _ = repo
    typer.secho(
        "GitHub candidate mining is not implemented yet (Phase 6).",
        fg=typer.colors.YELLOW,
        err=True,
    )
    raise typer.Exit(2)


@benchmark_app.command("list")
def benchmark_list() -> None:
    ids = list_benchmarks()
    if not ids:
        typer.echo("No benchmarks found. Add a directory under ./benchmarks with benchmark.yaml.")
        return
    for benchmark_id in ids:
        try:
            bench = load_benchmark(benchmark_id)
        except CatalogError as exc:
            typer.secho(f"{benchmark_id}\tERROR {exc}", fg=typer.colors.RED)
            continue
        typer.echo(f"{bench.id}\t{len(bench.tasks)} tasks\t{bench.repository.url}")


@task_app.command("inspect")
def task_inspect(
    instance_id: str = typer.Argument(..., help="Task instance_id"),
    include_private: bool = typer.Option(False, "--include-private"),
) -> None:
    inspect_cmd(instance_id=instance_id, include_private=include_private)


@task_app.command("validate")
def task_validate(
    instance_id: str = typer.Argument(..., help="Task instance_id or YAML path"),
) -> None:
    validate_cmd(instance_id=instance_id)


@results_app.command("show")
def results_show(run_id: str = typer.Argument(...)) -> None:
    _ = run_id
    typer.secho("Result storage is not implemented yet (Phase 5).", err=True)
    raise typer.Exit(2)


@results_app.command("summary")
def results_summary(benchmark_run_id: str = typer.Argument(...)) -> None:
    _ = benchmark_run_id
    typer.secho("Result aggregation is not implemented yet (Phase 5).", err=True)
    raise typer.Exit(2)


@app.command("adapters")
def adapters() -> None:
    for name in list_adapters():
        typer.echo(name)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
