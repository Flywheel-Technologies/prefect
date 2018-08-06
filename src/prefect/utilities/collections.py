from collections.abc import MutableMapping
from typing import Any


def merge_dicts(d1: MutableMapping, d2: MutableMapping) -> MutableMapping:
    """
    Updates `d1` from `d2` by replacing each `(k, v1)` pair in `d1` with the
    corresponding `(k, v2)` pair in `d2`.

    If the value of each pair is itself a dict, then the value is updated
    recursively.
    """

    new_dict = d1.copy()

    for k, v in d2.items():
        if isinstance(new_dict.get(k), MutableMapping) and isinstance(
            v, MutableMapping
        ):
            new_dict[k] = merge_dicts(new_dict[k], d2[k])
        else:
            new_dict[k] = d2[k]
    return new_dict


class DotDict(MutableMapping):
    """
    A `dict` that also supports attribute ("dot") access.

    Args:
        - `init_dict` (`dict`, optional): dictionary to initialize the `DotDict`
        with
        - `**kwargs` (optional): key, value pairs with which to initialize the
        `DotDict`

    **Example**:
        ```python
        dotdict = DotDict({'a': 34}, b=56, c=set())
        dotdict.a # 34
        dotdict['b'] # 56
        dotdict.c # set()
        ```
    """

    def __init__(self, init_dict=None, **kwargs):
        if init_dict:
            self.update(init_dict)
        self.update(kwargs)

    def __getitem__(self, key):
        return self.__dict__[key]

    def __setitem__(self, key, value):
        if hasattr(MutableMapping, key):
            raise ValueError("no sir")
        self.__dict__[key] = value

    def __setattr__(self, attr, value):
        self[attr] = value

    def __iter__(self):
        return iter(self.__dict__.keys())

    def __delitem__(self, key):
        del self.__dict__[key]

    def __len__(self):
        return len(self.__dict__)

    def copy(self):
        "Returns a shallow copy"
        return type(self)(self.__dict__.copy())


def to_dotdict(obj: Any) -> DotDict:
    """
    Given a obj formatted as a dictionary, returns an object
    that also supports "dot" access:

    ```
    obj['data']['child']
    obj.data.child
    ```
    """
    if isinstance(obj, (list, tuple, set)):
        return type(obj)([to_dotdict(d) for d in obj])
    elif isinstance(obj, dict):
        return DotDict({k: to_dotdict(v) for k, v in obj.items()})
    return obj


class CompoundKey(tuple):
    pass


def dict_to_flatdict(dct: dict, parent: CompoundKey = None) -> dict:
    """Converts a (nested) dictionary to a flattened representation.

    Each key
    of the flat dict will be a CompoundKey tuple containing the "chain of keys"
    for the corresponding value.

    Args:
        - `dct` (`dict`): The dictionary to flatten
        - `parent` (`CompoundKey`, optional): Defaults to `None`. The parent key
        (you shouldn't need to set this)

    """

    items = []
    parent = parent or CompoundKey()
    for k, v in dct.items():
        k_parent = CompoundKey(parent + (k,))
        if isinstance(v, dict):
            items.extend(dict_to_flatdict(v, parent=k_parent).items())
        else:
            items.append((k_parent, v))
    return dict(items)


def flatdict_to_dict(dct: dict, dct_class: type = None) -> MutableMapping:
    """Converts a flattened dictionary back to a nested dictionary.

    Args:
        - `dct` (`dict`): The dictionary to be nested. Each key should be a
        `CompoundKey`, as generated by `dict_to_flatdict()`

    """

    result = (dct_class or dict)()
    for k, v in dct.items():
        if isinstance(k, CompoundKey):
            current_dict = result
            for ki in k[:-1]:
                current_dict = current_dict.setdefault(ki, (dct_class or dict)())
            current_dict[k[-1]] = v
        else:
            result[k] = v

    return result
