"""Flow builder that uses object references instead of strings."""

from __future__ import annotations

from dataclasses import dataclass
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Generic,
    List,
    Optional,
    Type,
)

if TYPE_CHECKING:
    from .materializer import ExecutableGraph

from .core import DEFAULT_QUEUE_SIZE, QueueFullStrategy, R, T
from .factory import ensure_async
from .middleware import Middleware
from .nodes import Node
from .nodes.source import AsyncIteratorAdapter
from .nodes.unified import (
    create_filter_node,
    create_merge_node,
    create_sink_node,
    create_source_node,
    create_split_node,
    create_transform_node,
)


@dataclass
class PendingConnection:
    """A connection to be made between ports."""

    from_node: Node
    from_port_name: str
    to_node: Node
    to_port_name: str


class FlowBuilder(Generic[T]):
    """Builder for creating flow graphs with fluent interface.

    Examples:
        Basic pipeline:

        >>> import asyncio
        >>> from flow import flow
        >>> async def example():
        ...     results = []
        ...     await (
        ...         flow()
        ...         .source([1, 2, 3], int)
        ...         .transform(lambda x: x * 2, int)
        ...         .filter(lambda x: x > 2, int)
        ...         .sink(results.append)
        ...         .execute(duration=0.5)
        ...     )
        ...     return results
        >>> asyncio.run(example())
        [4, 6]

        Using tap for side effects:

        >>> async def example_tap():
        ...     tapped = []
        ...     results = []
        ...     await (
        ...         flow()
        ...         .source([1, 2, 3], int)
        ...         .tap(tapped.append)  # Side effect without consuming
        ...         .transform(lambda x: x * 10, int)
        ...         .sink(results.append)
        ...         .execute(duration=0.5)
        ...     )
        ...     return tapped, results
        >>> tapped, results = asyncio.run(example_tap())
        >>> tapped
        [1, 2, 3]
        >>> results
        [10, 20, 30]
    """

    def __init__(
        self,
        namespace: Optional[str] = None,
        current_node: Optional[Node] = None,
        current_port_name: str = "out",
        current_port_type: Optional[Type[T]] = None,
    ):
        self.namespace = namespace or "flow"
        self._nodes: List[Node] = []
        self._connections: List[PendingConnection] = []
        self._node_counter = 0

        # Track current position for chaining
        self._current_node = current_node
        self._current_port_name = current_port_name
        self._current_port_type = current_port_type

        # Optional debug names for nodes
        self._debug_names: Dict[Node, str] = {}

        # Pending middleware to apply to new nodes
        self._pending_middleware: tuple[Middleware, ...] = ()

    def _next_node_name(self, prefix: str) -> str:
        """Generate unique node name for debugging."""
        self._node_counter += 1
        return f"{prefix}_{self._node_counter}"

    def source(
        self, source: Any, output_type: Type[R], name: Optional[str] = None
    ) -> FlowBuilder[R]:
        """Add source node.

        Args:
            source: Data source - can be list, generator, iterator, or async iterator
            output_type: Type of items produced by the source
            name: Optional debug name for the node

        Returns:
            New FlowBuilder instance for chaining

        Examples:
            From a list:

            >>> builder = flow().source([1, 2, 3], int)
            >>> builder._current_port_type
            <class 'int'>

            From a generator:

            >>> def gen():
            ...     yield 1
            ...     yield 2
            >>> builder = flow().source(gen(), int)

            From a lambda:

            >>> builder = flow().source(lambda: range(5), int)

            From an async generator:

            >>> async def async_gen():
            ...     for i in range(3):
            ...         yield i
            >>> builder = flow().source(async_gen(), int)
        """
        debug_name = name or self._next_node_name("source")

        # Wrap source if needed
        if not hasattr(source, "__aiter__"):
            source = AsyncIteratorAdapter(source)

        node = create_source_node(debug_name, source, output_type)

        # Apply pending middleware to the node
        if hasattr(node, "middleware"):
            for middleware in self._pending_middleware:
                node.middleware.add(middleware)

        self._nodes.append(node)
        self._debug_names[node] = debug_name

        # Create new builder with current state
        new_builder = FlowBuilder(
            namespace=self.namespace,
            current_node=node,
            current_port_name="out",
            current_port_type=output_type,
        )
        new_builder._nodes = self._nodes.copy()
        new_builder._connections = self._connections.copy()
        new_builder._node_counter = self._node_counter
        new_builder._debug_names = self._debug_names.copy()

        return new_builder

    def transform(
        self,
        func: Callable[[T], R],
        output_type: Type[R],
        name: Optional[str] = None,
        queue_size: int = DEFAULT_QUEUE_SIZE,
        full_strategy: QueueFullStrategy = QueueFullStrategy.BLOCK,
    ) -> FlowBuilder[R]:
        """Add transform node.

        Args:
            func: Function to transform each item
            output_type: Type of transformed items
            name: Optional debug name for the node
            queue_size: Size of the input queue
            full_strategy: Strategy when queue is full

        Returns:
            New FlowBuilder instance for chaining

        Examples:
            Simple transformation:

            >>> import asyncio
            >>> async def example():
            ...     results = []
            ...     await (
            ...         flow()
            ...         .source([1, 2, 3], int)
            ...         .transform(lambda x: x * 2, int)
            ...         .sink(results.append)
            ...         .execute(duration=0.5)
            ...     )
            ...     return results
            >>> asyncio.run(example())
            [2, 4, 6]

            Async transformation:

            >>> async def async_double(x):
            ...     await asyncio.sleep(0.001)  # Simulate async work
            ...     return x * 2
            >>> async def example_async():
            ...     results = []
            ...     await (
            ...         flow()
            ...         .source([1, 2], int)
            ...         .transform(async_double, int)
            ...         .sink(results.append)
            ...         .execute(duration=0.5)
            ...     )
            ...     return results
            >>> asyncio.run(example_async())
            [2, 4]
        """
        if not self._current_node or self._current_port_type is None:
            raise ValueError("No source to transform from")

        debug_name = name or self._next_node_name("transform")

        async_func = ensure_async(func)
        node = create_transform_node(
            debug_name,
            async_func,
            self._current_port_type,
            output_type,
            False,
            queue_size,
            full_strategy,
        )

        # Apply pending middleware to the node
        if hasattr(node, "middleware"):
            for middleware in self._pending_middleware:
                node.middleware.add(middleware)

        self._nodes.append(node)
        self._debug_names[node] = debug_name

        # Add connection using object references
        self._connections.append(
            PendingConnection(
                from_node=self._current_node,
                from_port_name=self._current_port_name,
                to_node=node,
                to_port_name="in",
            )
        )

        # Create new builder
        new_builder = FlowBuilder(
            namespace=self.namespace,
            current_node=node,
            current_port_name="out",
            current_port_type=output_type,
        )
        new_builder._nodes = self._nodes.copy()
        new_builder._connections = self._connections.copy()
        new_builder._node_counter = self._node_counter
        new_builder._debug_names = self._debug_names.copy()

        return new_builder

    def filter(
        self,
        predicate: Callable[[T], bool],
        name: Optional[str] = None,
        queue_size: int = DEFAULT_QUEUE_SIZE,
        full_strategy: QueueFullStrategy = QueueFullStrategy.BLOCK,
    ) -> FlowBuilder[T]:
        """Add filter node.

        Args:
            predicate: Function that returns True to keep items
            name: Optional debug name for the node
            queue_size: Size of the input queue
            full_strategy: Strategy when queue is full

        Returns:
            New FlowBuilder instance for chaining

        Examples:
            Filter even numbers:

            >>> import asyncio
            >>> async def example():
            ...     results = []
            ...     await (
            ...         flow()
            ...         .source(range(6), int)
            ...         .filter(lambda x: x % 2 == 0)
            ...         .sink(results.append)
            ...         .execute(duration=0.5)
            ...     )
            ...     return results
            >>> asyncio.run(example())
            [0, 2, 4]

            Filter with async predicate:

            >>> async def is_valid(x):
            ...     await asyncio.sleep(0.001)  # Simulate async check
            ...     return x > 10
            >>> async def example_async():
            ...     results = []
            ...     await (
            ...         flow()
            ...         .source([5, 15, 25], int)
            ...         .filter(is_valid)
            ...         .sink(results.append)
            ...         .execute(duration=0.5)
            ...     )
            ...     return results
            >>> asyncio.run(example_async())
            [15, 25]
        """
        if not self._current_node or self._current_port_type is None:
            raise ValueError("No source to filter from")

        debug_name = name or self._next_node_name("filter")

        async_predicate = ensure_async(predicate)
        node = create_filter_node(
            debug_name,
            async_predicate,
            self._current_port_type,
            False,
            queue_size,
            full_strategy,
        )
        self._nodes.append(node)
        self._debug_names[node] = debug_name

        # Add connection
        self._connections.append(
            PendingConnection(
                from_node=self._current_node,
                from_port_name=self._current_port_name,
                to_node=node,
                to_port_name="in",
            )
        )

        # Create new builder
        new_builder = FlowBuilder(
            namespace=self.namespace,
            current_node=node,
            current_port_name="out",
            current_port_type=self._current_port_type,
        )
        new_builder._nodes = self._nodes.copy()
        new_builder._connections = self._connections.copy()
        new_builder._node_counter = self._node_counter
        new_builder._debug_names = self._debug_names.copy()

        return new_builder

    def tap(
        self,
        func: Callable[[T], None],
        name: Optional[str] = None,
        queue_size: int = DEFAULT_QUEUE_SIZE,
        full_strategy: QueueFullStrategy = QueueFullStrategy.BLOCK,
    ) -> FlowBuilder[T]:
        """Add tap for side effects without consuming the stream.

        Args:
            func: Function to call for side effects (return value ignored)
            name: Optional debug name for the node
            queue_size: Size of the input queue
            full_strategy: Strategy when queue is full

        Returns:
            New FlowBuilder instance for chaining

        Examples:
            Logging without modifying the stream:

            >>> import asyncio
            >>> async def example():
            ...     logged = []
            ...     results = []
            ...     await (
            ...         flow()
            ...         .source([1, 2, 3], int)
            ...         .tap(lambda x: logged.append(f"Processing {x}"))
            ...         .transform(lambda x: x**2, int)
            ...         .sink(results.append)
            ...         .execute(duration=0.5)
            ...     )
            ...     return logged, results
            >>> logged, results = asyncio.run(example())
            >>> logged
            ['Processing 1', 'Processing 2', 'Processing 3']
            >>> results
            [1, 4, 9]
        """
        if not self._current_node or self._current_port_type is None:
            raise ValueError("No source to tap from")

        debug_name = name or self._next_node_name("tap")

        async def tap_transform(item: T) -> T:
            await ensure_async(func)(item)
            return item

        async_func = tap_transform
        node = create_transform_node(
            debug_name,
            async_func,
            self._current_port_type,
            self._current_port_type,
            False,
            queue_size,
            full_strategy,
        )
        self._nodes.append(node)
        self._debug_names[node] = debug_name

        # Add connection
        self._connections.append(
            PendingConnection(
                from_node=self._current_node,
                from_port_name=self._current_port_name,
                to_node=node,
                to_port_name="in",
            )
        )

        # Create new builder
        new_builder = FlowBuilder(
            namespace=self.namespace,
            current_node=node,
            current_port_name="out",
            current_port_type=self._current_port_type,
        )
        new_builder._nodes = self._nodes.copy()
        new_builder._connections = self._connections.copy()
        new_builder._node_counter = self._node_counter
        new_builder._debug_names = self._debug_names.copy()

        return new_builder

    def sink(
        self,
        func: Callable[[T], Any],
        name: Optional[str] = None,
        queue_size: int = DEFAULT_QUEUE_SIZE,
        full_strategy: QueueFullStrategy = QueueFullStrategy.BLOCK,
    ) -> FlowBuilder[None]:
        """Add sink node.

        Args:
            func: Function to consume each item
            name: Optional debug name for the node
            queue_size: Size of the input queue
            full_strategy: Strategy when queue is full

        Returns:
            New FlowBuilder instance (cannot chain further transforms)

        Examples:
            Collect to a list:

            >>> import asyncio
            >>> async def example():
            ...     results = []
            ...     await (
            ...         flow()
            ...         .source([1, 2, 3], int)
            ...         .sink(results.append)
            ...         .execute(duration=0.5)
            ...     )
            ...     return results
            >>> asyncio.run(example())
            [1, 2, 3]

            Print items:

            >>> async def example_print():
            ...     await (
            ...         flow()
            ...         .source(["hello", "world"], str)
            ...         .sink(print)  # doctest: +SKIP
            ...         .execute(duration=0.5)
            ...     )
            >>> # asyncio.run(example_print())  # Would print: hello\\nworld
        """
        if not self._current_node or self._current_port_type is None:
            raise ValueError("No source to sink from")

        debug_name = name or self._next_node_name("sink")

        async_func = ensure_async(func)
        node = create_sink_node(
            debug_name,
            async_func,
            self._current_port_type,
            False,
            queue_size,
            full_strategy,
        )
        self._nodes.append(node)
        self._debug_names[node] = debug_name

        # Add connection
        self._connections.append(
            PendingConnection(
                from_node=self._current_node,
                from_port_name=self._current_port_name,
                to_node=node,
                to_port_name="in",
            )
        )

        # Create new builder with no current port
        new_builder = FlowBuilder(self.namespace, None, "out", None)
        new_builder._nodes = self._nodes.copy()
        new_builder._connections = self._connections.copy()
        new_builder._node_counter = self._node_counter
        new_builder._debug_names = self._debug_names.copy()

        return new_builder

    def to(
        self,
        func: Callable[[T], Any],
        name: Optional[str] = None,
        queue_size: int = DEFAULT_QUEUE_SIZE,
        full_strategy: QueueFullStrategy = QueueFullStrategy.BLOCK,
    ) -> FlowBuilder[None]:
        """Alias for sink().

        Examples:
            >>> import asyncio
            >>> async def example():
            ...     results = []
            ...     await (
            ...         flow()
            ...         .source([1, 2, 3], int)
            ...         .to(results.append)  # Same as .sink()
            ...         .execute(duration=0.5)
            ...     )
            ...     return results
            >>> asyncio.run(example())
            [1, 2, 3]
        """
        return self.sink(func, name, queue_size, full_strategy)

    def split(
        self,
        n: int = 2,
        queue_size: int = DEFAULT_QUEUE_SIZE,
        full_strategy: QueueFullStrategy = QueueFullStrategy.BLOCK,
    ) -> List[FlowBuilder[T]]:
        """Split stream into multiple outputs.

        Args:
            n: Number of output streams to create
            queue_size: Size of the input queue
            full_strategy: Strategy when queue is full

        Returns:
            List of FlowBuilder instances, one for each output

        Examples:
            Split and process separately:

            >>> source = flow().source([1, 2, 3], int)
            >>> streams = source.split(2)
            >>> len(streams)
            2
            >>> # Each stream can be processed independently
            >>> stream1, stream2 = streams
            >>> stream1._current_port_name
            'out0'
            >>> stream2._current_port_name
            'out1'
        """
        if not self._current_node or self._current_port_type is None:
            raise ValueError("No source to split from")

        debug_name = self._next_node_name("split")

        node = create_split_node(
            debug_name, self._current_port_type, n, queue_size, full_strategy
        )
        self._nodes.append(node)
        self._debug_names[node] = debug_name

        # Add connection from source to split
        self._connections.append(
            PendingConnection(
                from_node=self._current_node,
                from_port_name=self._current_port_name,
                to_node=node,
                to_port_name="in",
            )
        )

        # Create builders for each output
        builders = []
        for i in range(n):
            new_builder = FlowBuilder(
                namespace=self.namespace,
                current_node=node,
                current_port_name=f"out{i}",
                current_port_type=self._current_port_type,
            )
            new_builder._nodes = self._nodes.copy()
            new_builder._connections = self._connections.copy()
            new_builder._node_counter = self._node_counter
            new_builder._debug_names = self._debug_names.copy()
            builders.append(new_builder)

        return builders

    def merge_with(
        self,
        *others: FlowBuilder[T],
        name: Optional[str] = None,
        queue_size: int = DEFAULT_QUEUE_SIZE,
        full_strategy: QueueFullStrategy = QueueFullStrategy.BLOCK,
    ) -> FlowBuilder[T]:
        """Merge multiple flows together.

        Args:
            *others: Other FlowBuilder instances to merge with
            name: Optional debug name for the merge node
            queue_size: Size of the input queues
            full_strategy: Strategy when queue is full

        Returns:
            New FlowBuilder instance with merged streams

        Examples:
            Merge two sources:

            >>> import asyncio
            >>> async def example():
            ...     results = []
            ...
            ...     source1 = flow().source([1, 2, 3], int)
            ...     source2 = flow().source([4, 5, 6], int)
            ...
            ...     await (
            ...         source1.merge_with(source2)
            ...         .sink(results.append)
            ...         .execute(duration=0.5)
            ...     )
            ...     return sorted(results)  # Sort for deterministic output
            >>> asyncio.run(example())
            [1, 2, 3, 4, 5, 6]
        """
        if not self._current_node or self._current_port_type is None:
            raise ValueError("Cannot merge from a flow without a current port")

        # Verify type compatibility
        for other in others:
            if not other._current_node or other._current_port_type is None:
                raise ValueError("Cannot merge with a flow without a current port")
            if other._current_port_type != self._current_port_type:
                raise TypeError(
                    f"Type mismatch: cannot merge {self._current_port_type} "
                    f"with {other._current_port_type}"
                )

        debug_name = name or self._next_node_name("merge")
        num_inputs = 1 + len(others)

        # Create merge node
        merge_node = create_merge_node(
            debug_name,
            self._current_port_type,
            num_inputs,
            queue_size,
            full_strategy,
        )

        # Collect all nodes (no renaming needed!)
        all_nodes = self._nodes.copy()
        for other in others:
            all_nodes.extend(other._nodes)
        all_nodes.append(merge_node)

        # Collect all connections
        all_connections = self._connections.copy()
        for other in others:
            all_connections.extend(other._connections)

        # Add connections to merge node
        all_connections.append(
            PendingConnection(
                from_node=self._current_node,
                from_port_name=self._current_port_name,
                to_node=merge_node,
                to_port_name="in0",
            )
        )

        for i, other in enumerate(others, 1):
            # other._current_node is guaranteed to be non-None due to earlier check
            assert other._current_node is not None
            all_connections.append(
                PendingConnection(
                    from_node=other._current_node,
                    from_port_name=other._current_port_name,
                    to_node=merge_node,
                    to_port_name=f"in{i}",
                )
            )

        # Combine debug names with conflict resolution
        all_debug_names = self._debug_names.copy()
        for i, other in enumerate(others, 1):
            for node, name in other._debug_names.items():
                # Check for name collision
                if name in all_debug_names.values():
                    # Create unique name
                    unique_name = f"{name}_m{i}"
                    all_debug_names[node] = unique_name
                else:
                    all_debug_names[node] = name
        all_debug_names[merge_node] = debug_name

        # Create new builder
        new_builder = FlowBuilder(
            namespace=self.namespace,
            current_node=merge_node,
            current_port_name="out",
            current_port_type=self._current_port_type,
        )
        new_builder._nodes = all_nodes
        new_builder._connections = all_connections
        new_builder._node_counter = (
            self._node_counter + sum(other._node_counter for other in others) + 1
        )
        new_builder._debug_names = all_debug_names

        return new_builder

    def with_middleware(self, *middlewares: Middleware) -> FlowBuilder[T]:
        """Add middleware to all nodes in the current flow.

        Args:
            *middlewares: Middleware instances to add

        Returns:
            New FlowBuilder instance with middleware applied

        Examples:
            Add logging middleware:

            >>> import asyncio
            >>> from flow import LoggingMiddleware
            >>> async def example():
            ...     results = []
            ...     logger = LoggingMiddleware(log_inputs=False, log_outputs=False)
            ...
            ...     await (
            ...         flow()
            ...         .with_middleware(logger)
            ...         .source([1, 2], int)
            ...         .transform(lambda x: x * 2, int)
            ...         .sink(results.append)
            ...         .execute(duration=0.5)
            ...     )
            ...     return results
            >>> asyncio.run(example())
            [2, 4]
        """
        # Add middleware to existing nodes (only UnifiedNodes have middleware)
        for node in self._nodes:
            if hasattr(node, "middleware"):
                for middleware in middlewares:
                    node.middleware.add(middleware)  # type: ignore

        # Create new builder that will add middleware to future nodes
        new_builder = FlowBuilder(
            namespace=self.namespace,
            current_node=self._current_node,
            current_port_name=self._current_port_name,
            current_port_type=self._current_port_type,
        )
        new_builder._nodes = self._nodes.copy()
        new_builder._connections = self._connections.copy()
        new_builder._node_counter = self._node_counter
        new_builder._debug_names = self._debug_names.copy()
        new_builder._pending_middleware = middlewares

        return new_builder

    def build(self) -> ExecutableGraph:
        """Build the executable graph.

        Returns:
            ExecutableGraph ready for execution

        Examples:
            Build and inspect graph:

            >>> from flow import flow
            >>> builder = (
            ...     flow("MyPipeline")
            ...     .source([1, 2, 3], int)
            ...     .transform(lambda x: x * 2, int)
            ...     .sink(lambda x: None)
            ... )
            >>> graph = builder.build()
            >>> graph.name
            'MyPipeline'
            >>> len(graph.nodes)
            3
        """
        from .materializer import ExecutableGraph

        # Wire connections using object references
        connections = []
        for pending in self._connections:
            source_port = pending.from_node.get_output_port(pending.from_port_name)
            target_port = pending.to_node.get_input_port(pending.to_port_name)
            connection = source_port.connect_to(target_port)
            connections.append(connection)

        # Find source nodes
        nodes_with_inputs = set()
        for pending in self._connections:
            nodes_with_inputs.add(pending.to_node)

        source_nodes = [node for node in self._nodes if node not in nodes_with_inputs]

        # Validate DAG
        self._validate_dag()

        # Create dict for ExecutableGraph (it expects a dict for now)
        nodes_dict = {self._debug_names.get(n, f"node_{id(n)}"): n for n in self._nodes}

        return ExecutableGraph(
            name=self.namespace,
            nodes=nodes_dict,
            connections=connections,
            source_nodes=source_nodes,
        )

    def _validate_dag(self) -> None:
        """Validate the graph is a DAG."""
        # Build adjacency list using object identity
        graph: Dict[Node, List[Node]] = {node: [] for node in self._nodes}

        for pending in self._connections:
            if pending.from_node in graph:
                graph[pending.from_node].append(pending.to_node)

        # Check for cycles using DFS
        visited = set()
        rec_stack = set()

        def has_cycle(node: Node) -> bool:
            visited.add(node)
            rec_stack.add(node)

            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if has_cycle(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True

            rec_stack.remove(node)
            return False

        for node in self._nodes:
            if node not in visited:
                if has_cycle(node):
                    node_name = self._debug_names.get(node, str(node))
                    raise ValueError(
                        f"Graph contains a cycle involving node: {node_name}"
                    )

    async def execute(
        self, duration: Optional[float] = None, auto_stop: bool = True
    ) -> None:
        """Build and execute the graph.

        Args:
            duration: Maximum execution time in seconds
            auto_stop: Whether to stop when all data is processed

        Examples:
            Execute a simple pipeline:

            >>> import asyncio
            >>> async def example():
            ...     results = []
            ...     await (
            ...         flow()
            ...         .source([1, 2, 3], int)
            ...         .transform(lambda x: x + 10, int)
            ...         .sink(results.append)
            ...         .execute(duration=0.5)
            ...     )
            ...     return results
            >>> asyncio.run(example())
            [11, 12, 13]
        """
        graph = self.build()
        await graph.run(duration, auto_stop)


# Backward compatibility alias
FlowBuilderChain = FlowBuilder


def flow(namespace: Optional[str] = None) -> FlowBuilder[Any]:
    """Create a new flow builder.

    Args:
        namespace: Optional namespace for the flow (defaults to "flow")

    Returns:
        A new FlowBuilder instance

    Examples:
        Create a simple flow:

        >>> builder = flow()
        >>> builder.namespace
        'flow'

        Create a named flow:

        >>> builder = flow("DataPipeline")
        >>> builder.namespace
        'DataPipeline'

        Complete pipeline example:

        >>> import asyncio
        >>> async def process_data():
        ...     results = []
        ...     await (
        ...         flow("Example")
        ...         .source(range(5), int)
        ...         .filter(lambda x: x % 2 == 0)
        ...         .transform(lambda x: x**2, int)
        ...         .sink(results.append)
        ...         .execute(duration=0.5)
        ...     )
        ...     return results
        >>> asyncio.run(process_data())
        [0, 4, 16]
    """
    return FlowBuilder(namespace)
