import dataclasses
import decimal
import enum
import json
from typing import Any, List, Optional

import strawberry
from strawberry.utils.str_converters import to_camel_case

from .resolver import get_resource_map

try:
    from django.utils.functional import Promise
except ImportError:
    Promise = None


def _fix_data(
    data: Any,
    *,
    key: Optional[str] = None,
    remove_nulls: bool,
    remove_fields_from_types: List[str],
):
    if isinstance(data, dict):
        data = {
            to_camel_case(k): _fix_data(
                v,
                key=k,
                remove_nulls=remove_nulls,
                remove_fields_from_types=remove_fields_from_types,
            )
            for k, v in data.items()
            if (
                (not remove_nulls or v is not None)
                and not (k in {"multiple", "filterable", "orderable"} and not v)
            )
        }

        if "objKind" in data and data.get("objType") in remove_fields_from_types:
            data.pop("fields", None)

        return data
    if isinstance(data, (list, tuple)):
        return (
            {
                i["name"]: _fix_data(
                    i,
                    remove_nulls=remove_nulls,
                    remove_fields_from_types=remove_fields_from_types,
                )
                for i in data
            }
            if key == "fields"
            else [
                _fix_data(
                    v,
                    remove_nulls=remove_nulls,
                    remove_fields_from_types=remove_fields_from_types,
                )
                for v in data
            ]
        )

    return data


class _Encoder(json.JSONEncoder):
    def default(self, o: Any):
        if isinstance(o, decimal.Decimal):
            return str(o)
        if isinstance(o, enum.Enum):
            return o.name
        if Promise is not None and isinstance(o, Promise):
            return str(o)

        return super().default(o)


def to_dict(
    schema: strawberry.Schema,
    *,
    remove_nulls: bool = False,
    remove_nested_types_fields: bool = False,
):
    resource_map = get_resource_map(schema)
    data = {name: dataclasses.asdict(r) for name, r in resource_map.items()}
    remove_types = list(data) if remove_nested_types_fields else []
    return {
        k: _fix_data(
            v, remove_nulls=remove_nulls, remove_fields_from_types=remove_types
        )
        for k, v in data.items()
    }


def to_json(
    schema: strawberry.Schema,
    *,
    remove_nulls: bool = False,
    remove_nested_types_fields: bool = False,
    **kwargs,
):
    data = to_dict(
        schema,
        remove_nulls=remove_nulls,
        remove_nested_types_fields=remove_nested_types_fields,
    )
    return json.dumps(data, cls=_Encoder, **kwargs)
