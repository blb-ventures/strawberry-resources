import datetime
import decimal
import enum

import strawberry
from strawberry.tools import merge_types
from strawberry_django.filters import Optional
from typing_extensions import Annotated

from strawberry_resources.queries import Query as _Query
from strawberry_resources.types import (
    DecimalFieldValidation,
    FieldKind,
    Hidden,
    config,
)

from .utils import resource_query


def test_query():
    @strawberry.enum
    class SomeEnum(enum.Enum):
        FOO = "foo"
        BAR = strawberry.enum_value("bar", description="Bar")

    @strawberry.type
    class SomeType:
        id_field: strawberry.ID
        str_field: str
        int_field: int
        float_field: float
        decimal_field: decimal.Decimal
        date_field: datetime.date
        datetime_field: datetime.datetime
        time_field: datetime.time
        some_enum: SomeEnum

    @strawberry.type
    class Query:
        some_type: SomeType

    schema = strawberry.Schema(
        query=merge_types(
            "Query",
            (
                _Query,
                Query,
            ),
        ),
    )

    res = schema.execute_sync(resource_query, {"name": "SomeType"})
    assert res.errors is None
    assert res.data == {
        "resource": {
            "fields": [
                {
                    "__typename": "Field",
                    "choices": None,
                    "defaultValue": None,
                    "filterable": False,
                    "helpText": None,
                    "kind": "ID",
                    "label": "id_field",
                    "multiple": False,
                    "name": "idField",
                    "orderable": False,
                    "resource": None,
                    "validation": {"__typename": "BaseFieldValidation", "required": True},
                },
                {
                    "__typename": "Field",
                    "choices": None,
                    "defaultValue": None,
                    "filterable": False,
                    "helpText": None,
                    "kind": "STRING",
                    "label": "str_field",
                    "multiple": False,
                    "name": "strField",
                    "orderable": False,
                    "resource": None,
                    "validation": {"__typename": "BaseFieldValidation", "required": True},
                },
                {
                    "__typename": "Field",
                    "choices": None,
                    "defaultValue": None,
                    "filterable": False,
                    "helpText": None,
                    "kind": "INT",
                    "label": "int_field",
                    "multiple": False,
                    "name": "intField",
                    "orderable": False,
                    "resource": None,
                    "validation": {"__typename": "BaseFieldValidation", "required": True},
                },
                {
                    "__typename": "Field",
                    "choices": None,
                    "defaultValue": None,
                    "filterable": False,
                    "helpText": None,
                    "kind": "FLOAT",
                    "label": "float_field",
                    "multiple": False,
                    "name": "floatField",
                    "orderable": False,
                    "resource": None,
                    "validation": {"__typename": "BaseFieldValidation", "required": True},
                },
                {
                    "__typename": "Field",
                    "choices": None,
                    "defaultValue": None,
                    "filterable": False,
                    "helpText": None,
                    "kind": "DECIMAL",
                    "label": "decimal_field",
                    "multiple": False,
                    "name": "decimalField",
                    "orderable": False,
                    "resource": None,
                    "validation": {"__typename": "BaseFieldValidation", "required": True},
                },
                {
                    "__typename": "Field",
                    "choices": None,
                    "defaultValue": None,
                    "filterable": False,
                    "helpText": None,
                    "kind": "DATE",
                    "label": "date_field",
                    "multiple": False,
                    "name": "dateField",
                    "orderable": False,
                    "resource": None,
                    "validation": {"__typename": "BaseFieldValidation", "required": True},
                },
                {
                    "__typename": "Field",
                    "choices": None,
                    "defaultValue": None,
                    "filterable": False,
                    "helpText": None,
                    "kind": "DATETIME",
                    "label": "datetime_field",
                    "multiple": False,
                    "name": "datetimeField",
                    "orderable": False,
                    "resource": None,
                    "validation": {"__typename": "BaseFieldValidation", "required": True},
                },
                {
                    "__typename": "Field",
                    "choices": None,
                    "defaultValue": None,
                    "filterable": False,
                    "helpText": None,
                    "kind": "TIME",
                    "label": "time_field",
                    "multiple": False,
                    "name": "timeField",
                    "orderable": False,
                    "resource": None,
                    "validation": {"__typename": "BaseFieldValidation", "required": True},
                },
                {
                    "__typename": "Field",
                    "choices": [
                        {"group": None, "label": "FOO", "value": "FOO"},
                        {"group": None, "label": "Bar", "value": "BAR"},
                    ],
                    "defaultValue": None,
                    "filterable": False,
                    "helpText": None,
                    "kind": "STRING",
                    "label": "some_enum",
                    "multiple": False,
                    "name": "someEnum",
                    "orderable": False,
                    "resource": None,
                    "validation": {"__typename": "BaseFieldValidation", "required": True},
                },
            ],
            "name": "SomeType",
        },
    }


def test_query_with_annotations():
    @strawberry.enum
    class SomeEnum(enum.Enum):
        FOO = "foo"
        BAR = strawberry.enum_value("bar", description="Bar")

    @strawberry.type
    class SomeType:
        id_field: strawberry.ID
        str_field: Annotated[str, config(label="Str Field")]
        percent_field: Annotated[
            decimal.Decimal,
            config(
                label="Percent Field",
                kind=FieldKind.PERCENT,
                validation=DecimalFieldValidation(min_value=0, max_value=1),
            ),
        ]
        some_enum: Annotated[Optional[SomeEnum], config(default_value=SomeEnum.FOO)]
        hidden_field: Hidden[int]

    @strawberry.type
    class Query:
        some_type: SomeType

    schema = strawberry.Schema(
        query=merge_types(
            "Query",
            (
                _Query,
                Query,
            ),
        ),
    )

    res = schema.execute_sync(resource_query, {"name": "SomeType"})
    assert res.errors is None
    assert res.data == {
        "resource": {
            "fields": [
                {
                    "__typename": "Field",
                    "choices": None,
                    "defaultValue": None,
                    "filterable": False,
                    "helpText": None,
                    "kind": "ID",
                    "label": "id_field",
                    "multiple": False,
                    "name": "idField",
                    "orderable": False,
                    "resource": None,
                    "validation": {"__typename": "BaseFieldValidation", "required": True},
                },
                {
                    "__typename": "Field",
                    "choices": None,
                    "defaultValue": None,
                    "filterable": False,
                    "helpText": None,
                    "kind": "STRING",
                    "label": "Str Field",
                    "multiple": False,
                    "name": "strField",
                    "orderable": False,
                    "resource": None,
                    "validation": {"__typename": "BaseFieldValidation", "required": True},
                },
                {
                    "__typename": "Field",
                    "choices": None,
                    "defaultValue": None,
                    "filterable": False,
                    "helpText": None,
                    "kind": "PERCENT",
                    "label": "Percent Field",
                    "multiple": False,
                    "name": "percentField",
                    "orderable": False,
                    "resource": None,
                    "validation": {
                        "__typename": "DecimalFieldValidation",
                        "decimalPlaces": None,
                        "maxDigits": None,
                        "maxValue": 1,
                        "minValue": 0,
                        "required": True,
                    },
                },
                {
                    "__typename": "Field",
                    "choices": [
                        {"group": None, "label": "FOO", "value": "FOO"},
                        {"group": None, "label": "Bar", "value": "BAR"},
                    ],
                    "defaultValue": SomeEnum.FOO,
                    "filterable": False,
                    "helpText": None,
                    "kind": "STRING",
                    "label": "some_enum",
                    "multiple": False,
                    "name": "someEnum",
                    "orderable": False,
                    "resource": None,
                    "validation": {"__typename": "BaseFieldValidation", "required": False},
                },
            ],
            "name": "SomeType",
        },
    }
