"""Test Google Keep JSON models"""
import pytest


@pytest.fixture
def note():
    from keep2roam.models import Note

    return Note(
        color="DEFAULT",
        is_trashed=False,
        is_pinned=False,
        is_archived=False,
        text_content="Test Note",
        title="Test Note Title",
        user_edited_timestamp_usec=1577836800000000,
    )


@pytest.fixture
def note_list():
    from keep2roam.models import Annotation, Note

    return Note(
        color="DEFAULT",
        is_trashed=False,
        is_pinned=False,
        is_archived=False,
        list_content=[
            Annotation(text=f"Test Item {i+1}", is_checked=False) for i in range(3)
        ],
        title="Test Note Title",
        user_edited_timestamp_usec=1577836800000000,
    )


def test_note_date_and_time(note):
    from datetime import datetime

    assert note.date_and_time == datetime(2020, 1, 1, 0, 0)


def test_note_date_string(note):
    assert note.date_string == "January 1st, 2020"


def test_note_time_string(note):
    assert note.time_string == "12:00 AM"


@pytest.mark.parametrize("note_obj, result", [("note", False), ("note_list", True)])
def test_note_is_list(note_obj, result, request):
    assert request.getfixturevalue(note_obj).is_list() == result


def test_note_is_empty(note):
    assert not note.is_empty()
    note.text_content = note.title = ""
    assert note.is_empty()


def test_note_list_is_empty(note_list):
    assert not note_list.is_empty()
    note_list.title = ""
    note_list.list_content = []
    assert note_list.is_empty()


def test_to_markdown_string(note):
    assert note.to_markdown_string() == "- Test Note Title\n    - Test Note\n"
    setattr(note, "title", "")
    assert note.to_markdown_string() == "- 12:00 AM\n    - Test Note\n"


def test_to_markdown_string_list(note_list):
    assert note_list.to_markdown_string() == (
        "- Test Note Title\n    - Test Item 1\n    - Test Item 2\n    - Test Item 3\n"
    )
    setattr(note_list, "title", "")
    assert note_list.to_markdown_string() == (
        "- 12:00 AM\n    - Test Item 1\n    - Test Item 2\n    - Test Item 3\n"
    )
