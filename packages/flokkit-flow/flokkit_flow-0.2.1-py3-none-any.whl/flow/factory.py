"""Utility functions for the flow-based programming framework."""

import asyncio
from functools import wraps
from typing import Any, Awaitable, Callable


def ensure_async(func: Callable[..., Any]) -> Callable[..., Awaitable[Any]]:
    """Ensure a function is async.

    If the function is already async, returns it unchanged.
    If the function is sync, wraps it to be async.

    Args:
        func: Function to ensure is async

    Returns:
        An async version of the function

    Examples:
        Wrap a sync function:

        >>> def sync_add(x, y):
        ...     return x + y
        >>> async_add = ensure_async(sync_add)
        >>> import asyncio
        >>> asyncio.run(async_add(2, 3))
        5

        Already async function is unchanged:

        >>> async def already_async(x):
        ...     return x * 2
        >>> ensure_async(already_async) is already_async
        True

        Preserves function metadata:

        >>> def documented_func(x):
        ...     '''This function doubles the input'''
        ...     return x * 2
        >>> async_func = ensure_async(documented_func)
        >>> async_func.__name__
        'documented_func'
        >>> async_func.__doc__
        'This function doubles the input'
    """
    if asyncio.iscoroutinefunction(func):
        return func

    @wraps(func)
    async def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper
