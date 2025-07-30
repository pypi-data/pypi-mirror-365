"""Functions to pre-process data sources."""

import hashlib
import json
from typing import Any, Callable

import polars as pl


def cleaner(function: Callable, arguments: dict) -> dict[str, dict[str, Any]]:
    """Define a function to clean data.

    Args:
        function: the callable implementing the cleaning behaviour
        arguments: a dictionary of keyword arguments to pass to the cleaning function

    Returns:
        A representation of the cleaner ready to be passed to the `cleaners()` function
    """
    args_str = json.dumps(arguments, sort_keys=True, default=str)
    args_hash = hashlib.md5(args_str.encode()).hexdigest()[:6]
    cleaner_name = f"{function.__name__}_{args_hash}"
    return {cleaner_name: {"function": function, "arguments": arguments}}


def cleaners(*cleaner: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Combine multiple cleaners in a single object to pass to `process()`.

    Args:
        cleaner: Output of the `cleaner()` function

    Returns:
        A representation of multiple cleaners to be passed to the `process()` function

    Examples:
        ```python
        clean_pipeline = cleaners(
            cleaner(
                normalise_company_number,
                {"column": "company_number"},
            ),
            cleaner(
                normalise_postcode,
                {"column": "postcode"},
            ),
        )
        ```
    """
    return {k: v for d in cleaner for k, v in d.items()}


def process(data: pl.DataFrame, pipeline: dict[str, dict[str, Any]]) -> pl.DataFrame:
    """Apply cleaners to input dataframe.

    Args:
        data: The dataframe to process
        pipeline: Output of the `cleaners()` function

    Returns:
        The processed data
    """
    curr = data
    for func in pipeline.keys():
        curr = pipeline[func]["function"](curr, **pipeline[func]["arguments"])
    return curr
