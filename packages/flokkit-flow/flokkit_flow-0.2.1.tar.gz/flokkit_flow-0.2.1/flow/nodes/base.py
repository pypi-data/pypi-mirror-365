"""Base node class for all flow-based programming nodes."""

from __future__ import annotations

from abc import ABC, abstractmethod
import logging
from typing import TYPE_CHECKING, Any, Dict, Optional, Type

if TYPE_CHECKING:
    from ..materializer import ExecutableGraph

from ..core import DEFAULT_QUEUE_SIZE, Port, QueueFullStrategy, T

logger = logging.getLogger(__name__)


class Node(ABC):
    """Base class for all FBP nodes."""

    def __init__(self, name: str):
        self.name = name
        self._input_ports: Dict[str, Port[Any]] = {}
        self._output_ports: Dict[str, Port[Any]] = {}
        self._completed = False  # Track if node has completed processing
        self._error: Optional[Exception] = None
        self._graph: Optional[ExecutableGraph] = None  # Reference to containing graph
        self._setup_ports()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name})"

    def __str__(self) -> str:
        return self.name

    @abstractmethod
    def _setup_ports(self) -> None:
        """Setup input and output ports for this node."""

    @abstractmethod
    async def process(self) -> None:
        """Process data. Must be implemented by subclasses."""

    def add_input_port(
        self,
        name: str,
        data_type: Type[T],
        queue_size: int = DEFAULT_QUEUE_SIZE,
        full_strategy: QueueFullStrategy = QueueFullStrategy.BLOCK,
    ) -> Port[T]:
        """Add an input port to this node."""
        port: Port[T] = Port(name, True, data_type, self, queue_size, full_strategy)
        self._input_ports[name] = port
        return port

    def add_output_port(self, name: str, data_type: Type[T]) -> Port[T]:
        """Add an output port to this node."""
        port: Port[T] = Port(name, False, data_type, self)
        self._output_ports[name] = port
        return port

    def get_input_port(self, name: str) -> Port[Any]:
        """Get an input port by name."""
        return self._input_ports[name]

    def get_output_port(self, name: str) -> Port[Any]:
        """Get an output port by name."""
        return self._output_ports[name]

    async def initialize(self) -> None:
        """Initialize all ports and perform setup. Can be overridden."""
        for port in self._input_ports.values():
            await port.initialize()
        await self.on_start()

    async def on_start(self) -> None:
        """Called when node starts. Override for custom initialization."""

    async def on_stop(self) -> None:
        """Called when node stops. Override for cleanup."""

    async def on_error(self, error: Exception) -> None:
        """Called when an error occurs. Override for custom error handling."""
        self._error = error
        logger.error(f"Error in node {self.name}: {error}")

    async def on_complete(self) -> None:
        """Called when node completes all processing. Override for custom completion logic."""
        self._completed = True

    def signal_completion(self) -> None:
        """Signal that this node has completed and won't produce more data."""
        self._completed = True
