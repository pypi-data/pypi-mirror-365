# dictpress

Simple dictionary manipulation utilities for Python.

**Repository:** <https://github.com/allen2c/dictpress>
**PyPI:** <https://pypi.org/project/dictpress/>

## Installation

```bash
pip install dictpress
```

## Usage

```python
from dictpress import flatten_dict, unflatten_dict, merge, get_deep, set_deep

# Flatten nested dictionaries
data = {"a": {"b": {"c": 1}}, "x": 2}
flattened = flatten_dict(data)
# {"a.b.c": 1, "x": 2}

# Unflatten back to nested structure
nested = unflatten_dict(flattened)
# {"a": {"b": {"c": 1}}, "x": 2}

# Deep merge dictionaries
base = {"a": {"b": 1}, "c": 2}
update = {"a": {"d": 3}, "e": 4}
merged = merge(base, update)
# {"a": {"b": 1, "d": 3}, "c": 2, "e": 4}

# Get values from nested dictionaries
data = {"user": {"profile": {"name": "Alice", "age": 30}}}
name = get_deep(data, "name")  # "Alice" (suffix match)
age = get_deep(data, "user.profile.age")  # 30 (exact match)
missing = get_deep(data, "missing", "default")  # "default"

# Set values in nested dictionaries
data = {"a": 1}
result = set_deep(data, "user.name", "Bob")
# {"a": 1, "user": {"name": "Bob"}}
```

## API

### `flatten_dict(data: dict) -> dict`

Flatten nested dictionary into single-level with dot notation keys.

### `unflatten_dict(data: dict) -> dict`

Convert flattened dictionary back to nested structure.

### `merge(data: dict, update: dict) -> dict`

Deep merge two dictionaries. Values from `update` take precedence.

### `get_deep(data: dict, key: str, default=None) -> Any`

Get value from nested dictionary using dot notation or suffix matching.

### `set_deep(data: dict, key: str, value: Any) -> dict`

Set value in nested dictionary using dot notation. Returns new dictionary.
