"""Source node implementation and async iterator adapters."""

import asyncio
import inspect
from typing import Any, AsyncIterator, Callable, Iterator

from ..core import T

# Simple, focused adapter classes


class AsyncIteratorSource(AsyncIterator[T]):
    """Adapter for sources that are already async iterators."""

    def __init__(self, source: AsyncIterator[T]):
        self.source = source

    def __aiter__(self):
        return self

    async def __anext__(self):
        return await self.source.__anext__()


class SyncIteratorSource(AsyncIterator[T]):
    """Adapter for sync iterators (lists, generators, etc)."""

    def __init__(self, source: Iterator[T]):
        self.source = source

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            return next(self.source)
        except StopIteration:
            raise StopAsyncIteration


class AsyncCallableSource(AsyncIterator[T]):
    """Adapter for async callables that return values or iterators."""

    def __init__(self, source: Callable[[], Any]):
        self.source = source
        self._initialized = False
        self._iterator = None

    def __aiter__(self):
        return self

    async def __anext__(self):
        if not self._initialized:
            # First call - check what the async function returns
            result = await self.source()

            # Check if it returned an iterator
            if hasattr(result, "__aiter__"):
                self._iterator = result.__aiter__()
                self._initialized = True
                return await self._iterator.__anext__()
            if hasattr(result, "__iter__"):
                self._iterator = iter(result)
                self._initialized = True
                try:
                    return next(self._iterator)
                except StopIteration:
                    raise StopAsyncIteration
            else:
                # It returns single values
                self._initialized = True
                if result is None:
                    raise StopAsyncIteration
                return result

        # Subsequent calls
        if self._iterator:
            if hasattr(self._iterator, "__anext__"):
                return await self._iterator.__anext__()
            try:
                return next(self._iterator)
            except StopIteration:
                raise StopAsyncIteration
        else:
            # Single value mode - call function again
            result = await self.source()
            if result is None:
                raise StopAsyncIteration
            return result


class SyncCallableSource(AsyncIterator[T]):
    """Adapter for sync callables that return values or iterators."""

    def __init__(self, source: Callable[[], Any]):
        self.source = source
        self._initialized = False
        self._iterator = None

    def __aiter__(self):
        return self

    async def __anext__(self):
        if not self._initialized:
            # First call - check what the function returns
            result = self.source()

            # Check if it returned an iterator
            if hasattr(result, "__aiter__"):
                self._iterator = result.__aiter__()
                self._initialized = True
                return await self._iterator.__anext__()
            if hasattr(result, "__iter__"):
                self._iterator = iter(result)
                self._initialized = True
                try:
                    return next(self._iterator)
                except StopIteration:
                    raise StopAsyncIteration
            else:
                # It returns single values
                self._initialized = True
                if result is None:
                    raise StopAsyncIteration
                return result

        # Subsequent calls
        if self._iterator:
            if hasattr(self._iterator, "__anext__"):
                return await self._iterator.__anext__()
            try:
                return next(self._iterator)
            except StopIteration:
                raise StopAsyncIteration
        else:
            # Single value mode - call function again
            result = self.source()
            if result is None:
                raise StopAsyncIteration
            return result


# Factory function to maintain backward compatibility
def AsyncIteratorAdapter(source: Any) -> AsyncIterator[Any]:
    """Create appropriate async iterator adapter based on source type.

    This maintains backward compatibility with the old AsyncIteratorAdapter class.
    """
    # Check if already an async iterator
    if hasattr(source, "__aiter__"):
        return AsyncIteratorSource(source)

    # Check if sync iterator (including lists, tuples, generators)
    if hasattr(source, "__iter__"):
        return SyncIteratorSource(iter(source))

    # Check if callable
    if callable(source):
        # Handle async generator functions
        if inspect.isasyncgenfunction(source):
            return AsyncIteratorSource(source())

        # Handle sync generator functions
        if inspect.isgeneratorfunction(source):
            return SyncIteratorSource(source())

        # Handle regular callables
        if asyncio.iscoroutinefunction(source):
            return AsyncCallableSource(source)
        return SyncCallableSource(source)

    # Single value - immediately exhausted
    return SyncIteratorSource(iter([]))
