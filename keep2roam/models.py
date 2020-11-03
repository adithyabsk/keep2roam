"""Schema and Models for Google Keep objects."""
import re
import unicodedata
from datetime import datetime
from types import SimpleNamespace
from typing import Any, Dict, Mapping, cast

from marshmallow import (
    EXCLUDE,
    Schema,
    ValidationError,
    fields,
    post_load,
    validates_schema,
)


JSON = Dict[str, Any]


def _process_dict_values(value: Any) -> Any:
    """Process a returned from a JSON response.

    Args:
        value: A dict, list, or value returned from a JSON response.

    Returns:
        Either an SimpleNamespace, a List of processed values, or the original value \
            passed through.

    """
    if isinstance(value, Mapping):
        return SimpleNamespace(**value)  # pragma: no cover
    elif isinstance(value, list):
        return [_process_dict_values(v) for v in value]
    else:
        return value


def camelcase(s: str) -> str:
    """Convert snake case to camel case.

    Example:
        >>> camelcase("camel_case")
        'camelCase'
    """
    parts = iter(s.split("_"))
    return next(parts) + "".join(i.title() for i in parts)


def suffix(d: int) -> str:
    """Convert an input date integer to a string with a suffix.

    Example:
        >>> suffix(10)
        'th'
        >>> suffix(2)
        'nd'
        >>> suffix(23)
        'rd'
        >>> suffix(4)
        'th'

    """
    return "th" if 11 <= d <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(d % 10, "th")


def custom_strftime(fmt: str, t: datetime) -> str:
    """Add suffixes to dates in strftime.

    Example:
        >>> from datetime import date
        >>> custom_strftime("{S}", date(2020, 1, 1))
        '1st'
        >>> custom_strftime("{S}", date(2020, 2, 2))
        '2nd'
        >>> custom_strftime("{S}", date(2020, 10, 3))
        '3rd'
        >>> custom_strftime("{S}", date(2020, 10, 24))
        '24th'

    Args:
        fmt: The format string
        t: The datetime object

    Returns:
        The string formatted date.

    """
    # https://stackoverflow.com/a/5891598/3262054
    return t.strftime(fmt).replace("{S}", str(t.day) + suffix(t.day))


class BaseSchema(Schema):
    """Support camel case conversion support and auto object creation."""

    __model__: Any = SimpleNamespace
    """Determine the object that is created when the load method is called."""

    class Meta:
        unknown = EXCLUDE

    def on_bind_field(self, field_name: str, field_obj: fields.Field) -> None:
        """Modify a field when it is bound to the schema.

        Automatically convert all schema fields to their camelCase representations.

        Args:
            field_name: The name of the field
            field_obj: The field object

        """
        # https://marshmallow.readthedocs.io/en/latest/examples.html#inflection-camel-casing-keys
        field_obj.data_key = camelcase(field_obj.data_key or field_name)

    @post_load
    def make_object(self, data: JSON, **kwargs: Any) -> "__model__":
        """Build model for the given `__model__` class attribute.

        Args:
            data: The JSON diction to use to build the model.
            **kwargs: Unused but required to match signature of `Schema.make_object`

        Returns:
            An instance of the `__model__` class.

        """
        return self.__model__(**data)


class BaseModel(SimpleNamespace):
    """BaseModel that all models should inherit from.

    Note:
        If a passed parameter is a nested dictionary, then it is created with the
        SimpleNamespace. If it is a list, then it becomes a list of the appropriate
        model.

    Args:
        **kwargs: All passed parameters as converted to instance attributes.
    """

    def __init__(self, **kwargs: Any) -> None:
        kwargs = {k: _process_dict_values(v) for k, v in kwargs.items()}

        self.__dict__.update(kwargs)


class Annotation(BaseModel):  # noqa: D101
    ...


class Note(BaseModel):
    """Google Keep Note model."""

    @property
    def date_and_time(self) -> datetime:
        """Get a datetime object from the unix epoch timestamp.

        Returns:
            A initialized datetime object.

        """
        return datetime.utcfromtimestamp(self.user_edited_timestamp_usec / 1e6)

    @property
    def date_string(self) -> str:
        """Get the date as a string in Roam Daily Note format.

        Returns:
            The datetime as a string.

        """
        return custom_strftime("%B {S}, %Y", self.date_and_time)

    @property
    def time_string(self) -> str:
        """Get the time in standard HH:MM AM/PM format.

        Returns:
            The time as a string.

        """
        return self.date_and_time.strftime("%I:%M %p")

    def is_list(self) -> bool:
        """Check if the note is a checklist.

        Returns:
            The boolean state.

        """
        return hasattr(self, "list_content")

    def is_empty(self) -> bool:
        """Check if the note is empty.

        Returns:
            The boolean state.

        """
        if not self.is_list():
            return cast(bool, self.title == self.text_content == "")
        else:
            return cast(bool, self.title == "" and len(self.list_content) == 0)

    def _text_content_to_bullet(self) -> str:
        # Prepare body string (sub bullet points)
        # Try to convert all unicode characters to ascii
        body = (
            unicodedata.normalize("NFKD", self.text_content)
            .encode("ascii", "ignore")
            .decode()
        )
        # Replace multiple newlines with a single newline
        body = re.sub(r"\n+", "\n", body).strip()
        # Remove all whitespace except newlines and deduplicate spaces
        body = re.compile(r"^\s+|\s+$|[^\S\n\r]+(?=\s)", re.MULTILINE).sub("", body)
        # Prepend newline if body is not empty
        body = f"\n{body}" if body != "" else body
        # Convert all body bullet points into sub-bullets
        # TODO: this could maybe made better to handle lists (sub-sub bullet points!)
        body = body.replace("\n", "\n    - ")

        return body

    def _list_content_to_bullet(self) -> str:
        text_list = [lc.text for lc in self.list_content]

        return "\n    - " + "\n    - ".join(text_list)

    def to_markdown_string(self) -> str:
        """Convert the note to a markdown string.

        Returns:
            A string containing a markdown file.

        """
        # Prepare title string (main bullet point)
        title_str = f"- {self.title or self.time_string}"

        if not self.is_list():
            body = self._text_content_to_bullet()
        else:
            body = self._list_content_to_bullet()

        ret_str = title_str + body
        # Append newline if string does not end in newline
        ret_str = ret_str + "\n" if ret_str[-1] != "\n" else ret_str

        return ret_str


class NoteList(BaseModel):
    """Base class for Lists within notes."""

    ...


class AnnotationSchema(BaseSchema):  # noqa: D101
    __model__ = Annotation

    source = fields.Str()
    url = fields.Str()
    description = fields.Str()
    title = fields.Str()


class NoteListSchema(BaseSchema):  # noqa: D101
    __model__ = NoteList

    text = fields.Str()
    is_checked = fields.Bool()


class NoteSchema(BaseSchema):  # noqa: D101
    __model__ = Note

    is_pinned = fields.Bool()
    title = fields.Str(required=True)
    annotations = fields.List(fields.Nested(AnnotationSchema))
    list_content = fields.List(fields.Nested(NoteListSchema))
    color = fields.Str()
    is_trashed = fields.Bool()
    text_content = fields.Str()
    user_edited_timestamp_usec = fields.Int(required=True)
    is_archived = fields.Bool()

    @validates_schema
    def _check_list_or_text_content(self, data: JSON, **kwargs: Any) -> None:
        if "list_content" not in data and "text_content" not in data:
            raise ValidationError(
                "Either list_content or text_content must be in Note contents."
            )
