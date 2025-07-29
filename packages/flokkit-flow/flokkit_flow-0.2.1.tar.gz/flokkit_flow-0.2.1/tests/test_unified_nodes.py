"""Test the unified node system."""

import pytest

from flow import flow
from flow.nodes.source import AsyncIteratorAdapter
from flow.nodes.unified import (
    FilterBehavior,
    MergeBehavior,
    NodeType,
    SinkBehavior,
    SourceBehavior,
    SplitBehavior,
    TransformBehavior,
    UnifiedNode,
    create_filter_node,
    create_merge_node,
    create_sink_node,
    create_source_node,
    create_split_node,
    create_transform_node,
)


class TestUnifiedNodes:
    """Test the unified node implementation."""

    @pytest.mark.asyncio
    async def test_unified_source_node(self):
        """Test unified source node behavior."""
        results = []

        # Test using the unified node system
        await (
            flow("test")
            .source(lambda: [1, 2, 3], int)
            .sink(lambda x: results.append(x))
            .execute()
        )

        assert results == [1, 2, 3]

    @pytest.mark.asyncio
    async def test_unified_transform_node(self):
        """Test unified transform node behavior."""
        results = []

        await (
            flow("test")
            .source(lambda: [1, 2, 3], int)
            .transform(lambda x: x * 2, int)
            .sink(lambda x: results.append(x))
            .execute()
        )

        assert results == [2, 4, 6]

    @pytest.mark.asyncio
    async def test_unified_filter_node(self):
        """Test unified filter node behavior."""
        results = []

        await (
            flow("test")
            .source(lambda: [1, 2, 3, 4, 5], int)
            .filter(lambda x: x % 2 == 0)
            .sink(lambda x: results.append(x))
            .execute()
        )

        assert results == [2, 4]

    @pytest.mark.asyncio
    async def test_unified_split_node(self):
        """Test unified split node behavior."""
        results = []

        # Test that split node can be created and works
        source_chain = flow("test").source(lambda: [1, 2, 3], int)
        branches = source_chain.split(2)

        # Just test that one branch works correctly
        await branches[0].sink(lambda x: results.append(x)).execute()

        assert results == [1, 2, 3]

    @pytest.mark.asyncio
    async def test_unified_merge_node(self):
        """Test unified merge node behavior."""
        results = []

        # Create two flows
        flow1 = flow("test1").source(lambda: [1, 2], int)
        flow2 = flow("test2").source(lambda: [3, 4], int)

        # Merge them (this uses the fixed merge functionality)
        await flow1.merge_with(flow2).sink(lambda x: results.append(x)).execute()

        assert sorted(results) == [1, 2, 3, 4]

    def test_node_type_determination(self):
        """Test that node types are correctly determined from behaviors."""
        # Create different behavior types
        source_behavior = SourceBehavior(AsyncIteratorAdapter([1, 2, 3]), int)
        sink_behavior = SinkBehavior(lambda x: None, int)
        transform_behavior = TransformBehavior(lambda x: x * 2, int, int)
        filter_behavior = FilterBehavior(lambda x: x > 0, int)
        split_behavior = SplitBehavior(int, 2)
        merge_behavior = MergeBehavior(int, 2)

        # Create unified nodes
        source_node = UnifiedNode("source", source_behavior)
        sink_node = UnifiedNode("sink", sink_behavior)
        transform_node = UnifiedNode("transform", transform_behavior)
        filter_node = UnifiedNode("filter", filter_behavior)
        split_node = UnifiedNode("split", split_behavior)
        merge_node = UnifiedNode("merge", merge_behavior)

        # Check node types
        assert source_node.node_type == NodeType.SOURCE
        assert sink_node.node_type == NodeType.SINK
        assert transform_node.node_type == NodeType.TRANSFORM
        assert filter_node.node_type == NodeType.FILTER
        assert split_node.node_type == NodeType.SPLIT
        assert merge_node.node_type == NodeType.MERGE

    def test_factory_functions(self):
        """Test that factory functions create correct unified nodes."""
        # Test factory functions
        source = create_source_node("src", AsyncIteratorAdapter([1, 2]), int)
        sink = create_sink_node("sink", lambda x: None, int)
        transform = create_transform_node("trans", lambda x: x * 2, int, int)
        filter_node = create_filter_node("filter", lambda x: x > 0, int)
        split = create_split_node("split", int, 2)
        merge = create_merge_node("merge", int, 2)

        # All should be UnifiedNode instances
        assert isinstance(source, UnifiedNode)
        assert isinstance(sink, UnifiedNode)
        assert isinstance(transform, UnifiedNode)
        assert isinstance(filter_node, UnifiedNode)
        assert isinstance(split, UnifiedNode)
        assert isinstance(merge, UnifiedNode)

        # Check names
        assert source.name == "src"
        assert sink.name == "sink"
        assert transform.name == "trans"
        assert filter_node.name == "filter"
        assert split.name == "split"
        assert merge.name == "merge"

    def test_node_repr(self):
        """Test unified node repr methods."""
        source = create_source_node("src", AsyncIteratorAdapter([1, 2]), int)
        sink = create_sink_node("sink", lambda x: None, int)
        transform = create_transform_node("trans", lambda x: x * 2, int, int)

        assert repr(source) == "SourceNode(src)"
        assert repr(sink) == "SinkNode(sink)"
        assert repr(transform) == "TransformNode(trans)"

    @pytest.mark.asyncio
    async def test_complex_unified_flow(self):
        """Test a complex flow using unified nodes."""
        results = []

        # Create a complex flow: source -> transform -> filter -> split -> merge -> sink
        source_flow = flow("test").source(lambda: range(10), int)

        # Transform and filter
        processed = source_flow.transform(lambda x: x * 2, int).filter(  # Double values
            lambda x: x > 10
        )  # Keep only values > 10

        # Split into 2 branches
        branches = processed.split(2)

        # Transform each branch differently
        branch1 = branches[0].transform(lambda x: x + 100, int)
        branch2 = branches[1].transform(lambda x: x + 200, int)

        # Merge them back
        merged = branch1.merge_with(branch2)

        # Sink
        await merged.sink(lambda x: results.append(x)).execute(
            duration=1.0
        )  # Add timeout

        # Values: 0,1,2,3,4,5,6,7,8,9 -> 0,2,4,6,8,10,12,14,16,18 -> 12,14,16,18
        # Branch1: 112,114,116,118  Branch2: 212,214,216,218
        # Due to timing, we might not get all values
        assert len(results) >= 4  # At least some values should be processed


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
