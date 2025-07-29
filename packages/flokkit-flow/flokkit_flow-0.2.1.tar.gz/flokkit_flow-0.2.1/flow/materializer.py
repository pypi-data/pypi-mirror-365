"""Executable graph for running flow-based programs."""

from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional

from .core import Connection
from .nodes import Node


class ExecutableGraph:
    """Executable graph created directly by FlowBuilder."""

    def __init__(
        self,
        name: str,
        nodes: Dict[str, Node],
        connections: List[Connection[Any]],
        source_nodes: List[Node],
    ):
        self.name = name
        self.nodes = nodes
        self.connections = connections
        self.source_nodes = source_nodes
        self._running = False
        self._tasks: Dict[str, asyncio.Task[None]] = {}
        self._stop_event = asyncio.Event()
        self._completion_tracker: Dict[str, bool] = {}
        self._node_error: Optional[Exception] = None
        self._failed_node: Optional[str] = None

    async def run(
        self, duration: Optional[float] = None, auto_stop: bool = True
    ) -> None:
        """Execute the graph."""
        await self._initialize()
        self._running = True

        # Start tasks for all nodes
        for name, node in self.nodes.items():
            task = asyncio.create_task(self._run_node(node), name=f"node_{name}")
            self._tasks[name] = task

        try:
            if duration:
                await asyncio.sleep(duration)
            elif auto_stop:
                # Give nodes a chance to start
                await asyncio.sleep(0.01)
                # Monitor for completion
                while self._running and not self._stop_event.is_set():
                    # Check completion every 100ms
                    await asyncio.sleep(0.1)
                    if await self._is_complete():
                        self._stop_event.set()
                        break
            else:
                # Just wait for stop event
                await self._stop_event.wait()
        finally:
            await self._shutdown()

            # If a node failed, re-raise the error
            if self._node_error:
                raise self._node_error

    async def stop(self) -> None:
        """Stop graph execution."""
        self._stop_event.set()
        await self._shutdown()

    async def _initialize(self) -> None:
        """Initialize all nodes."""
        for node in self.nodes.values():
            # Set graph reference
            node._graph = self
            await node.initialize()
        self._stop_event.clear()

    async def _run_node(self, node: Node) -> None:
        """Run a single node."""
        try:
            # Call on_start lifecycle hook
            await node.on_start()

            while self._running and not node._completed:
                try:
                    await node.process()

                    if node._completed:
                        self._completion_tracker[node.name] = True
                        break

                except asyncio.CancelledError:
                    break
                except Exception as e:
                    await node.on_error(e)
                    if node._error:
                        # Store error for later re-raising
                        self._node_error = e
                        self._failed_node = node.name
                        # Stop the graph
                        self._stop_event.set()
                        raise
        finally:
            await node.on_stop()

    async def _is_complete(self) -> bool:
        """Check if all processing is complete."""
        # Check if we have any source nodes
        if not self.source_nodes:
            # No sources means nothing to do
            return True

        # All sources must be done
        all_sources_done = all(
            self._completion_tracker.get(node.name, False) for node in self.source_nodes
        )

        if not all_sources_done:
            return False

        # All queues must be empty
        for node in self.nodes.values():
            for port in node._input_ports.values():
                if port._queue and not port._queue.empty():
                    return False

        return True

    async def _shutdown(self) -> None:
        """Shutdown all nodes gracefully."""
        self._running = False

        # Give nodes a brief moment to notice _running is False
        await asyncio.sleep(0.01)

        # Cancel all tasks
        for task in self._tasks.values():
            if not task.done():
                task.cancel()

        # Wait for all tasks to complete with timeout
        if self._tasks:
            try:
                await asyncio.wait_for(
                    asyncio.gather(*self._tasks.values(), return_exceptions=True),
                    timeout=5.0,
                )
            except asyncio.TimeoutError:
                # Force cancel if tasks don't stop gracefully
                for task in self._tasks.values():
                    if not task.done():
                        task.cancel()

        self._tasks.clear()
