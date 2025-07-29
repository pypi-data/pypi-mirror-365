"""Simple test for cycle detection in FlowBuilder."""

import pytest

from flow import flow
from flow.flow_builder import PendingConnection
from flow.nodes.unified import create_transform_node


class TestCycleDetection:
    """Test cycle detection functionality."""

    def test_cycle_detection(self):
        """Test that FlowBuilder detects cycles and raises ValueError."""

        # Create a normal flow builder
        builder = flow("test").source(lambda: [1, 2, 3], int)

        # Manually create nodes that will form a cycle
        node1 = create_transform_node("node1", lambda x: x, int, int, False)
        node2 = create_transform_node("node2", lambda x: x, int, int, False)

        # Add these nodes to the builder
        builder._nodes.extend([node1, node2])
        builder._debug_names[node1] = "node1"
        builder._debug_names[node2] = "node2"

        # Create connections that form a cycle: node1 -> node2 -> node1
        builder._connections.extend(
            [
                PendingConnection(
                    from_node=node1,
                    from_port_name="out",
                    to_node=node2,
                    to_port_name="in",
                ),
                PendingConnection(
                    from_node=node2,
                    from_port_name="out",
                    to_node=node1,
                    to_port_name="in",
                ),
            ]
        )

        # Try to build - should raise ValueError about cycle
        with pytest.raises(ValueError, match="Graph contains a cycle"):
            builder.build()

    def test_no_cycle_normal_flow(self):
        """Test that normal flows don't trigger cycle detection."""

        # This should work fine - no cycle
        builder = (
            flow("test")
            .source(lambda: [1, 2, 3], int)
            .transform(lambda x: x * 2, int)
            .filter(lambda x: x > 2)
            .sink(lambda x: None)
        )

        # Should build successfully
        graph = builder.build()
        assert len(graph.nodes) == 4  # source, transform, filter, sink
