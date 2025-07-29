"""Core type definitions for the flow-based programming framework."""

from enum import Enum, auto
from typing import TypeVar

# Type variables
T = TypeVar("T")
S = TypeVar("S")
R = TypeVar("R")

# Constants
DEFAULT_QUEUE_SIZE = 1000


class QueueFullStrategy(Enum):
    """Strategies for handling full queues.

    Examples:
        Default strategy blocks when queue is full:

        >>> QueueFullStrategy.BLOCK.name
        'BLOCK'

        Use in flow configuration:

        >>> from flow import flow, QueueFullStrategy
        >>> builder = (
        ...     flow()
        ...     .source([1, 2], int)
        ...     .transform(
        ...         lambda x: x * 2,
        ...         int,
        ...         queue_size=10,
        ...         full_strategy=QueueFullStrategy.DROP_OLD,
        ...     )
        ... )

        Available strategies:

        >>> [s.name for s in QueueFullStrategy]
        ['BLOCK', 'DROP_NEW', 'DROP_OLD', 'ERROR']
    """

    BLOCK = auto()  # Block until space available (default)
    DROP_NEW = auto()  # Drop new items
    DROP_OLD = auto()  # Drop oldest items
    ERROR = auto()  # Raise an error


class ShutdownMode(Enum):
    """Different modes for shutting down the graph.

    Examples:
        Available shutdown modes:

        >>> [mode.name for mode in ShutdownMode]
        ['GRACEFUL', 'IMMEDIATE', 'FORCE']

        Default is graceful shutdown:

        >>> ShutdownMode.GRACEFUL.name
        'GRACEFUL'
    """

    GRACEFUL = auto()  # Wait for queues to drain
    IMMEDIATE = auto()  # Stop processing but cleanup
    FORCE = auto()  # Cancel immediately
