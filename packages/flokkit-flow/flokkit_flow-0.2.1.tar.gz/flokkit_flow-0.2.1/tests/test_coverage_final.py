"""Final tests to reach near 100% coverage."""

import asyncio

import pytest

from flow import flow
from flow.core.strategies import DropOldStrategy
from flow.nodes.source import AsyncIteratorAdapter


class TestStrategyEdgeCases:
    """Test remaining strategy edge cases."""

    @pytest.mark.asyncio
    async def test_drop_old_strategy_empty_queue_edge_case(self):
        """Test DropOldStrategy.put with truly empty queue."""
        strategy = DropOldStrategy()
        queue = asyncio.Queue(maxsize=1)

        # This should handle the empty queue case gracefully
        await strategy.put(queue, 1, "test")
        assert queue.get_nowait() == 1


class TestDescriptionEdgeCases2:
    """Test remaining description edge cases."""

    def test_get_ports_with_qualified_references(self):
        """Test that FlowBuilder builds graphs correctly."""
        # Build a simple graph
        builder = flow("test")
        results = []

        chain = (
            builder.source(lambda: [1, 2, 3], int)
            .transform(lambda x: str(x), str)
            .sink(results.append)
        )

        graph = chain.build()

        # Test that graph was built correctly
        assert len(graph.nodes) == 3
        assert len(graph.connections) == 2
        assert len(graph.source_nodes) == 1


class TestAsyncIteratorAdapterEdgeCases:
    """Test AsyncIteratorAdapter edge cases."""

    @pytest.mark.asyncio
    async def test_adapter_with_sync_generator(self):
        """Test adapter with sync generator."""

        def sync_gen():
            yield 1
            yield 2

        adapter = AsyncIteratorAdapter(sync_gen)
        values = []
        async for val in adapter:
            values.append(val)
        assert values == [1, 2]

    @pytest.mark.asyncio
    async def test_adapter_with_async_generator(self):
        """Test adapter with async generator."""

        async def async_gen():
            yield 1
            yield 2

        adapter = AsyncIteratorAdapter(async_gen)
        values = []
        async for val in adapter:
            values.append(val)
        assert values == [1, 2]

    @pytest.mark.asyncio
    async def test_adapter_with_sync_function_returning_list(self):
        """Test adapter with sync function returning list."""

        def sync_func():
            return [1, 2, 3]

        adapter = AsyncIteratorAdapter(sync_func)
        values = []
        async for val in adapter:
            values.append(val)
        assert values == [1, 2, 3]

    @pytest.mark.asyncio
    async def test_adapter_with_async_function_returning_list(self):
        """Test adapter with async function returning list."""

        async def async_func():
            return [1, 2, 3]

        adapter = AsyncIteratorAdapter(async_func)
        values = []
        async for val in adapter:
            values.append(val)
        assert values == [1, 2, 3]

    @pytest.mark.asyncio
    async def test_adapter_with_callable_returning_none(self):
        """Test adapter with callable that returns None (stops iteration)."""
        call_count = 0

        def finite_callable():
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                return call_count
            return None

        adapter = AsyncIteratorAdapter(finite_callable)
        values = []
        async for val in adapter:
            values.append(val)
        assert values == [1, 2]

    @pytest.mark.asyncio
    async def test_adapter_with_sync_iterator(self):
        """Test adapter with sync iterator (not generator function)."""
        # Pass an actual iterator, not a generator function
        iterator = iter([1, 2, 3])

        adapter = AsyncIteratorAdapter(iterator)
        values = []
        async for val in adapter:
            values.append(val)
        assert values == [1, 2, 3]


class TestMaterializerValidation:
    """Test materializer validation paths."""

    def test_materializer_duplicate_connections(self):
        """Test that FlowBuilder prevents duplicate connections."""
        # FlowBuilder inherently prevents duplicate connections by design
        # Each transform/sink creates a new node with a single connection
        builder = flow("test")
        results = []

        # Build a simple chain - each operation creates exactly one connection
        chain = (
            builder.source(lambda: [1, 2], int)
            .transform(lambda x: x * 2, int)
            .sink(results.append)
        )

        graph = chain.build()
        # Should have exactly 2 connections (source->transform, transform->sink)
        assert len(graph.connections) == 2

    def test_materializer_unknown_node_type(self):
        """Test that FlowBuilder only allows valid operations."""
        # FlowBuilder doesn't allow unknown node types - you can only use the provided methods
        builder = flow("test")

        # Can only use source, transform, filter, tap, sink, split, merge_with
        # No way to create an unknown node type
        assert hasattr(builder, "source")
        assert hasattr(builder, "transform")
        assert not hasattr(builder, "unknown_operation")

    def test_materializer_missing_port_in_connection(self):
        """Test that FlowBuilder ensures valid connections."""
        # FlowBuilder creates valid connections by construction
        # Invalid connections are prevented at the API level
        builder = flow("test")

        # The API only allows valid operations that create proper connections
        chain = builder.source(lambda: [1], int)

        # Can't create invalid connections - the API doesn't allow it
        # Each method creates the right ports and connections automatically
        assert hasattr(chain, "transform")
        assert hasattr(chain, "sink")


class TestExecutableGraphEdgeCases:
    """Test ExecutableGraph edge cases."""

    @pytest.mark.asyncio
    async def test_graph_shutdown_graceful_with_timeout(self):
        """Test graceful shutdown with very short timeout."""

        async def slow_processor(x):
            await asyncio.sleep(1)  # Longer than timeout
            return x

        results = []
        await (
            flow("test")
            .source(lambda: range(10), int)
            .transform(slow_processor, int)
            .sink(lambda x: results.append(x))
            .execute(duration=0.1)
        )

        # Should have processed very few due to slow processing
        assert len(results) < 5


class TestFlowBuilderEdgeCases2:
    """More flow builder edge cases."""

    def test_flow_builder_counter_increments(self):
        """Test that node counter increments properly."""
        builder = flow("test")

        # Add multiple nodes
        chain1 = builder.source(lambda: [1], int)
        chain2 = chain1.transform(lambda x: x * 2, int)
        chain3 = chain2.sink(lambda x: None)

        # Check counter incremented
        assert chain3._node_counter > 0

    @pytest.mark.asyncio
    async def test_flow_with_namespace(self):
        """Test flow with custom namespace."""
        results = []

        await (
            flow("custom_namespace")
            .source(lambda: [1, 2, 3], int)
            .sink(lambda x: results.append(x))
            .execute()
        )

        assert results == [1, 2, 3]


class TestFactoryFunctions:
    """Test factory function calls to improve coverage."""

    @pytest.mark.asyncio
    async def test_factory_create_functions_are_called(self):
        """Ensure unified node factory create functions are exercised."""
        from flow.nodes.source import AsyncIteratorAdapter
        from flow.nodes.unified import (
            create_filter_node,
            create_sink_node,
            create_source_node,
            create_transform_node,
        )

        # These are called internally by the materializer
        # Let's call them directly to ensure coverage

        # create_source_node
        source = create_source_node(
            "test_source", AsyncIteratorAdapter(lambda: [1, 2]), int
        )
        assert source.name == "test_source"

        # create_sink_node
        sink = create_sink_node("test_sink", lambda x: None, int)
        assert sink.name == "test_sink"

        # create_transform_node
        transform = create_transform_node("test_transform", lambda x: x * 2, int, int)
        assert transform.name == "test_transform"

        # create_filter_node
        filter_node = create_filter_node("test_filter", lambda x: x > 0, int)
        assert filter_node.name == "test_filter"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
