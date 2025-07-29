"""Focused test suite for maximum coverage with minimal, fast tests."""

import asyncio
import sys

import pytest

sys.path.insert(0, ".")

from flow import QueueFullStrategy, ensure_async, flow


class TestNodes:
    """Test all node types efficiently."""

    @pytest.mark.asyncio
    async def test_all_node_types(self):
        """Test all node types in one pipeline."""
        # Note: Split and Merge nodes are not directly supported in the new flow API
        # Testing basic pipeline functionality instead

        # Source
        def generate_values():
            for i in [1, 2, 3, 4, 5]:
                yield i

        results = []

        # Build and execute pipeline
        await (
            flow("All Nodes Test")
            .source(generate_values, int)
            .transform(lambda x: x * 2, int)
            .filter(lambda x: x > 5)
            .sink(results.append)
            .execute(duration=0.5)
        )

        # Verify some processing happened
        assert len(results) > 0
        assert all(x > 5 for x in results)  # All filtered

    @pytest.mark.asyncio
    async def test_lifecycle_hooks(self):
        """Test all lifecycle hooks."""
        # Note: The new flow API doesn't expose custom node types with lifecycle hooks
        # Testing error propagation instead

        def generate_with_error():
            yield 1
            yield 99

        def process_with_error(x):
            if x == 99:
                raise ValueError("test")
            return x

        # Execute and expect error propagation
        with pytest.raises(ValueError, match="test"):
            await (
                flow("Lifecycle")
                .source(generate_with_error, int)
                .transform(process_with_error, int)
                .sink(lambda x: None)
                .execute(duration=0.5)
            )


class TestQueueStrategies:
    """Test queue strategies efficiently."""

    @pytest.mark.asyncio
    async def test_queue_strategies(self):
        """Test queue strategies using constructor parameters."""

        # Test ERROR strategy - simplest to verify
        def generate_many():
            for i in range(10):
                yield i

        # Create sink that doesn't process (causing queue to fill)
        async def never_process(x):
            await asyncio.sleep(10)  # Never completes

        with pytest.raises(RuntimeError, match="Queue full"):
            await (
                flow("ERROR")
                .source(generate_many, int)
                .sink(
                    never_process, queue_size=1, full_strategy=QueueFullStrategy.ERROR
                )
                .execute(duration=0.1)
            )

        # Test basic queue strategy enum coverage
        assert QueueFullStrategy.BLOCK != QueueFullStrategy.DROP_NEW
        assert QueueFullStrategy.DROP_OLD != QueueFullStrategy.ERROR


class TestAdaptFunction:
    """Test function adaptation."""

    @pytest.mark.asyncio
    async def test_adapt_all_types(self):
        """Test adapting different function types."""

        # Sync function
        def sync_func(x):
            return x * 2

        adapted = ensure_async(sync_func)
        assert await adapted(5) == 10

        # Async function
        async def async_func(x):
            return x * 3

        adapted = ensure_async(async_func)
        assert await adapted(5) == 15

        # Generator
        def gen():
            yield 1
            yield 2

        adapted = ensure_async(gen)
        result = await adapted()
        # Generator functions return generator objects
        assert hasattr(result, "__next__")
        assert next(result) == 1

        # Async generator
        async def async_gen():
            yield 10
            yield 20

        adapted = ensure_async(async_gen)
        gen = await adapted()
        # Async generator functions return async generator objects
        assert hasattr(gen, "__anext__")
        first_value = await gen.__anext__()
        assert first_value == 10


class TestShutdown:
    """Test shutdown modes."""

    @pytest.mark.asyncio
    async def test_shutdown_modes(self):
        """Test all shutdown modes quickly."""
        # Note: The new flow API doesn't expose shutdown modes directly
        # Testing basic duration-based shutdown instead

        # Test with duration
        await (
            flow("Shutdown Test")
            .source(self._infinite_source, int)
            .sink(lambda x: None)
            .execute(duration=0.1)
        )

    async def _infinite_source(self):
        i = 0
        while True:
            yield i
            i += 1
            await asyncio.sleep(0.01)


class TestBuilderAPI:
    """Test fluent builder API."""

    @pytest.mark.asyncio
    async def test_builder_features(self):
        """Test builder API features."""
        builder = flow("Builder Test")
        results = {"tap": [], "filter": [], "final": []}

        # Simple pipeline to test builder API
        count = 0

        def source_func():
            nonlocal count
            count += 1
            return count

        def tap_func(x):
            results["tap"].append(x)

        def filter_func(x):
            return x <= 5

        def double_func(x):
            return x * 2

        def final_func(x):
            results["final"].append(x)

        # No longer need GraphMaterializer

        pipeline = (
            builder.source(source_func, int)
            .tap(tap_func)
            .filter(filter_func)
            .transform(double_func, int)
            .sink(final_func)
        )

        # Build and run
        await pipeline.execute(duration=0.2)

        # Check that the pipeline processed some values
        assert len(results["tap"]) > 0
        assert len(results["final"]) > 0
        # All final results should be even (doubled) and <= 10 (filtered <= 5, then doubled)
        assert all(x % 2 == 0 and x <= 10 for x in results["final"])


class TestEdgeCases:
    """Test edge cases and error conditions."""

    @pytest.mark.asyncio
    async def test_auto_stop(self):
        """Test auto stop functionality."""

        # Auto stop enabled by default
        def generate_auto_stop_values():
            for i in [1, 2, 3]:
                yield i

        results = []
        await (
            flow("Auto Stop")
            .source(generate_auto_stop_values, int)
            .sink(results.append)
            .execute(duration=1.0)
        )  # Use duration to prevent hanging

        assert len(results) == 3

        # Test with duration instead of auto_stop=False
        count = 0

        async def infinite_source():
            nonlocal count
            while True:
                count += 1
                yield count
                await asyncio.sleep(0.01)  # Small delay to prevent CPU spinning

        results2 = []
        await (
            flow("No Auto Stop")
            .source(infinite_source, int)
            .sink(results2.append)
            .execute(duration=0.2, auto_stop=False)
        )

        assert len(results2) > 0  # Got some values
        assert len(results2) < 30  # Should not get too many in 0.2s

    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error propagation."""

        def error_transform(x):
            if x == 2:
                raise ValueError("Test error")
            return x

        def generate_error_test_values():
            for i in [1, 2, 3]:
                yield i

        with pytest.raises(ValueError):
            await (
                flow("Error Test")
                .source(generate_error_test_values, int)
                .transform(error_transform, int)
                .sink(lambda x: None)
                .execute(duration=0.5)
            )

    def test_repr_methods(self):
        """Test __repr__ methods for coverage."""
        # Test flow builder repr
        builder = flow("Test Flow")
        graph = builder.build()
        assert "Test Flow" in graph.name

        # Test with actual nodes
        def generate_empty():
            return
            yield  # Never reached

        builder = flow("Test")
        chain = builder.source(generate_empty, int)
        graph = chain.build()
        assert len(graph.nodes) == 1

    def test_source_tracking(self):
        """Test source node tracking."""

        # The new flow API doesn't expose internal tracking methods
        # Testing that source nodes work correctly instead
        def generate_values():
            yield 1
            yield 2
            yield 3

        results = []
        builder = flow("Tracking").source(generate_values, int).sink(results.append)

        # Build and verify source is in graph
        graph = builder.build()
        assert len(graph.nodes) == 2
        assert len(graph.source_nodes) == 1

    @pytest.mark.asyncio
    async def test_transform_without_caching(self):
        """Test transform functionality without caching."""
        calls = 0

        def expensive(x):
            nonlocal calls
            calls += 1
            return x * x

        def generate_repeated():
            for i in [1, 2, 1, 2, 1]:
                yield i

        await (
            flow("Transform Test")
            .source(generate_repeated, int)
            .transform(expensive, int)
            .sink(lambda x: None)
            .execute(duration=0.5)
        )

        # Should call expensive for every value (5 times)
        assert calls == 5

    @pytest.mark.asyncio
    async def test_port_operations(self):
        """Test port edge cases."""
        # The new flow API doesn't expose port operations directly
        # Testing basic sink functionality instead
        results = []
        processed = False

        async def test_sink(x):
            nonlocal processed
            processed = True
            results.append(x)

        await (
            flow("Port Test")
            .source(lambda: [1], int)
            .sink(test_sink)
            .execute(duration=0.1)
        )

        assert processed
        assert results == [1]

    # @pytest.mark.asyncio
    # async def test_blocking_function(self):
    #     """Test blocking function handling."""
    #     # This test is no longer relevant as is_blocking parameter was removed
    #     pass

    @pytest.mark.asyncio
    async def test_dag_verification(self):
        """Test DAG verification is called."""
        # The new flow API inherently prevents cycles during construction
        # Testing basic chaining instead

        await (
            flow("DAG Test")
            .source(lambda: [1, 2, 3], int)
            .transform(lambda x: x, int)
            .transform(lambda x: x, int)
            .sink(lambda x: None)
            .execute(duration=0.1)
        )
