#!/usr/bin/env python

from pathlib import Path
import json

import click

from models import NoteSchema, Note

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


class Keep2RoamException(Exception):
    pass


def open_note(json_fpath: Path) -> Note:
    # Open the json_file
    with open(json_fpath, 'r') as f:
        keep_dict = json.load(f)

    # Load and return the Note object
    try:
        return NoteSchema().load(keep_dict)
    except Exception:
        raise Keep2RoamException(
            f"An error occurred while parsing {json_fpath}, skipping..."
        )


def write_or_append_note(note: Note, root_path: Path):
    file_path = root_path.joinpath(note.date_string + ".md")
    open_mode = 'a' if file_path.is_file() else 'w'
    with open(file_path, open_mode) as fopen:
        md_note = note.to_markdown_string()
        fopen.write(md_note)


def convert(read_path: Path, write_path: Path):
    # Collect all of the json files in the archive path
    json_files = [
        p
        for p in read_path.iterdir()
        if p.is_file() and p.suffix == '.json'
    ]
    print(f"Found {len(json_files)}...")

    # Iterate over the found files and convert each one to a suitable
    # markdown format
    for jf in json_files:
        try:
            note = open_note(jf)
            if not note.is_empty():
                write_or_append_note(note, write_path)
        except Keep2RoamException:
            pass


@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument('src', type=click.Path(exists=True, file_okay=False))
@click.argument('dest', type=click.Path(exists=True, file_okay=False, writable=True))
def cli(src: str, dest: str) -> None:
    """Convert SRC Google Keep Takeout dump and write to DEST folder.

    Assumes SRC exists and creates DEST folder if it does not exist.

    """
    convert(Path(src), Path(dest))


if __name__ == "__main__":
    cli()
