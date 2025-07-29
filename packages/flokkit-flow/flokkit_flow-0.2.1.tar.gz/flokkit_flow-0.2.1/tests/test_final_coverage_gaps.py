"""Tests for final coverage gaps."""

import asyncio

import pytest

from flow import flow
from flow.nodes.unified import create_merge_node


class TestFinalGaps:
    """Test final coverage gaps."""

    def test_node_str_method(self):
        """Test Node.__str__ method (line 30 in base.py)."""
        # Create a concrete node instance using unified nodes
        merge_node = create_merge_node("test_merge", int, num_inputs=2)

        # Test __str__
        assert str(merge_node) == "test_merge"

    def test_node_signal_completion(self):
        """Test Node.signal_completion method (line 89 in base.py)."""
        merge_node = create_merge_node("test_merge", int, num_inputs=2)

        # Should start not completed
        assert not merge_node._completed

        # Signal completion
        merge_node.signal_completion()

        # Should now be completed
        assert merge_node._completed

    @pytest.mark.asyncio
    async def test_merge_node_edge_case(self):
        """Test merge node when a port is exhausted (lines 55-56)."""
        # This tests the case where one input to merge is exhausted
        results = []

        # One source with fewer items
        flow1 = flow("test1").source(lambda: [1, 2], int)
        # Another source with more items
        flow2 = flow("test2").source(lambda: [3, 4, 5, 6], int)

        # Merge them - flow1 will exhaust first
        await flow1.merge_with(flow2).sink(lambda x: results.append(x)).execute()

        # Should get all values from both sources
        assert sorted(results) == [1, 2, 3, 4, 5, 6]

    @pytest.mark.asyncio
    async def test_flow_builder_edge_cases(self):
        """Test edge cases in flow_builder.py."""
        # Test line 93 - build() on FlowBuilderChain
        flow_chain = flow("test").source(lambda: [1], int)
        graph = flow_chain.build()
        assert graph.name == "test"  # ExecutableGraph has name, not namespace

        # Test lines 346, 351 - branches in merge_with for connection renaming
        # This happens when connections have non-local references
        results = []

        # Create flows with internal connections
        flow1 = (
            flow("test1").source(lambda: [1, 2], int).transform(lambda x: x * 10, int)
        )

        flow2 = flow("test2").source(lambda: [3, 4], int).filter(lambda x: x > 2)

        # Merge them - this exercises the connection renaming logic
        await flow1.merge_with(flow2).sink(lambda x: results.append(x)).execute()

        assert sorted(results) == [3, 4, 10, 20]

    @pytest.mark.asyncio
    async def test_execute_with_auto_stop_false(self):
        """Test execute with auto_stop=False (lines 411-412)."""

        # Create an infinite source
        async def infinite_source():
            count = 0
            while True:
                count += 1
                yield count
                await asyncio.sleep(0.1)

        results = []

        # Run with auto_stop=False and no duration
        # This should use the default 60s duration but we'll stop it early
        task = asyncio.create_task(
            flow("test")
            .source(infinite_source, int)
            .sink(lambda x: results.append(x))
            .execute(auto_stop=False)  # No duration, auto_stop=False
        )

        # Let it run briefly
        await asyncio.sleep(0.3)
        task.cancel()

        try:
            await task
        except asyncio.CancelledError:
            pass

        # Should have collected some values
        assert len(results) >= 2
        assert all(isinstance(x, int) for x in results)
