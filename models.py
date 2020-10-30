import re
import unicodedata
from datetime import datetime
from typing import Any, Dict, Mapping
from types import SimpleNamespace
from marshmallow import Schema, fields, post_load, EXCLUDE

JSON = Dict[str, Any]


def _process_dict_values(value: Any) -> Any:
    """Process a returned from a JSON response.

    Args:
        value: A dict, list, or value returned from a JSON response.

    Returns:
        Either an UnknownModel, a List of processed values, or the original value \
            passed through.

    """
    if isinstance(value, Mapping):
        return SimpleNamespace(**value)
    elif isinstance(value, list):
        return [_process_dict_values(v) for v in value]
    else:
        return value


def camelcase(s):
    parts = iter(s.split("_"))
    return next(parts) + "".join(i.title() for i in parts)


def suffix(d):
    return 'th' if 11 <= d <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(d % 10, 'th')


def custom_strftime(fmt, t):
    return t.strftime(fmt).replace('{S}', str(t.day) + suffix(t.day))


class BaseSchema(Schema):
    """Schema that uses camel-case for its external representation
    and snake-case for its internal representation.
    """

    __model__: Any = SimpleNamespace
    """Determine the object that is created when the load method is called."""

    class Meta:
        unknown = EXCLUDE

    def on_bind_field(self, field_name, field_obj):
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
        `UnknownModel` class. If it is a list, then it is created with

    Args:
        **kwargs: All passed parameters as converted to instance attributes.
    """

    def __init__(self, **kwargs: Any) -> None:
        kwargs = {k: _process_dict_values(v) for k, v in kwargs.items()}

        self.__dict__.update(kwargs)


class Annotation(BaseModel):
    ...


class Note(BaseModel):

    @property
    def date_and_time(self):
        return datetime.fromtimestamp(self.user_edited_timestamp_usec / 1e6)

    @property
    def date_string(self):
        # https://stackoverflow.com/a/5891598/3262054
        return custom_strftime("%B {S}, %Y", self.date_and_time)

    @property
    def time_string(self):
        return self.date_and_time.strftime("%I:%M %p")

    def is_list(self):
        return hasattr(self, "list_content")

    def is_empty(self):
        if not self.is_list():
            return self.title == self.text_content == ""
        else:
            return self.title == "" and len(self.list_content) == 0

    def _text_content_to_bullet(self):
        # Prepare body string (sub bullet points)
        # Try to convert all unicode characters to ascii
        body = unicodedata.normalize('NFKD', self.text_content).encode(
            'ascii', 'ignore'
        ).decode()
        # Replace multiple newlines with a single newline
        body = re.sub(r'\n+', '\n', body).strip()
        # Remove all whitespace except newlines and deduplicate spaces
        body = re.compile(r"^\s+|\s+$|[^\S\n\r]+(?=\s)", re.MULTILINE).sub('', body)
        # Prepend newline if body is not empty
        body = f"\n{body}" if body != "" else body
        # Convert all body bullet points into sub-bullets
        # TODO: this could maybe made better to handle lists (sub-sub bullet points!)
        body = body.replace('\n', '\n    - ')

        return body

    def _list_content_to_bullet(self):
        text_list = [lc.text for lc in self.list_content]

        return '\n    - ' + '\n    - '.join(text_list)

    def to_markdown_string(self):
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


class List_(BaseModel):
    ...


class AnnotationSchema(BaseSchema):
    __model__ = Annotation

    source = fields.Str()
    url = fields.Str()
    description = fields.Str()
    title = fields.Str()


class ListSchema(BaseSchema):
    __model__ = List_

    text = fields.Str()
    is_checked = fields.Bool()


class NoteSchema(BaseSchema):
    __model__ = Note

    is_pinned = fields.Bool()
    title = fields.Str()
    annotations = fields.List(fields.Nested(AnnotationSchema))
    list_content = fields.List(fields.Nested(ListSchema))
    color = fields.Str()
    is_trashed = fields.Bool()
    text_content = fields.Str()
    user_edited_timestamp_usec = fields.Int()
    is_archived = fields.Bool()
