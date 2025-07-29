"""Port and Connection classes for data flow between nodes."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import TYPE_CHECKING, Generic, List, Optional, Type

from .strategies import STRATEGY_MAP
from .types import DEFAULT_QUEUE_SIZE, QueueFullStrategy, T

if TYPE_CHECKING:
    from ..nodes.base import Node


@dataclass
class Port(Generic[T]):
    """Represents an input or output port with type information."""

    name: str
    is_input: bool
    data_type: Type[T]
    node: Optional[Node] = None
    queue_size: int = DEFAULT_QUEUE_SIZE
    full_strategy: QueueFullStrategy = QueueFullStrategy.BLOCK

    def __post_init__(self):
        self._connections: List[Connection[T]] = []
        self._queue: Optional[asyncio.Queue[T]] = None
        self._strategy = STRATEGY_MAP[self.full_strategy]

    async def initialize(self):
        """Initialize the port's queue."""
        if self.is_input:
            self._queue = asyncio.Queue(maxsize=self.queue_size)

    def connect_to(self, other: Port[T]) -> Connection[T]:
        """Create a connection from this port to another port."""
        if self.is_input:
            raise ValueError(
                f"Can only connect from output ports, {self.name} is an input port"
            )
        if not other.is_input:
            raise ValueError(
                f"Can only connect to input ports, {other.name} is an output port"
            )
        if self.data_type != other.data_type:
            raise TypeError(f"Type mismatch: {self.data_type} != {other.data_type}")

        connection = Connection(self, other)
        self._connections.append(connection)
        other._connections.append(connection)
        return connection

    async def send(self, value: T) -> None:
        """Send a value through this output port."""
        if self.is_input:
            raise ValueError("Can only send from output ports")

        # Send to all connected input ports
        tasks = []
        for conn in self._connections:
            tasks.append(conn.transfer(value))
        if tasks:
            await asyncio.gather(*tasks)

    async def receive(self, timeout: Optional[float] = None) -> Optional[T]:
        """Receive a value from this input port."""
        if not self.is_input:
            raise ValueError("Can only receive from input ports")
        if not self._queue:
            raise RuntimeError("Port not initialized")

        try:
            if timeout is not None:
                value = await asyncio.wait_for(self._queue.get(), timeout)
            else:
                value = await self._queue.get()

            return value
        except asyncio.TimeoutError:
            return None

    def has_data(self) -> bool:
        """Check if this input port has data available."""
        return bool(self._queue and not self._queue.empty())

    def is_full(self) -> bool:
        """Check if this input port's queue is full."""
        return bool(self._queue and self._queue.full())

    def __repr__(self) -> str:
        direction = "input" if self.is_input else "output"
        node_name = self.node.name if self.node else "unconnected"
        return f"Port({self.name}, {direction}, {self.data_type.__name__}, node={node_name})"


@dataclass
class Connection(Generic[T]):
    """Represents a connection between two ports."""

    source: Port[T]
    target: Port[T]

    def __repr__(self) -> str:
        source_node = self.source.node.name if self.source.node else "unknown"
        target_node = self.target.node.name if self.target.node else "unknown"
        return f"Connection({source_node}.{self.source.name} -> {target_node}.{self.target.name})"

    async def transfer(self, value: T) -> None:
        """Transfer a value through this connection."""
        if not self.target._queue:
            raise RuntimeError("Target port not initialized")

        node_name = (
            f"{self.target.node.name}.{self.target.name}"
            if self.target.node
            else self.target.name
        )
        await self.target._strategy.put(self.target._queue, value, node_name)
