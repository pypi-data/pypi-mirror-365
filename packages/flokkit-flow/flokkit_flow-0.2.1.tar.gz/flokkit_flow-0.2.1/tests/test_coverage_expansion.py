"""Tests to expand coverage to near 100%."""

import asyncio

import pytest

from flow import flow
from flow.core.ports import Port
from flow.core.strategies import DropOldStrategy
from flow.factory import ensure_async


class TestPortErrorCases:
    """Test error cases in Port class."""

    def test_connect_from_input_port_error(self):
        """Test connecting from an input port raises error."""
        input_port = Port[int](name="in", is_input=True, data_type=int)
        output_port = Port[int](name="out", is_input=False, data_type=int)

        with pytest.raises(ValueError, match="Can only connect from output ports"):
            input_port.connect_to(output_port)

    def test_connect_to_output_port_error(self):
        """Test connecting to an output port raises error."""
        output_port1 = Port[int](name="out1", is_input=False, data_type=int)
        output_port2 = Port[int](name="out2", is_input=False, data_type=int)

        with pytest.raises(ValueError, match="Can only connect to input ports"):
            output_port1.connect_to(output_port2)

    def test_connect_type_mismatch_error(self):
        """Test connecting mismatched types raises error."""
        output_port = Port[int](name="out", is_input=False, data_type=int)
        input_port = Port[str](name="in", is_input=True, data_type=str)

        with pytest.raises(TypeError, match="Type mismatch"):
            output_port.connect_to(input_port)

    @pytest.mark.asyncio
    async def test_send_from_input_port_error(self):
        """Test sending from input port raises error."""
        input_port = Port[int](name="in", is_input=True, data_type=int)

        with pytest.raises(ValueError, match="Can only send from output ports"):
            await input_port.send(42)

    @pytest.mark.asyncio
    async def test_receive_from_output_port_error(self):
        """Test receiving from output port raises error."""
        output_port = Port[int](name="out", is_input=False, data_type=int)

        with pytest.raises(ValueError, match="Can only receive from input ports"):
            await output_port.receive()

    @pytest.mark.asyncio
    async def test_receive_uninitialized_port_error(self):
        """Test receiving from uninitialized port."""
        input_port = Port[int](name="in", is_input=True, data_type=int)

        with pytest.raises(RuntimeError, match="Port not initialized"):
            await input_port.receive()

    @pytest.mark.asyncio
    async def test_receive_timeout(self):
        """Test receive with timeout."""
        input_port = Port[int](name="in", is_input=True, data_type=int)
        await input_port.initialize()

        # Should timeout and return None
        result = await input_port.receive(timeout=0.01)
        assert result is None

    @pytest.mark.asyncio
    async def test_has_data_empty(self):
        """Test has_data on empty queue."""
        input_port = Port[int](name="in", is_input=True, data_type=int)
        await input_port.initialize()

        assert not input_port.has_data()

    @pytest.mark.asyncio
    async def test_is_full(self):
        """Test is_full on queue."""
        input_port = Port[int](name="in", is_input=True, data_type=int, queue_size=1)
        await input_port.initialize()

        # Fill the queue
        input_port._queue.put_nowait(42)
        assert input_port.is_full()


class TestQueueStrategiesEdgeCases:
    """Test queue strategy edge cases."""

    @pytest.mark.asyncio
    async def test_drop_old_empty_queue(self):
        """Test DropOldStrategy with empty queue."""
        strategy = DropOldStrategy()
        queue = asyncio.Queue(maxsize=2)

        # Should work fine with empty queue
        await strategy.put(queue, 42, "test_node")
        assert queue.qsize() == 1
        assert await queue.get() == 42


class TestFactoryEdgeCases:
    """Test factory edge cases."""

    def test_ensure_async_with_sync_function(self):
        """Test ensure_async wraps sync functions."""

        def sync_func(x):
            return x * 2

        async_func = ensure_async(sync_func)
        assert asyncio.iscoroutinefunction(async_func)

    def test_ensure_async_with_async_function(self):
        """Test ensure_async returns async functions unchanged."""

        async def async_func(x):
            return x * 2

        result = ensure_async(async_func)
        assert result is async_func


class TestFlowBuilderEdgeCases:
    """Test FlowBuilder edge cases."""

    @pytest.mark.asyncio
    async def test_to_legacy_method(self):
        """Test that 'to' is an alias for 'sink'."""
        builder = flow("Test")
        results = []

        # Using 'to' instead of 'sink'
        await builder.source([1, 2, 3], int).to(results.append).execute()

        assert results == [1, 2, 3]

    @pytest.mark.asyncio
    async def test_tap_functionality(self):
        """Test tap for side effects."""
        builder = flow("Test")
        tapped = []
        results = []

        await (
            builder.source([1, 2, 3], int)
            .tap(tapped.append)
            .to(results.append)
            .execute()
        )

        assert tapped == [1, 2, 3]
        assert results == [1, 2, 3]

    def test_merge_with_type_mismatch_error(self):
        """Test merging flows with mismatched types."""
        builder1 = flow("Flow1").source([1, 2], int)
        builder2 = flow("Flow2").source(["a", "b"], str)

        with pytest.raises(TypeError, match="Type mismatch"):
            builder1.merge_with(builder2)
