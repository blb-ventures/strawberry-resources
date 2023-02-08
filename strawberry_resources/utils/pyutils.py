from typing import Mapping, TypeVar, Union, cast

_T1 = TypeVar("_T1", bound=Mapping)
_T2 = TypeVar("_T2", bound=Mapping)


def dict_merge(dict1: _T1, dict2: _T2) -> Union[_T1, _T2]:
    new = {
        **dict1,
        **dict2,
    }

    for k, v1 in dict1.items():
        if not isinstance(v1, dict):
            continue

        v2 = dict2.get(k)
        if isinstance(v2, Mapping):
            new[k] = dict_merge(v1, v2)

    for k, v2 in dict2.items():
        if not isinstance(v2, dict):
            continue

        v1 = dict1.get(k)
        if isinstance(v1, Mapping):
            new[k] = dict_merge(v1, v2)

    return cast(Union[_T1, _T2], new)
