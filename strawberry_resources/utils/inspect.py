import itertools
from typing import Generator, Optional, Union

from strawberry.lazy_type import LazyType
from strawberry.type import (
    StrawberryContainer,
    StrawberryType,
    StrawberryTypeVar,
    get_object_definition,
)
from strawberry.types.types import StrawberryObjectDefinition
from strawberry.union import StrawberryUnion
from typing_extensions import assert_never


def get_possible_types(
    gql_type: Union[StrawberryObjectDefinition, StrawberryType, type],
    *,
    object_definition: Optional[StrawberryObjectDefinition] = None,
) -> Generator[type, None, None]:
    if isinstance(gql_type, StrawberryObjectDefinition):
        yield from get_possible_types(gql_type.origin, object_definition=gql_type)
    elif isinstance(gql_type, LazyType):
        yield from get_possible_types(gql_type.resolve_type())
    elif isinstance(gql_type, StrawberryTypeVar) and object_definition is not None:
        resolved = object_definition.type_var_map.get(gql_type.type_var, None)
        if resolved is not None:
            yield from get_possible_types(resolved)
    elif isinstance(gql_type, StrawberryContainer):
        yield from get_possible_types(gql_type.of_type)
    elif isinstance(gql_type, StrawberryUnion):
        yield from itertools.chain.from_iterable(
            (get_possible_types(t) for t in gql_type.types),
        )
    elif isinstance(gql_type, StrawberryType):
        # Nothing to return here
        pass
    elif isinstance(gql_type, type):
        yield gql_type
    else:
        assert_never(gql_type)


def get_possible_type_definitions(
    gql_type: Union[StrawberryObjectDefinition, StrawberryType, type],
) -> Generator[StrawberryObjectDefinition, None, None]:
    if isinstance(gql_type, StrawberryObjectDefinition):
        yield gql_type
        return

    for t in get_possible_types(gql_type):
        if isinstance(t, StrawberryObjectDefinition):
            yield t
        elif (type_def := get_object_definition(t)) is not None:
            yield type_def
