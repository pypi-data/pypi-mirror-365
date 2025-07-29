"""Unified node implementation that replaces all specialized node types."""

from abc import ABC, abstractmethod
import asyncio
from enum import Enum, auto
from typing import Any, AsyncIterator, Awaitable, Callable, Optional, Type

from ..core import DEFAULT_QUEUE_SIZE, Port, QueueFullStrategy, R, T
from ..middleware import MiddlewareChain, ProcessingContext
from .base import Node


class NodeType(Enum):
    """Supported node behavior types."""

    SOURCE = auto()
    SINK = auto()
    TRANSFORM = auto()
    FILTER = auto()
    SPLIT = auto()
    MERGE = auto()


class NodeBehavior(ABC):
    """Base class for node behaviors."""

    @abstractmethod
    def setup_ports(self, node: "UnifiedNode") -> None:
        """Setup input/output ports for this behavior."""

    @abstractmethod
    async def process(self, node: "UnifiedNode") -> None:
        """Process data for this behavior."""


class SourceBehavior(NodeBehavior):
    """Behavior for source nodes."""

    def __init__(self, source: AsyncIterator[T], output_type: Type[T]):
        self.source = source
        self.output_type = output_type
        self.output_port: Optional[Port[Any]] = None

    def setup_ports(self, node: "UnifiedNode") -> None:
        self.output_port = node.add_output_port("out", self.output_type)

    async def process(self, node: "UnifiedNode") -> None:
        if node._completed:
            return
        assert self.output_port is not None
        try:
            value = await self.source.__anext__()
            await self.output_port.send(value)
        except StopAsyncIteration:
            await node.on_complete()


class SinkBehavior(NodeBehavior):
    """Behavior for sink nodes."""

    def __init__(
        self,
        consumer_func: Callable[[T], Awaitable[None]],
        input_type: Type[T],
        queue_size: int = DEFAULT_QUEUE_SIZE,
        full_strategy: QueueFullStrategy = QueueFullStrategy.BLOCK,
    ):
        self.consumer_func = consumer_func
        self.input_type = input_type
        self.queue_size = queue_size
        self.full_strategy = full_strategy
        self.input_port: Optional[Port[Any]] = None

    def setup_ports(self, node: "UnifiedNode") -> None:
        self.input_port = node.add_input_port(
            "in", self.input_type, self.queue_size, self.full_strategy
        )

    async def process(self, node: "UnifiedNode") -> None:
        assert self.input_port is not None
        value = await self.input_port.receive()
        if value is not None:
            await self.consumer_func(value)
        else:
            # Input exhausted, signal completion
            node.signal_completion()


class TransformBehavior(NodeBehavior):
    """Behavior for transform nodes."""

    def __init__(
        self,
        transform_func: Callable[[T], Awaitable[R]],
        input_type: Type[T],
        output_type: Type[R],
        queue_size: int = DEFAULT_QUEUE_SIZE,
        full_strategy: QueueFullStrategy = QueueFullStrategy.BLOCK,
    ):
        self.transform_func = transform_func
        self.input_type = input_type
        self.output_type = output_type
        self.queue_size = queue_size
        self.full_strategy = full_strategy
        self.input_port: Optional[Port[Any]] = None
        self.output_port: Optional[Port[Any]] = None

    def setup_ports(self, node: "UnifiedNode") -> None:
        self.input_port = node.add_input_port(
            "in", self.input_type, self.queue_size, self.full_strategy
        )
        self.output_port = node.add_output_port("out", self.output_type)

    async def process(self, node: "UnifiedNode") -> None:
        assert self.input_port is not None
        assert self.output_port is not None
        value = await self.input_port.receive()
        if value is not None:
            result = await self.transform_func(value)
            await self.output_port.send(result)
        else:
            # Input exhausted, signal completion
            node.signal_completion()


class FilterBehavior(NodeBehavior):
    """Behavior for filter nodes."""

    def __init__(
        self,
        predicate_func: Callable[[T], Awaitable[bool]],
        data_type: Type[T],
        queue_size: int = DEFAULT_QUEUE_SIZE,
        full_strategy: QueueFullStrategy = QueueFullStrategy.BLOCK,
    ):
        self.predicate_func = predicate_func
        self.data_type = data_type
        self.queue_size = queue_size
        self.full_strategy = full_strategy
        self.input_port: Optional[Port[Any]] = None
        self.output_port: Optional[Port[Any]] = None

    def setup_ports(self, node: "UnifiedNode") -> None:
        self.input_port = node.add_input_port(
            "in", self.data_type, self.queue_size, self.full_strategy
        )
        self.output_port = node.add_output_port("out", self.data_type)

    async def process(self, node: "UnifiedNode") -> None:
        assert self.input_port is not None
        assert self.output_port is not None
        value = await self.input_port.receive()
        if value is not None:
            if await self.predicate_func(value):
                await self.output_port.send(value)
        else:
            # Input exhausted, signal completion
            node.signal_completion()


class SplitBehavior(NodeBehavior):
    """Behavior for split nodes."""

    def __init__(
        self,
        data_type: Type[T],
        num_outputs: int = 2,
        queue_size: int = DEFAULT_QUEUE_SIZE,
        full_strategy: QueueFullStrategy = QueueFullStrategy.BLOCK,
    ):
        self.data_type = data_type
        self.num_outputs = num_outputs
        self.queue_size = queue_size
        self.full_strategy = full_strategy

    def setup_ports(self, node: "UnifiedNode") -> None:
        node.add_input_port("in", self.data_type, self.queue_size, self.full_strategy)
        for i in range(self.num_outputs):
            node.add_output_port(f"out{i}", self.data_type)

    async def process(self, node: "UnifiedNode") -> None:
        value = await node.get_input_port("in").receive()
        if value is not None:
            tasks = []
            for i in range(self.num_outputs):
                tasks.append(node.get_output_port(f"out{i}").send(value))
            await asyncio.gather(*tasks)
        else:
            # Input exhausted, signal completion
            node.signal_completion()


class MergeBehavior(NodeBehavior):
    """Behavior for merge nodes."""

    def __init__(
        self,
        data_type: Type[T],
        num_inputs: int = 2,
        queue_size: int = DEFAULT_QUEUE_SIZE,
        full_strategy: QueueFullStrategy = QueueFullStrategy.BLOCK,
    ):
        self.data_type = data_type
        self.num_inputs = num_inputs
        self.queue_size = queue_size
        self.full_strategy = full_strategy

    def setup_ports(self, node: "UnifiedNode") -> None:
        for i in range(self.num_inputs):
            node.add_input_port(
                f"in{i}", self.data_type, self.queue_size, self.full_strategy
            )
        node.add_output_port("out", self.data_type)

    async def process(self, node: "UnifiedNode") -> None:
        # Create receive tasks for all input ports
        receive_tasks = {}
        for i in range(self.num_inputs):
            port = node.get_input_port(f"in{i}")
            receive_tasks[i] = asyncio.create_task(port.receive())

        # Continue processing while any tasks remain
        while receive_tasks:
            done, pending = await asyncio.wait(
                receive_tasks.values(), return_when=asyncio.FIRST_COMPLETED
            )

            # Process completed tasks
            for task in done:
                value = task.result()

                # Find which port this task belongs to
                port_idx = None
                for idx, t in receive_tasks.items():
                    if t == task:
                        port_idx = idx
                        break

                if value is None:
                    # This port is exhausted, remove it
                    if port_idx is not None:
                        del receive_tasks[port_idx]
                else:
                    # Forward the value
                    await node.get_output_port("out").send(value)

                    # Create a new receive task for this port
                    if port_idx is not None:
                        port = node.get_input_port(f"in{port_idx}")
                        receive_tasks[port_idx] = asyncio.create_task(port.receive())

        # All inputs exhausted, signal completion
        node.signal_completion()


class UnifiedNode(Node):
    """Unified node that can behave as any node type based on behavior composition."""

    def __init__(self, name: str, behavior: NodeBehavior):
        self.behavior = behavior
        self.node_type = self._determine_node_type(behavior)
        self.middleware = MiddlewareChain()
        super().__init__(name)

    def _determine_node_type(self, behavior: NodeBehavior) -> NodeType:
        """Determine node type from behavior class."""
        behavior_map = {
            SourceBehavior: NodeType.SOURCE,
            SinkBehavior: NodeType.SINK,
            TransformBehavior: NodeType.TRANSFORM,
            FilterBehavior: NodeType.FILTER,
            SplitBehavior: NodeType.SPLIT,
            MergeBehavior: NodeType.MERGE,
        }
        return behavior_map.get(type(behavior), NodeType.TRANSFORM)

    def _setup_ports(self) -> None:
        """Delegate port setup to behavior."""
        self.behavior.setup_ports(self)

    async def process(self) -> None:
        """Delegate processing to behavior with middleware support."""
        context = ProcessingContext(
            node_name=self.name, node_type=self.node_type.name.lower()
        )

        async def behavior_handler(ctx: ProcessingContext) -> Any:
            return await self.behavior.process(self)

        await self.middleware.execute(context, behavior_handler)

    def __repr__(self) -> str:
        return f"{self.node_type.name.title()}Node({self.name})"


# Factory functions for backwards compatibility
def create_source_node(
    name: str, source: AsyncIterator[T], output_type: Type[T]
) -> UnifiedNode:
    """Create a source node using unified interface."""
    return UnifiedNode(name, SourceBehavior(source, output_type))


def create_sink_node(
    name: str,
    consumer_func: Callable[[T], Awaitable[None]],
    input_type: Type[T],
    is_blocking: bool = False,
    queue_size: int = DEFAULT_QUEUE_SIZE,
    full_strategy: QueueFullStrategy = QueueFullStrategy.BLOCK,
) -> UnifiedNode:
    """Create a sink node using unified interface."""
    return UnifiedNode(
        name, SinkBehavior(consumer_func, input_type, queue_size, full_strategy)
    )


def create_transform_node(
    name: str,
    transform_func: Callable[[T], Awaitable[R]],
    input_type: Type[T],
    output_type: Type[R],
    is_blocking: bool = False,
    queue_size: int = DEFAULT_QUEUE_SIZE,
    full_strategy: QueueFullStrategy = QueueFullStrategy.BLOCK,
) -> UnifiedNode:
    """Create a transform node using unified interface."""
    return UnifiedNode(
        name,
        TransformBehavior(
            transform_func, input_type, output_type, queue_size, full_strategy
        ),
    )


def create_filter_node(
    name: str,
    predicate_func: Callable[[T], Awaitable[bool]],
    data_type: Type[T],
    is_blocking: bool = False,
    queue_size: int = DEFAULT_QUEUE_SIZE,
    full_strategy: QueueFullStrategy = QueueFullStrategy.BLOCK,
) -> UnifiedNode:
    """Create a filter node using unified interface."""
    return UnifiedNode(
        name, FilterBehavior(predicate_func, data_type, queue_size, full_strategy)
    )


def create_split_node(
    name: str,
    data_type: Type[T],
    num_outputs: int = 2,
    queue_size: int = DEFAULT_QUEUE_SIZE,
    full_strategy: QueueFullStrategy = QueueFullStrategy.BLOCK,
) -> UnifiedNode:
    """Create a split node using unified interface."""
    return UnifiedNode(
        name, SplitBehavior(data_type, num_outputs, queue_size, full_strategy)
    )


def create_merge_node(
    name: str,
    data_type: Type[T],
    num_inputs: int = 2,
    queue_size: int = DEFAULT_QUEUE_SIZE,
    full_strategy: QueueFullStrategy = QueueFullStrategy.BLOCK,
) -> UnifiedNode:
    """Create a merge node using unified interface."""
    return UnifiedNode(
        name, MergeBehavior(data_type, num_inputs, queue_size, full_strategy)
    )
