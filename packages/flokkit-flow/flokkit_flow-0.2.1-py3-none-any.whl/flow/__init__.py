"""
Flow-Based Programming (FBP) implementation in Python.

This module provides a complete FBP framework supporting:
- Type-safe connections between nodes
- Async-only execution
- Bounded queues with backpressure
- Sources, sinks, transforms, and other node types
- Automatic graph execution with proper scheduling
- Clean separation of concerns for flow-based programming
"""

# Core types and enums
from .core import DEFAULT_QUEUE_SIZE, Connection, Port, QueueFullStrategy, ShutdownMode

# Utility functions
from .factory import ensure_async

# New immutable API
from .flow_builder import FlowBuilder, FlowBuilderChain, flow
from .materializer import ExecutableGraph

# Middleware system
from .middleware import (
    LoggingMiddleware,
    MetricsMiddleware,
    Middleware,
    ProcessingContext,
    RetryMiddleware,
    ThrottleMiddleware,
)

# Base node type (for advanced usage)
from .nodes import Node

# AsyncIterator adapters for advanced usage
from .nodes.source import (
    AsyncCallableSource,
    AsyncIteratorAdapter,
    AsyncIteratorSource,
    SyncCallableSource,
    SyncIteratorSource,
)

# Shell command integration
from .shell import ShellCommand, shell_sink, shell_source, shell_transform

__version__ = "0.2.0"

__all__ = [
    # Core types
    "QueueFullStrategy",
    "ShutdownMode",
    "DEFAULT_QUEUE_SIZE",
    "Port",
    "Connection",
    # Base node type (for advanced usage)
    "Node",
    # Primary API
    "flow",
    "FlowBuilder",
    "FlowBuilderChain",
    # Advanced API for custom patterns
    "ExecutableGraph",
    # Utility functions
    "ensure_async",
    # AsyncIterator adapters for advanced usage
    "AsyncIteratorAdapter",
    "AsyncIteratorSource",
    "SyncIteratorSource",
    "AsyncCallableSource",
    "SyncCallableSource",
    # Middleware system
    "Middleware",
    "LoggingMiddleware",
    "MetricsMiddleware",
    "ThrottleMiddleware",
    "RetryMiddleware",
    "ProcessingContext",
    # Shell command integration
    "ShellCommand",
    "shell_source",
    "shell_transform",
    "shell_sink",
]
