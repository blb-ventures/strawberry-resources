import datetime
import decimal
import uuid
from typing import (
    Dict,
    Optional,
    Tuple,
    TypeVar,
    cast,
)

import strawberry
from django.db import models
from strawberry import Schema
from strawberry.custom_scalar import ScalarWrapper
from strawberry.enum import EnumDefinition
from strawberry.file_uploads import Upload
from strawberry.lazy_type import LazyType
from strawberry.scalars import JSON
from strawberry.type import StrawberryContainer, StrawberryList, StrawberryOptional
from strawberry.types.types import TypeDefinition
from strawberry.utils.str_converters import to_camel_case
from typing_extensions import Annotated, TypeAlias, get_args, get_origin

from strawberry_resources.integrations.base import get_all
from strawberry_resources.utils.inspect import get_possible_type_definitions
from strawberry_resources.utils.pyutils import dict_merge

from .types import (
    BaseFieldValidation,
    Field,
    FieldChoice,
    FieldKind,
    FieldObject,
    FieldObjectKind,
    FieldOptions,
    FieldOptionsConfig,
    FieldOrFieldObjectOptions,
    HiddenField,
    HiddenFieldError,
    Resource,
)

_R = TypeVar("_R")
_T = TypeVar("_T", bound=type)
_M = TypeVar("_M", bound=models.Model)
_TypeMap: TypeAlias = Dict[str, Resource]

MAX_DEPTH = 5
type_name_map: Dict[Schema, Optional[_TypeMap]] = {}
field_type_map: Dict[type, FieldKind] = {
    bool: FieldKind.BOOLEAN,
    str: FieldKind.STRING,
    int: FieldKind.INT,
    float: FieldKind.FLOAT,
    datetime.date: FieldKind.DATE,
    datetime.time: FieldKind.TIME,
    datetime.datetime: FieldKind.DATETIME,
    datetime.timedelta: FieldKind.TIMEDELTA,
    decimal.Decimal: FieldKind.DECIMAL,
    uuid.UUID: FieldKind.UUID,
    strawberry.ID: FieldKind.ID,
    Upload.wrap: FieldKind.FILE,  # type: ignore
}


def get_resource_map(schema: "Schema") -> _TypeMap:
    if (type_map := type_name_map.get(schema)) is None:
        type_map = {}

        for resource in resolve_all(schema):
            type_map[resource.name] = resource

        type_name_map[schema] = type_map

    return type_map


def get_resource_by_name(schema: "Schema", name: str) -> Optional[Resource]:
    return get_resource_map(schema).get(name)


def resolve_all(schema: Schema):
    seen: set[str] = set()

    for _name, type_ in schema.schema_converter.type_map.items():
        for type_def in get_possible_type_definitions(type_.definition):
            if type_def.name in seen:
                continue

            yield Resource(
                name=type_def.name,
                fields=list(resolve_fields_for_type(type_def.origin)),
            )
            seen.add(type_def.name)


def resolve_fields_for_type(type_: type, *, depth: int = 0):
    type_def = cast(TypeDefinition, type_._type_definition)  # type: ignore  # noqa: SLF001
    integrations = get_all()

    for field in type_def.fields:
        cname = field.graphql_name or to_camel_case(field.name)
        hidden = False
        options: FieldOrFieldObjectOptions = {
            "label": field.name,
            "validation": BaseFieldValidation(
                required=not isinstance(field.type, StrawberryOptional),
            ),
        }

        f_type = field.type
        if get_origin(f_type) is Annotated:
            f_type, *extras = get_args(f_type)
        else:
            extras = []

        # If this was annotated with Hidden, do not expose it in the resource
        if any(isinstance(extra, HiddenField) for extra in extras):
            continue

        is_list: bool = False
        while isinstance(f_type, StrawberryContainer):
            is_list = is_list or isinstance(f_type, StrawberryList)
            f_type = f_type.of_type

        if isinstance(f_type, LazyType):
            f_type = f_type.resolve_type()
        if isinstance(f_type, EnumDefinition):
            if all(isinstance(v.value, int) for v in f_type.values):
                options["kind"] = FieldKind.INT
            elif all(isinstance(v.value, str) for v in f_type.values):
                options["kind"] = FieldKind.STRING
            else:
                # FIXME: Are there other possibilities other than int or string?
                options["kind"] = FieldKind.STRING

            options["choices"] = [
                FieldChoice(
                    label=value.description or value.name,
                    value=cast(JSON, value.name),
                )
                for value in f_type.values
            ]
            f_type = f_type.wrapped_cls
        if isinstance(f_type, ScalarWrapper):
            f_type = f_type.wrap

        type_map = field_type_map.copy()
        for integration in integrations:
            type_map.update(integration.get_extra_mappings())
            try:
                options = dict_merge(
                    options,
                    integration.get_field_options(
                        type_,
                        field,
                        cast(type, f_type),
                        is_list,
                    ),
                )
            except HiddenFieldError:
                hidden = True
                break

        if (f_kind := field_type_map.get(cast(type, f_type))) is not None:
            options["kind"] = f_kind  # type: ignore

        annotations = {}
        for o in reversed(type_def.origin.__mro__):
            annotations.update(getattr(o, "__annotations__", {}))

        # Override those options with the field options
        if (
            (annotation := annotations.get(field.name)) and get_origin(annotation) is Annotated
        ) or (
            (resolver := getattr(type_def.origin, field.name, None))
            and hasattr(resolver, "__annotations__")
            and get_origin(annotation := resolver.__annotations__.get("return")) is Annotated
        ):
            for opt in get_args(annotation)[1:]:
                if isinstance(opt, HiddenField):
                    hidden = True
                    break

                if not isinstance(opt, FieldOptionsConfig):
                    continue

                options = dict_merge(options, opt.options)

        if hidden:
            continue

        # If this is another type, we should return a FieldObject instead
        if "obj_kind" in options or hasattr(f_type, "_type_definition"):
            if depth > MAX_DEPTH:
                continue

            inner_type_def = cast(
                TypeDefinition,
                f_type._type_definition,  # type: ignore  # noqa: SLF001
            )

            assert isinstance(f_type, type)
            obj_kind = options.get("obj_kind")
            if obj_kind is None:
                obj_kind_map: Dict[Tuple[bool, bool], FieldObjectKind] = {
                    (False, False): FieldObjectKind.OBJECT,
                    (True, False): FieldObjectKind.OBJECT_LIST,
                    (True, True): FieldObjectKind.INPUT_LIST,
                    (False, True): FieldObjectKind.INPUT,
                }
                obj_kind = obj_kind_map[(is_list, getattr(inner_type_def, "is_input", False))]

            yield FieldObject(
                name=cname,
                label=options.get("label", field.name),
                obj_kind=obj_kind,
                obj_type=inner_type_def.name,
                fields=list(resolve_fields_for_type(f_type, depth=depth + 1)),
            )
        else:
            options = cast(FieldOptions, options)

            # FIXME: How to improve this?
            if "kind" not in options:
                continue

            yield Field(name=cname, **options)
