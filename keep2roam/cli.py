"""CLI entry point for keep2roam."""

from pathlib import Path

import click

from keep2roam.convert import convert
from keep2roam.version import get_version


CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


def print_version(ctx, param, value):  # type: ignore
    """Print package version callback."""
    if not value or ctx.resilient_parsing:
        return
    click.echo(get_version())
    ctx.exit()


@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument("src", type=click.Path(exists=True, file_okay=False))
@click.argument("dest", type=click.Path(exists=True, file_okay=False, writable=True))
@click.option(
    "--version",
    is_flag=True,
    callback=print_version,
    is_eager=True,
    expose_value=False,
    help="Prints the CLI version",
)
def cli(src: str, dest: str) -> None:
    """Convert SRC Google Keep Takeout dump and write to DEST folder.

    Assumes SRC exists and creates DEST folder if it does not exist.

    """
    convert(Path(src), Path(dest))
