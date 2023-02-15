import dataclasses
import enum
from typing import (
    Any,
    List,
    Optional,
    TypedDict,
    TypeVar,
    Union,
)

import strawberry
from django.db import models
from strawberry.scalars import JSON
from typing_extensions import Annotated, TypeAlias, Unpack

_R = TypeVar("_R")
_T = TypeVar("_T", bound=type)
_M = TypeVar("_M", bound=models.Model)


@strawberry.type
class Resource:
    name: str
    fields: List["ResourceField"] = strawberry.field(default_factory=list)

    def __hash__(self):
        return hash(self.name)


@strawberry.enum
class FieldKind(enum.Enum):
    """The proper field kind.

    This is useful to differentiate the kind of the field from its
    scalar value. E.g. A "String" scalar might be a `POSTAL_CODE`, a
    `PASSWORD`, etc.
    """

    BOOLEAN = "boolean"
    CURRENCY = "currency"
    DATE = "date"
    DATETIME = "datetime"
    TIMEDELTA = "timedelta"
    DECIMAL = "decimal"
    EMAIL = "email"
    FILE = "file"
    IMAGE = "image"
    FLOAT = "float"
    ID = "id"
    IP = "IP"
    INT = "int"
    JSON = "json"
    LEGAL_PERSON_DOC = "legal-person-doc"
    NATURAL_PERSON_DOC = "natural-person-doc"
    PASSWORD = "password"
    PERCENT = "percent"
    PHONE = "phone"
    POSTAL_CODE = "postal-code"
    STRING = "string"
    STRING_LIST = "string-list"
    MULTILINE = "multiline"
    TIME = "time"
    URL = "url"
    UUID = "uuid"
    POINT = "point"
    GEOPOINT = "geopoint"
    POLYGON = "polygon"
    DISTANCE = "distance"


@strawberry.enum
class FieldObjectKind(enum.Enum):
    """The kind of the nested object.

    The options here are:
        OBJECT:
            A nested type containing the given fields (e.g. `{"foo": "bar", "baz", 123}`)
        OBJECT_LIST:
            A nested list of types containing the given fields
            (e.g. `[{"foo": "bar", "baz", 123}, ...]`)
        INPUT:
            A nested input expecting the given fields (e.g. `{"foo": "bar", "baz", 123}`)
        INPUT_LIST:
            A nested list of inputs expecting the given fields
            (e.g. `[{"foo": "bar", "baz", 123}, ...]`)
        LIST_INPUT:
            A nested `ListInput` type, containing its usual `set`/`add`/`remove` options,
            each expecting a list of the given inputs
            (e.g. `{"set": [{{"foo": "bar", "baz", 123}, ...}]}`).
    """

    OBJECT = "object"
    OBJECT_LIST = "object-list"
    INPUT = "input"
    INPUT_LIST = "input-list"
    LIST_INPUT = "list-input"


@strawberry.type
class BaseFieldValidation:
    """Field validation values."""

    required: bool = strawberry.field(
        description="If this field is required.",
        default=True,
    )


@strawberry.type
class StringFieldValidation(BaseFieldValidation):
    """Field validation for string values."""

    min_length: Optional[int] = strawberry.field(
        description="Min length for the string.",
        default=None,
    )
    max_length: Optional[int] = strawberry.field(
        description="Max length for the string.",
        default=None,
    )


@strawberry.type
class IntFieldValidation(BaseFieldValidation):
    """Field validation for integer values."""

    min_value: Optional[int] = strawberry.field(
        description="Min value for the number.",
        default=None,
    )
    max_value: Optional[int] = strawberry.field(
        description="Max value for the number.",
        default=None,
    )


@strawberry.type
class DecimalFieldValidation(IntFieldValidation):
    """Field validation for decimal values."""

    max_digits: Optional[int] = strawberry.field(
        description="Max digits allowed. Note: This include the decimal places.",
        default=None,
    )
    decimal_places: Optional[int] = strawberry.field(
        description="Decimal places allowed",
        default=None,
    )


FieldValidation: TypeAlias = strawberry.union(  # type: ignore
    "FieldValidation",
    (BaseFieldValidation, StringFieldValidation, IntFieldValidation, DecimalFieldValidation),
)


@strawberry.type
class FieldChoice:
    """A valid choice for the field."""

    label: str
    value: JSON
    group: Optional[str] = None


@strawberry.type
class Field:
    """Base field schema."""

    name: str = strawberry.field(
        description="The name of the field.",
    )
    kind: FieldKind = strawberry.field(
        description="The kind of the field.",
    )
    label: str = strawberry.field(
        description="The field's humanized name",
    )
    multiple: bool = strawberry.field(
        description="If this field expects an array of values.",
        default=False,
    )
    orderable: bool = strawberry.field(
        description="If this field is orderable.",
        default=False,
    )
    filterable: bool = strawberry.field(
        description="If this field is filterable.",
        default=False,
    )
    help_text: Optional[str] = strawberry.field(
        description="A help text for the field.",
        default=None,
    )
    choices: Optional[List[FieldChoice]] = strawberry.field(
        description="Valid choices for this field, if any is defined.",
        default=None,
    )
    default_value: Optional[JSON] = strawberry.field(
        description="Default value for the field. Parse the json to get its value.",
        default=None,
    )
    validation: FieldValidation = strawberry.field(
        description="Validation options for this field",
        default_factory=BaseFieldValidation,
    )
    resource: Optional[str] = strawberry.field(
        description="The resource that this field is linked to",
        default=None,
    )


@strawberry.type
class FieldObject:
    """Base field list schema."""

    name: str = strawberry.field(
        description="The name of the field.",
    )
    label: str = strawberry.field(
        description="The field's humanized name",
    )
    obj_kind: FieldObjectKind = strawberry.field(
        description="The kind of the field.",
    )
    obj_type: str = strawberry.field(
        description="The obj type name.",
    )
    fields: List["ResourceField"] = strawberry.field(
        description="All subfields of this field.",
    )


ResourceField: TypeAlias = strawberry.union("ResourceField", (Field, FieldObject))  # type: ignore


class FieldOptions(TypedDict, total=False):
    kind: FieldKind
    multiple: bool
    orderable: bool
    filterable: bool
    label: str
    resource: Optional[str]
    help_text: Optional[str]
    choices: Optional[List[FieldChoice]]
    default_value: Any
    validation: FieldValidation


class FieldObjectOptions(TypedDict, total=False):
    label: str
    obj_kind: FieldObjectKind


FieldOrFieldObjectOptions: TypeAlias = Union[FieldOptions, FieldObjectOptions]


@dataclasses.dataclass
class FieldOptionsConfig:
    options: FieldOptions

    def __hash__(self):
        return hash((self.__class__, frozenset(self.options.items())))


class HiddenFieldError(Exception):
    ...


class HiddenField:
    ...


Hidden = Annotated[_R, HiddenField()]


def config(**options: Unpack[FieldOptions]):
    """Override options for a field."""
    return FieldOptionsConfig(options=options)
