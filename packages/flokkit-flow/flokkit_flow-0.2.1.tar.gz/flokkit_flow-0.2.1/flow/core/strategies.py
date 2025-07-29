"""Queue handling strategies for the flow-based programming framework."""

from abc import ABC, abstractmethod
import asyncio
import logging
from typing import TypeVar

from .types import QueueFullStrategy

logger = logging.getLogger(__name__)
T = TypeVar("T")


class QueueStrategy(ABC):
    """Abstract base for queue strategies."""

    @abstractmethod
    async def put(self, queue: asyncio.Queue[T], value: T, node_name: str) -> None:
        """Put a value in the queue according to strategy."""


class BlockingStrategy(QueueStrategy):
    """Block until space is available."""

    async def put(self, queue: asyncio.Queue[T], value: T, node_name: str) -> None:
        await queue.put(value)


class DropNewStrategy(QueueStrategy):
    """Drop new items when queue is full."""

    async def put(self, queue: asyncio.Queue[T], value: T, node_name: str) -> None:
        try:
            queue.put_nowait(value)
        except asyncio.QueueFull:
            logger.warning(f"Dropping item on full queue: {node_name}")


class DropOldStrategy(QueueStrategy):
    """Drop oldest items to make room."""

    async def put(self, queue: asyncio.Queue[T], value: T, node_name: str) -> None:
        if queue.full():
            queue.get_nowait()  # Drop oldest
        await queue.put(value)


class ErrorStrategy(QueueStrategy):
    """Raise error when queue is full."""

    async def put(self, queue: asyncio.Queue[T], value: T, node_name: str) -> None:
        try:
            queue.put_nowait(value)
        except asyncio.QueueFull:
            raise RuntimeError(f"Queue full: {node_name}")


# Map enum to strategy instances
STRATEGY_MAP = {
    QueueFullStrategy.BLOCK: BlockingStrategy(),
    QueueFullStrategy.DROP_NEW: DropNewStrategy(),
    QueueFullStrategy.DROP_OLD: DropOldStrategy(),
    QueueFullStrategy.ERROR: ErrorStrategy(),
}
