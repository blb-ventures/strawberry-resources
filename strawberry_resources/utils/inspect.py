import itertools
from typing import Generator, Optional, Union

from strawberry.lazy_type import LazyType
from strawberry.type import StrawberryContainer, StrawberryType, StrawberryTypeVar
from strawberry.types.types import TypeDefinition
from strawberry.union import StrawberryUnion
from typing_extensions import assert_never


def get_possible_types(
    gql_type: Union[TypeDefinition, StrawberryType, type],
    type_def: Optional[TypeDefinition] = None,
) -> Generator[type, None, None]:
    if isinstance(gql_type, TypeDefinition):
        yield from get_possible_types(gql_type.origin, type_def=gql_type)
    elif isinstance(gql_type, LazyType):
        yield from get_possible_types(gql_type.resolve_type())
    elif isinstance(gql_type, StrawberryTypeVar) and type_def is not None:
        # Try to resolve TypeVar
        for f in type_def.fields:
            f_type = f.type
            if not isinstance(f_type, StrawberryTypeVar):
                continue

            resolved = type_def.type_var_map.get(f_type.type_var, None)
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
    gql_type: Union[TypeDefinition, StrawberryType, type],
) -> Generator[TypeDefinition, None, None]:
    if isinstance(gql_type, TypeDefinition):
        yield gql_type
        return

    for t in get_possible_types(gql_type):
        if isinstance(t, TypeDefinition):
            yield t
        elif hasattr(t, "_type_definition"):
            yield t._type_definition  # type: ignore  # noqa: SLF001
