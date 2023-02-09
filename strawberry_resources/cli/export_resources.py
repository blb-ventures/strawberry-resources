import sys

import click
from strawberry.cli.utils import load_schema

from strawberry_resources.exporter import to_json


@click.command(short_help="Exports the resources")
@click.argument("schema", type=str)
@click.option(
    "--app-dir",
    default=".",
    type=str,
    show_default=True,
    help=(
        "Look for the module in the specified directory, by adding this to the "
        "PYTHONPATH. Defaults to the current working directory. "
        "Works the same as `--app-dir` in uvicorn."
    ),
)
@click.option(
    "--remove-nulls",
    is_flag=True,
    show_default=True,
    default=False,
    help="Remove null values from the output to keep its size smaller",
)
def export_resources(schema: str, app_dir: str, remove_nulls: bool):
    schema_obj = load_schema(schema, app_dir)
    sys.stdout.write(
        to_json(
            schema_obj,
            remove_nulls=remove_nulls,
            indent=2,
            ensure_ascii=False,
        ),
    )
