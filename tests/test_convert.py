"""Test Conversion API."""

from pathlib import Path
from unittest.mock import Mock

import pytest


BASE_PATH = Path(__file__).parent
KEEP_NOTE_PATH = (BASE_PATH / Path("sample/keep_note.json")).resolve()
KEEP_NOTE_LIST_PATH = (BASE_PATH / Path("sample/keep_note_list.json")).resolve()
KEEP_NOTE_MISSING_TITLE = (
    BASE_PATH / Path("sample/keep_note_missing_title.json")
).resolve()
KEEP_NOTE_MISSING_BODY = (
    BASE_PATH / Path("sample/keep_note_missing_body.json")
).resolve()


def test_get_note():
    from keep2roam.convert import get_note

    note = get_note(KEEP_NOTE_PATH)
    assert note.title == "Test Note Title"
    assert note.text_content == "Test Note"
    assert note.user_edited_timestamp_usec == 1577836800000000


def test_get_note_list():
    from keep2roam.convert import get_note

    note_list = get_note(KEEP_NOTE_LIST_PATH)
    assert note_list.title == "Test List Title"
    assert len(note_list.list_content) == 3
    assert note_list.user_edited_timestamp_usec == 1577836800000000


@pytest.mark.parametrize("path", [KEEP_NOTE_MISSING_TITLE, KEEP_NOTE_MISSING_BODY])
def test_get_note_missing_title(path):
    from keep2roam.convert import Keep2RoamException, get_note

    with pytest.raises(Keep2RoamException) as err:
        get_note(path)

    assert "An error occurred" in str(err)


def test_write_or_append_note(monkeypatch, tmp_path):
    from keep2roam.convert import write_or_append_note

    note = Mock()
    date_str = "January 1, 2020"
    markdown_contents = "* Test\n    * Test Body\n"
    monkeypatch.setattr(note, "date_string", date_str)
    monkeypatch.setattr(note, "to_markdown_string", lambda: markdown_contents)
    write_or_append_note(note, tmp_path)

    # Should create file and write to it
    test_file = tmp_path / Path(date_str + ".md")
    assert test_file.open().read() == markdown_contents

    # Should append to the same file
    write_or_append_note(note, tmp_path)
    assert test_file.open().read() == markdown_contents * 2


def test_convert(capsys, tmp_path, monkeypatch):
    from keep2roam.convert import Keep2RoamException, convert

    read_path = tmp_path / Path("read_path")
    read_path.mkdir()
    write_path = tmp_path / Path("write_path")
    write_path.mkdir()

    # Create three simple files
    fpaths = [read_path / Path(f"file{n+1}.json") for n in range(3)]
    [fp.open("w+").write("") for fp in fpaths]

    note_mock = Mock()
    note_mock.is_empty = Mock(side_effect=[True, False, False])
    monkeypatch.setattr(
        "keep2roam.convert.get_note",
        Mock(side_effect=[note_mock, note_mock, Keep2RoamException()]),
    )
    woa_mock = Mock()
    monkeypatch.setattr("keep2roam.convert.write_or_append_note", woa_mock)

    # Only the second two files should be read
    convert(read_path, write_path)
    assert f"Found {len(fpaths)}" in capsys.readouterr().out
    assert woa_mock.call_count == 1
