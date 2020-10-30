#!/usr/bin/env python

import argparse
from pathlib import Path
import json

from models import NoteSchema, Note


def open_note(json_fpath: Path) -> Note:
    # Open the json_file
    with open(json_fpath, 'r') as f:
        keep_dict = json.load(f)

    # Load and return the Note object
    try:
        return NoteSchema().load(keep_dict)
    except Exception:
        print(json_fpath)
        quit()


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
        note = open_note(jf)
        if not note.is_empty():
            write_or_append_note(note, write_path)


def run_parser() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert a Google Keep dump to Markdown files."
    )
    parser.add_argument(
        'input',
        type=Path,
        help='The folder containing the Google Keep Dump.'
    )
    parser.add_argument(
        'output',
        type=Path,
        help='The folder to write the converted files.'
    )
    args = parser.parse_args()

    return args


def main():
    args = run_parser()
    convert(args.input, args.output)


if __name__ == "__main__":
    main()
