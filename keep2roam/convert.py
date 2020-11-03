"""Keep / Roam conversion utility."""

import json
from pathlib import Path
from typing import cast

from marshmallow import ValidationError

from keep2roam.models import Note, NoteSchema


class Keep2RoamException(Exception):
    """Base class for all exceptions in Keep2Roam."""

    ...


def get_note(json_fpath: Path) -> Note:
    """Get a Google Keep note from a particular path.

    Args:
        json_fpath: The path to the json file.

    Returns:
        An instance of Note.

    Raises:
        Keep2RoamException: If an error occurs while parsing the file.

    """
    # Open the json_file
    with open(json_fpath, "r") as f:
        keep_dict = json.load(f)

    # Load and return the Note object
    try:
        return cast(Note, NoteSchema().load(keep_dict))
    except ValidationError:
        raise Keep2RoamException(
            f"An error occurred while parsing {json_fpath}, skipping..."
        )


def write_or_append_note(note: Note, root_path: Path) -> None:
    """Write or append a note to a particular path.

    If the file already exists this will append otherwise it will create and write to
    the path. The file name will be the note's date of creation in Roam Daily Note
    format.

    Args:
        note: An instance of Note
        root_path: The folder to which to write the note.

    """
    file_path = root_path.joinpath(note.date_string + ".md")
    open_mode = "a" if file_path.is_file() else "w"
    with open(file_path, open_mode) as fopen:
        md_note = note.to_markdown_string()
        fopen.write(md_note)


def convert(read_path: Path, write_path: Path) -> None:
    """Convert a directory of Google Keep json files to Roam Daily Notes.

    If the note is empty or cannot be processed, it will be ignored and a message will
    be printed to stdout. If two notes were created on the same day, they will be
    written to the same Daily Note file.

    Args:
        read_path: The path to find all the Google Keep json files.
        write_path: The path to write each of the converted Roam Daily Note files.

    """
    # Collect all of the json files in the archive path
    json_files = [p for p in read_path.iterdir() if p.is_file() and p.suffix == ".json"]
    print(f"Found {len(json_files)} Google Keep json files...")

    # Iterate over the found files and convert each one to a suitable markdown format
    for jf in json_files:
        try:
            note = get_note(jf)
            if not note.is_empty():
                write_or_append_note(note, write_path)
        except Keep2RoamException:
            pass
