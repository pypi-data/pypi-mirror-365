"""Tests to cover remaining AsyncIteratorAdapter cases."""

import asyncio

import pytest

from flow import flow
from flow.nodes.source import AsyncIteratorAdapter


class TestAsyncIteratorAdapterCoverage:
    """Test remaining uncovered cases in AsyncIteratorAdapter."""

    @pytest.mark.asyncio
    async def test_async_iterator_directly(self):
        """Test passing an async iterator directly (not async generator function)."""

        class CustomAsyncIterator:
            def __init__(self):
                self.count = 0

            def __aiter__(self):
                return self

            async def __anext__(self):
                if self.count < 3:
                    self.count += 1
                    return self.count
                raise StopAsyncIteration

        # Test with the adapter directly
        adapter = AsyncIteratorAdapter(CustomAsyncIterator())
        values = []
        async for val in adapter:
            values.append(val)
        assert values == [1, 2, 3]

        # Test in a flow
        results = []
        await (
            flow("test")
            .source(CustomAsyncIterator(), int)
            .sink(lambda x: results.append(x))
            .execute()
        )
        assert results == [1, 2, 3]

    @pytest.mark.asyncio
    async def test_async_function_returning_async_iterator(self):
        """Test async function that returns an async iterator."""

        async def async_func_returns_async_iter():
            class AsyncIter:
                def __init__(self):
                    self.count = 0

                def __aiter__(self):
                    return self

                async def __anext__(self):
                    if self.count < 2:
                        self.count += 1
                        return self.count
                    raise StopAsyncIteration

            return AsyncIter()

        results = []
        await (
            flow("test")
            .source(async_func_returns_async_iter, int)
            .sink(lambda x: results.append(x))
            .execute()
        )
        assert results == [1, 2]

    @pytest.mark.asyncio
    async def test_async_function_returning_none(self):
        """Test async function that returns None (stops iteration)."""
        call_count = 0

        async def async_func_returns_none():
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                return call_count
            return None  # Stop iteration

        results = []
        await (
            flow("test")
            .source(async_func_returns_none, int)
            .sink(lambda x: results.append(x))
            .execute()
        )
        assert results == [1, 2]

    @pytest.mark.asyncio
    async def test_async_infinite_callable(self):
        """Test async function as infinite source."""
        call_count = 0

        async def async_infinite():
            nonlocal call_count
            call_count += 1
            if call_count > 5:
                return None  # Stop after 5
            await asyncio.sleep(0.01)
            return call_count

        results = []
        await (
            flow("test")
            .source(async_infinite, int)
            .sink(lambda x: results.append(x))
            .execute()
        )
        assert results == [1, 2, 3, 4, 5]

    @pytest.mark.asyncio
    async def test_single_non_callable_value(self):
        """Test passing a single non-callable, non-iterable value."""
        # This should produce no values
        results = []
        await (
            flow("test")
            .source(42, int)  # Single value, not callable or iterable
            .sink(lambda x: results.append(x))
            .execute()
        )
        assert results == []

    @pytest.mark.asyncio
    async def test_iterator_exhaustion(self):
        """Test when iterator is exhausted and returns None."""

        class ExhaustibleIterator:
            def __init__(self):
                self.items = [1, 2, 3]
                self.index = 0

            def __iter__(self):
                return self

            def __next__(self):
                if self.index < len(self.items):
                    val = self.items[self.index]
                    self.index += 1
                    return val
                # This covers line 92 where iterator exists but raises StopIteration
                raise StopIteration

        results = []
        await (
            flow("test")
            .source(ExhaustibleIterator(), int)
            .sink(lambda x: results.append(x))
            .execute()
        )
        assert results == [1, 2, 3]

    @pytest.mark.asyncio
    async def test_source_node_repr(self):
        """Test SourceNode repr method (line 109)."""
        from flow.nodes.unified import create_source_node

        # Create a source node using unified nodes
        source_node = create_source_node(
            "test_source", AsyncIteratorAdapter(lambda: [1, 2]), int
        )

        # Test repr
        repr_str = repr(source_node)
        assert repr_str == "SourceNode(test_source)"

    @pytest.mark.asyncio
    async def test_complex_flow_with_various_sources(self):
        """Test a complex flow mixing different source types."""

        # Sync generator
        def sync_gen():
            yield from [1, 2]

        # Async generator
        async def async_gen():
            for i in [3, 4]:
                yield i

        # Regular list
        list_source = [5, 6]

        results1, results2, results3 = [], [], []

        # Run all three flows
        await (
            flow("sync_gen")
            .source(sync_gen, int)
            .sink(lambda x: results1.append(x))
            .execute()
        )

        await (
            flow("async_gen")
            .source(async_gen, int)
            .sink(lambda x: results2.append(x))
            .execute()
        )

        await (
            flow("list")
            .source(lambda: list_source, int)
            .sink(lambda x: results3.append(x))
            .execute()
        )

        assert results1 == [1, 2]
        assert results2 == [3, 4]
        assert results3 == [5, 6]

    @pytest.mark.asyncio
    async def test_async_generator_function_direct(self):
        """Test async generator function detected by inspect (line 39)."""

        async def async_gen_func():
            yield 1
            yield 2

        # Use adapter directly to test line 39
        adapter = AsyncIteratorAdapter(async_gen_func)
        values = []
        async for val in adapter:
            values.append(val)
        assert values == [1, 2]

    @pytest.mark.asyncio
    async def test_async_callable_returning_none_first_call(self):
        """Test async callable that returns None on first call (line 50)."""

        async def returns_none_immediately():
            return None

        results = []
        await (
            flow("test")
            .source(returns_none_immediately, int)
            .sink(lambda x: results.append(x))
            .execute()
        )
        assert results == []

    @pytest.mark.asyncio
    async def test_async_infinite_callable_with_await(self):
        """Test infinite async callable (lines 78-81)."""
        call_count = 0

        async def async_callable():
            nonlocal call_count
            call_count += 1
            if call_count > 3:
                return None
            return call_count

        # Test through adapter to ensure we hit the async path
        adapter = AsyncIteratorAdapter(async_callable)
        adapter._is_infinite_callable = True  # Force infinite callable mode
        adapter._initialized = True  # Skip initialization

        values = []
        try:
            async for val in adapter:
                values.append(val)
        except StopAsyncIteration:
            pass

        assert values == [1, 2, 3]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
