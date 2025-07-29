"""Clean command for dbt-toolbox CLI."""

from typing import Annotated

import typer

from dbt_toolbox.dbt_parser import dbt_parser


def clean(
    models: Annotated[
        str | None,
        typer.Option(
            "--models",
            "-m",
            help="Specific models to clean from cache (comma-separated). "
            "If not provided, cleans entire cache.",
        ),
    ] = None,
) -> None:
    """Clean the cache completely or for specific models."""
    if models:
        # Clean specific models
        model_list = [m.strip() for m in models.split(",") if m.strip()]
        removed_models = dbt_parser.cache.clear_models_cache(model_list)

        if removed_models:
            typer.secho("🧹 Models cleaned from cache successfully!", fg=typer.colors.GREEN)
            typer.secho(f"Removed {len(removed_models)} models from cache:", fg=typer.colors.CYAN)
            for model in removed_models:
                typer.secho(f"  • {model}", fg=typer.colors.BRIGHT_BLACK)
        else:
            typer.secho("⚠️  No models were found in cache to clean", fg=typer.colors.YELLOW)

        # Show models that weren't found
        not_found = [m for m in model_list if m not in removed_models]
        if not_found:
            typer.secho(
                f"Models not found in cache: {', '.join(not_found)}",
                fg=typer.colors.BRIGHT_BLACK,
            )
    else:
        # Clean entire cache (original behavior)
        # Collect metadata before clearing
        cache_exists = dbt_parser.cache.cache_path.exists()
        cache_files = []

        if cache_exists:
            cache_files = list(dbt_parser.cache.cache_path.glob("*.cache"))

        dbt_parser.cache.clear()

        # Display metadata about what was cleaned
        typer.secho("🧹 Cache cleaned successfully!", fg=typer.colors.GREEN)

        if cache_files:
            typer.secho(f"Removed {len(cache_files)} cache files:", fg=typer.colors.CYAN)
            for cache_file in cache_files:
                typer.secho(f"  • {cache_file.name}", fg=typer.colors.BRIGHT_BLACK)
        else:
            typer.secho("Cache directory was already empty", fg=typer.colors.BRIGHT_BLACK)
