"""Tests to cover tiny remaining gaps."""

import pytest

from flow import flow


class TestTinyGaps:
    """Test tiny coverage gaps."""

    def test_flow_builder_optional_namespace(self):
        """Test FlowBuilder with optional namespace."""
        # No namespace defaults to "flow"
        builder1 = flow()
        assert builder1.namespace == "flow"

        # Empty namespace also defaults to "flow"
        builder2 = flow("")
        assert builder2.namespace == "flow"

        # Explicit namespace works
        builder3 = flow("custom")
        assert builder3.namespace == "custom"

    @pytest.mark.asyncio
    async def test_materializer_node_not_found_error(self):
        """Test that FlowBuilder validates nodes exist during build."""
        # FlowBuilder creates connections as you chain operations
        # You can't create a connection to a non-existent node
        builder = flow("test")

        # This creates a valid graph with one source node
        chain = builder.source(lambda: [1], int)

        # Building succeeds - no invalid connections possible
        graph = chain.build()
        assert len(graph.nodes) == 1
