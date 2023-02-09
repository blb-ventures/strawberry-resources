import dataclasses
import decimal
import enum
import json
from typing import Any, Optional

import strawberry
from strawberry.utils.str_converters import to_camel_case

from .resolver import get_resource_map

try:
    from django.utils.functional import Promise
except ImportError:
    Promise = None


def _remove_nulls(data: Any, key: Optional[str] = None):
    if isinstance(data, dict):
        return {
            to_camel_case(k): _remove_nulls(v, key=k)
            for k, v in data.items()
            if v is not None and not (k in ["multiple", "filterable", "orderable"] and not v)
        }
    if isinstance(data, (list, tuple)):
        return (
            {i["name"]: _remove_nulls(i) for i in data}
            if key == "fields"
            else [_remove_nulls(v) for v in data]
        )

    return data


class _Encoder(json.JSONEncoder):
    def default(self, obj: Any):
        if isinstance(obj, decimal.Decimal):
            return str(obj)
        if isinstance(obj, enum.Enum):
            return obj.name
        if Promise is not None and isinstance(obj, Promise):
            return str(obj)

        return super().default(obj)


def to_dict(schema: strawberry.Schema, *, remove_nulls: bool = False):
    resource_map = get_resource_map(schema)
    data = {name: dataclasses.asdict(r) for name, r in resource_map.items()}
    if remove_nulls:
        data = {k: _remove_nulls(v) for k, v in data.items()}

    return data


def to_json(schema: strawberry.Schema, *, remove_nulls: bool = False, **kwargs):
    data = to_dict(schema, remove_nulls=remove_nulls)
    return json.dumps(data, cls=_Encoder, **kwargs)
