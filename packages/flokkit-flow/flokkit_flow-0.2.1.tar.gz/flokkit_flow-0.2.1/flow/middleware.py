"""Middleware system for flow processing."""

from __future__ import annotations

from abc import ABC, abstractmethod
import asyncio
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Awaitable, Callable, Dict, Optional


class MiddlewareHook(Enum):
    """Points where middleware can hook into processing."""

    BEFORE_PROCESS = "before_process"
    AFTER_PROCESS = "after_process"
    ON_ERROR = "on_error"
    ON_COMPLETE = "on_complete"


@dataclass
class ProcessingContext:
    """Context passed to middleware with processing information.

    Examples:
        Create a context:

        >>> ctx = ProcessingContext(
        ...     node_name="transform_1", node_type="transform", input_value=42
        ... )
        >>> ctx.node_name
        'transform_1'
        >>> ctx.metadata
        {}

        Add metadata:

        >>> ctx.metadata["start_time"] = 123.45
        >>> ctx.metadata["start_time"]
        123.45
    """

    node_name: str
    node_type: str
    input_value: Any = None
    output_value: Any = None
    error: Optional[Exception] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class Middleware(ABC):
    """Base class for flow middleware.

    Examples:
        Custom middleware implementation:

        >>> class CounterMiddleware(Middleware):
        ...     def __init__(self):
        ...         self.count = 0
        ...
        ...     async def process(self, context, next_middleware):
        ...         self.count += 1
        ...         return await next_middleware(context)

        >>> import asyncio
        >>> counter = CounterMiddleware()
        >>> async def handler(ctx):
        ...     return "done"
        >>> result = asyncio.run(
        ...     counter.process(ProcessingContext("test", "transform"), handler)
        ... )
        >>> counter.count
        1
    """

    @abstractmethod
    async def process(
        self,
        context: ProcessingContext,
        next_middleware: Callable[[ProcessingContext], Awaitable[Any]],
    ) -> Any:
        """Process the context and call next middleware in chain."""


class LoggingMiddleware(Middleware):
    """Middleware that logs processing events.

    Examples:
        Basic usage:

        >>> logger = LoggingMiddleware(log_inputs=True, log_outputs=False)
        >>> logger.log_inputs
        True
        >>> logger.log_outputs
        False

        In a flow (output would go to console):

        >>> import asyncio
        >>> from flow import flow
        >>> async def example():
        ...     logger = LoggingMiddleware()
        ...     results = []
        ...     await (
        ...         flow()
        ...         .with_middleware(logger)
        ...         .source([1, 2], int)
        ...         .sink(results.append)
        ...         .execute(duration=0.5)
        ...     )
        ...     return results
        >>> # asyncio.run(example())  # Would log to console
    """

    def __init__(self, log_inputs: bool = True, log_outputs: bool = True):
        self.log_inputs = log_inputs
        self.log_outputs = log_outputs

    async def process(
        self,
        context: ProcessingContext,
        next_middleware: Callable[[ProcessingContext], Awaitable[Any]],
    ) -> Any:
        if self.log_inputs and context.input_value is not None:
            print(f"[{context.node_name}] Input: {context.input_value}")

        try:
            result = await next_middleware(context)

            if self.log_outputs and context.output_value is not None:
                print(f"[{context.node_name}] Output: {context.output_value}")

            return result
        except Exception as e:
            print(f"[{context.node_name}] Error: {e}")
            raise


class MetricsMiddleware(Middleware):
    """Middleware that collects processing metrics.

    Examples:
        Track metrics across a flow:

        >>> import asyncio
        >>> from flow import flow
        >>> async def example():
        ...     metrics = MetricsMiddleware()
        ...     results = []
        ...
        ...     await (
        ...         flow()
        ...         .with_middleware(metrics)
        ...         .source([1, 2, 3], int)
        ...         .filter(lambda x: x > 1)
        ...         .sink(results.append)
        ...         .execute(duration=0.5)
        ...     )
        ...
        ...     return metrics.get_metrics()
        >>> stats = asyncio.run(example())
        >>> stats["total_processed"] > 0  # Should have processed some items
        True
        >>> stats["total_errors"]
        0
    """

    def __init__(self):
        self.process_count = 0
        self.error_count = 0
        self.node_metrics = {}

    async def process(
        self,
        context: ProcessingContext,
        next_middleware: Callable[[ProcessingContext], Awaitable[Any]],
    ) -> Any:
        node_name = context.node_name
        if node_name not in self.node_metrics:
            self.node_metrics[node_name] = {"processed": 0, "errors": 0}

        self.process_count += 1
        self.node_metrics[node_name]["processed"] += 1

        try:
            return await next_middleware(context)
        except Exception:
            self.error_count += 1
            self.node_metrics[node_name]["errors"] += 1
            raise

    def get_metrics(self) -> Dict[str, Any]:
        """Get collected metrics."""
        return {
            "total_processed": self.process_count,
            "total_errors": self.error_count,
            "by_node": self.node_metrics.copy(),
        }


class ThrottleMiddleware(Middleware):
    """Middleware that adds delays for rate limiting.

    Examples:
        Create with 100ms delay:

        >>> throttle = ThrottleMiddleware(0.1)
        >>> throttle.delay_seconds
        0.1

        Use in a flow to limit processing rate:

        >>> import asyncio
        >>> import time
        >>> from flow import flow
        >>> async def example():
        ...     throttle = ThrottleMiddleware(0.05)  # 50ms delay
        ...     results = []
        ...
        ...     start = time.time()
        ...     await (
        ...         flow()
        ...         .source([1, 2], int)
        ...         .with_middleware(throttle)
        ...         .sink(results.append)
        ...         .execute(duration=1.0)
        ...     )
        ...     elapsed = time.time() - start
        ...
        ...     return len(results), elapsed > 0.1  # Should take > 100ms
        >>> count, slow_enough = asyncio.run(example())
        >>> count
        2
        >>> slow_enough
        True
    """

    def __init__(self, delay_seconds: float):
        self.delay_seconds = delay_seconds

    async def process(
        self,
        context: ProcessingContext,
        next_middleware: Callable[[ProcessingContext], Awaitable[Any]],
    ) -> Any:
        result = await next_middleware(context)
        await asyncio.sleep(self.delay_seconds)
        return result


class RetryMiddleware(Middleware):
    """Middleware that retries failed operations.

    Examples:
        Create with custom settings:

        >>> retry = RetryMiddleware(max_attempts=5, backoff=0.1)
        >>> retry.max_attempts
        5
        >>> retry.backoff
        0.1

        Usage in a flow:

        >>> import asyncio
        >>> from flow import flow
        >>> # The retry middleware can be used to handle transient failures
        >>> retry = RetryMiddleware(max_attempts=3, backoff=0.1)
        >>> # In practice, it would retry operations that fail temporarily
        >>> # For example, network requests or database operations
    """

    def __init__(self, max_attempts: int = 3, backoff: float = 1.0):
        self.max_attempts = max_attempts
        self.backoff = backoff

    async def process(
        self,
        context: ProcessingContext,
        next_middleware: Callable[[ProcessingContext], Awaitable[Any]],
    ) -> Any:
        last_error = None

        for attempt in range(self.max_attempts):
            try:
                return await next_middleware(context)
            except Exception as e:
                last_error = e
                if attempt < self.max_attempts - 1:
                    delay = self.backoff * (2**attempt)  # Exponential backoff
                    await asyncio.sleep(delay)
                    continue
                break

        # All attempts failed
        if last_error is not None:
            raise last_error
        raise Exception("Retry failed with no error captured")


class MiddlewareChain:
    """Manages a chain of middleware.

    Examples:
        Create and manage a chain:

        >>> chain = MiddlewareChain()
        >>> len(chain.middlewares)
        0

        Add middleware:

        >>> logger = LoggingMiddleware()
        >>> metrics = MetricsMiddleware()
        >>> chain.add(logger)
        >>> chain.add(metrics)
        >>> len(chain.middlewares)
        2

        Remove middleware:

        >>> chain.remove(logger)
        True
        >>> len(chain.middlewares)
        1
        >>> chain.remove(logger)  # Already removed
        False

        Clear all:

        >>> chain.clear()
        >>> len(chain.middlewares)
        0
    """

    def __init__(self):
        self.middlewares: list[Middleware] = []

    def add(self, middleware: Middleware) -> None:
        """Add middleware to the chain."""
        self.middlewares.append(middleware)

    def remove(self, middleware: Middleware) -> bool:
        """Remove middleware from the chain."""
        try:
            self.middlewares.remove(middleware)
            return True
        except ValueError:
            return False

    def clear(self) -> None:
        """Remove all middleware."""
        self.middlewares.clear()

    async def execute(
        self,
        context: ProcessingContext,
        final_handler: Callable[[ProcessingContext], Awaitable[Any]],
    ) -> Any:
        """Execute the middleware chain."""
        if not self.middlewares:
            return await final_handler(context)

        # Build the chain from the end backwards
        def build_chain(index: int) -> Callable[[ProcessingContext], Awaitable[Any]]:
            if index >= len(self.middlewares):
                return final_handler

            middleware = self.middlewares[index]
            next_handler = build_chain(index + 1)

            async def middleware_wrapper(ctx: ProcessingContext) -> Any:
                return await middleware.process(ctx, next_handler)

            return middleware_wrapper

        handler = build_chain(0)
        return await handler(context)
