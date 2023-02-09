import click

from .export import export


@click.group()
def run():  # pragma: nocover
    pass


run.add_command(export)
