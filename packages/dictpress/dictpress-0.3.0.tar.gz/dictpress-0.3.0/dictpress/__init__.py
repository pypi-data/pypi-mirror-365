import pathlib
import typing

__version__ = pathlib.Path(__file__).parent.joinpath("VERSION").read_text().strip()
__all__ = ["flatten_dict", "unflatten_dict", "merge", "get_deep", "set_deep"]


def flatten_dict(data: dict, *, parent_key: str = "", sep: str = ".") -> dict:
    """
    Flatten a nested dictionary into a single-level dict.
    Keys are joined with dots (e.g., 'a.b.c' for nested['a']['b']['c']).
    Dictionaries with any non-string keys are treated as leaf values and not flattened.
    """
    items = {}
    for k, v in data.items():
        if isinstance(k, str):
            new_key = parent_key + sep + k if parent_key else k
            if (
                isinstance(v, dict)
                and v
                and all(isinstance(sk, str) for sk in v.keys())
            ):
                items.update(flatten_dict(v, parent_key=new_key, sep=sep))
            else:
                items[new_key] = v
        else:
            items[k] = v
    return items


def unflatten_dict(data: dict, *, sep: str = ".") -> dict:
    """
    Convert a flattened dictionary back to its original nested structure.
    Reverses the operation performed by flatten_dict().
    Non-string keys are restored as-is.
    """
    result = {}
    for key, value in data.items():
        if not isinstance(key, str):
            result[key] = value
            continue
        parts = key.split(sep)
        d = result
        for i, part in enumerate(parts):
            if i == len(parts) - 1:
                d[part] = value
            else:
                if part not in d or not isinstance(d.get(part), dict):
                    d[part] = {}
                d = d[part]
    return result


def merge(data: dict, update: dict) -> dict:
    """
    Merge two dictionaries with deep merging support.
    Values from 'update' take precedence over 'data' for conflicting keys.
    """
    out = flatten_dict(data)
    out.update(flatten_dict(update))
    return unflatten_dict(out)


def get_deep(
    data: dict,
    key: str,
    default: typing.Any | None = None,
    *,
    case_sensitive: bool = True,
) -> typing.Any | None:
    """
    Get a value from nested dictionary using dot notation or suffix matching.
    Searches for exact key match or keys ending with '.{key}'.
    Returns the found value or default if not found.
    """
    flattened = flatten_dict(data)

    for k, v in flattened.items():
        if not isinstance(k, str):
            continue
        if k == key:
            return v
        if k.endswith(f".{key}"):
            return v

    if not case_sensitive:
        key_lower = key.lower()
        for k, v in flattened.items():
            if not isinstance(k, str):
                continue
            k_lower = k.lower()
            if k_lower == key_lower:
                return v
            if k_lower.endswith(f".{key_lower}"):
                return v
    return default


def set_deep(
    data: dict, key: str, value: typing.Any
) -> dict:  # key is a dot-separated path, return new dict
    """
    Set a value in nested dictionary using dot-separated path notation.
    Creates a new dictionary with the specified value at the given path.
    Does not modify the original dictionary.
    """

    updater = {key: value}
    return merge(data, updater)
