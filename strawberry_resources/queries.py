from typing import List, Optional

import strawberry
from strawberry.types.info import Info

from .resolver import get_resource_by_name, get_resource_map
from .types import Resource


@strawberry.type
class Query:
    @strawberry.field
    def resources(self, info: Info, name: str) -> List[Resource]:
        """Retrieve all resources in the schema."""
        return list(get_resource_map(info.schema).values())

    @strawberry.field
    def resource(self, info: Info, name: str) -> Optional[Resource]:
        """Retrieve the schema settings for the given resource."""
        return get_resource_by_name(info.schema, name)
