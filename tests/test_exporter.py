import datetime
import decimal
import enum
import json
import pathlib
from typing import Tuple

import pytest
import strawberry
from strawberry.tools import merge_types

from strawberry_resources.exporter import to_json
from strawberry_resources.queries import Query as _Query


def _check_json(name: str, result: str):
    data_path = pathlib.Path(__file__).parent / "data"
    data_path.mkdir(parents=True, exist_ok=True)
    path = data_path / f"{name}.json"

    if not path.exists():
        with path.open("w") as f:
            # The \n at the end is to avoid pre-commit hooks always modifying those
            f.write(result + "\n")

    with path.open("r") as f:
        assert json.loads(f.read()) == json.loads(result)


@pytest.mark.parametrize(
    "config",
    [
        ("base", False, False),
        ("no_nulls", True, False),
        ("no_duplicated_types", False, True),
        ("no_nulls_no_duplicated_types", True, True),
    ],
)
def test_to_json(config: Tuple[str, bool, bool]):
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
    _check_json(
        config[0],
        to_json(
            schema,
            remove_nulls=config[1],
            remove_nested_types_fields=config[2],
            indent=2,
            sort_keys=True,
        ),
    )
