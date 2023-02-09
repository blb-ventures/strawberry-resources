import datetime
import decimal

import strawberry
from typing_extensions import Annotated

from strawberry_resources.resolver import get_resource_by_name
from strawberry_resources.types import (
    DecimalFieldValidation,
    Field,
    FieldKind,
    FieldObject,
    FieldObjectKind,
    Hidden,
    Resource,
    config,
)


def test_resource():
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

    @strawberry.type
    class Query:
        some_type: SomeType

    schema = strawberry.Schema(query=Query)

    expected = Resource(
        name="SomeType",
        fields=[
            Field(
                name="idField",
                kind=FieldKind.ID,
                label="id_field",
            ),
            Field(
                name="strField",
                kind=FieldKind.STRING,
                label="str_field",
            ),
            Field(
                name="intField",
                kind=FieldKind.INT,
                label="int_field",
            ),
            Field(
                name="floatField",
                kind=FieldKind.FLOAT,
                label="float_field",
            ),
            Field(
                name="decimalField",
                kind=FieldKind.DECIMAL,
                label="decimal_field",
            ),
            Field(
                name="dateField",
                kind=FieldKind.DATE,
                label="date_field",
            ),
            Field(
                name="datetimeField",
                kind=FieldKind.DATETIME,
                label="datetime_field",
            ),
            Field(
                name="timeField",
                kind=FieldKind.TIME,
                label="time_field",
            ),
        ],
    )

    resource = get_resource_by_name(schema, "SomeType")
    assert resource == expected
    assert get_resource_by_name(schema, "Query") == Resource(
        name="Query",
        fields=[
            FieldObject(
                name="someType",
                label="some_type",
                obj_kind=FieldObjectKind.OBJECT,
                fields=expected.fields,
            ),
        ],
    )


def test_resourcea_with_annotations():
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
        hidden_field: Hidden[int]

    @strawberry.type
    class Query:
        some_type: SomeType

    schema = strawberry.Schema(query=Query)

    expected = Resource(
        name="SomeType",
        fields=[
            Field(
                name="idField",
                kind=FieldKind.ID,
                label="id_field",
            ),
            Field(
                name="strField",
                kind=FieldKind.STRING,
                label="Str Field",
            ),
            Field(
                name="percentField",
                kind=FieldKind.PERCENT,
                label="Percent Field",
                validation=DecimalFieldValidation(
                    min_value=0,
                    max_value=1,
                ),
            ),
        ],
    )

    resource = get_resource_by_name(schema, "SomeType")
    assert resource == expected
    assert get_resource_by_name(schema, "Query") == Resource(
        name="Query",
        fields=[
            FieldObject(
                name="someType",
                label="some_type",
                obj_kind=FieldObjectKind.OBJECT,
                fields=expected.fields,
            ),
        ],
    )
