import contextlib
import dataclasses
import pathlib
from typing import TYPE_CHECKING, Callable, Dict, List, NoReturn, Union

from strawberry.field import StrawberryField

if TYPE_CHECKING:
    from strawberry_resources.types import FieldKind, FieldOrFieldObjectOptions

_integrations_imported: bool = False
integrations: Dict[str, "StrawberryResourceIntegration"] = {}


@dataclasses.dataclass
class StrawberryResourceIntegration:
    name: str
    get_extra_mappings: Callable[[], Dict[type, "FieldKind"]]
    get_field_options: Callable[
        [type, StrawberryField, type, bool],
        Union["FieldOrFieldObjectOptions", NoReturn],
    ]
    ordering: int = 0

    def __post_init__(self):
        integrations[self.name] = self


def get_all() -> List[StrawberryResourceIntegration]:
    global _integrations_imported

    if not _integrations_imported:
        for module in pathlib.Path(__file__).parent.iterdir():
            if (
                not module.is_file()
                or module.name == "__init.py"
                or not module.name.endswith(".py")
            ):
                continue

            with contextlib.suppress(Exception):
                __import__(module.name[:-3], locals(), globals())

        _integrations_imported = True

    return sorted(integrations.values(), key=lambda i: i.ordering)
