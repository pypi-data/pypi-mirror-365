"""
JSON Tools RS - High-performance JSON manipulation library

This package provides Python bindings for the JSON Tools RS library,
offering high-performance JSON flattening and unflattening with SIMD-accelerated parsing.

The main entry points are the JsonFlattener and JsonUnflattener classes, which provide
unified builder pattern APIs for all JSON manipulation operations.

Perfect Type Matching - Input type = Output type:
    - str input → str output (JSON string)
    - dict input → dict output (Python dictionary)
    - list[str] input → list[str] output (list of JSON strings)
    - list[dict] input → list[dict] output (list of Python dictionaries)
    - Mixed lists preserve original types

Flattening Example:
    >>> import json_tools_rs
    >>>
    >>> # JSON string input → JSON string output
    >>> flattener = json_tools_rs.JsonFlattener()
    >>> result = flattener.flatten('{"user": {"name": "John", "age": 30}}')
    >>> print(result)  # '{"user.name": "John", "user.age": 30}' (str)
    >>> print(type(result))  # <class 'str'>
    >>>
    >>> # Python dict input → Python dict output (much more convenient!)
    >>> result = flattener.flatten({"user": {"name": "John", "age": 30}})
    >>> print(result)  # {'user.name': 'John', 'user.age': 30} (dict)
    >>> print(type(result))  # <class 'dict'>

Unflattening Example:
    >>> import json_tools_rs
    >>>
    >>> # JSON string input → JSON string output
    >>> unflattener = json_tools_rs.JsonUnflattener()
    >>> result = unflattener.unflatten('{"user.name": "John", "user.age": 30}')
    >>> print(result)  # '{"user": {"name": "John", "age": 30}}' (str)
    >>> print(type(result))  # <class 'str'>
    >>>
    >>> # Python dict input → Python dict output (much more convenient!)
    >>> result = unflattener.unflatten({"user.name": "John", "user.age": 30})
    >>> print(result)  # {'user': {'name': 'John', 'age': 30}} (dict)
    >>> print(type(result))  # <class 'dict'>

Advanced Configuration:
    >>> # Both classes support the same builder pattern
    >>> flattener = (json_tools_rs.JsonFlattener()
    ...     .remove_empty_strings(True)
    ...     .remove_nulls(True)
    ...     .separator("_")
    ...     .lowercase_keys(True))
    >>>
    >>> unflattener = (json_tools_rs.JsonUnflattener()
    ...     .separator("_")
    ...     .lowercase_keys(True)
    ...     .key_replacement("prefix_", "user_"))
    >>>
    >>> # Perfect type preservation in batch processing
    >>> str_results = flattener.flatten(['{"a": 1}', '{"b": 2}'])
    >>> print(str_results)  # ['{"a": 1}', '{"b": 2}'] (list of strings)
    >>>
    >>> dict_results = unflattener.unflatten([{"a.b": 1}, {"c.d": 2}])
    >>> print(dict_results)  # [{'a': {'b': 1}}, {'c': {'d': 2}}] (list of dicts)
"""

from .json_tools_rs import JsonFlattener, JsonFlattenError, JsonOutput, JsonUnflattener

__version__ = "0.1.0"
__author__ = "JSON Tools RS Contributors"

__all__ = [
    "JsonFlattener",
    "JsonUnflattener",
    "JsonOutput",
    "JsonFlattenError",
]
