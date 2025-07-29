"""
Test basic functionality of the FBP implementation.
"""

import asyncio

from flow import flow
from tests.pytest_compat import pytest

# No longer need GraphMaterializer - FlowBuilder creates graphs directly


@pytest.mark.asyncio
async def test_basic_flow():
    """Test basic source -> transform -> sink flow."""
    builder = flow("Test")

    count = 0

    def source() -> int:
        nonlocal count
        count += 1
        return count

    def double(x: int) -> int:
        return x * 2

    results = []

    def sink(x: int) -> None:
        results.append(x)

    await (
        builder.source(source, int)
        .transform(double, int)
        .sink(sink)
        .execute(duration=0.1)
    )

    # Assertions
    assert len(results) > 0, "Should have processed some items"
    assert all(x % 2 == 0 for x in results), "All results should be even (doubled)"
    assert results[0] == 2, "First result should be 2 (1 doubled)"
    assert results[1] == 4, "Second result should be 4 (2 doubled)"


@pytest.mark.asyncio
async def test_backpressure():
    """Test backpressure with small queue."""
    builder = flow("Backpressure")

    produced = 0

    async def producer() -> int:
        nonlocal produced
        produced += 1
        return produced

    consumed = 0

    async def consumer(x: int) -> None:
        nonlocal consumed
        consumed += 1
        await asyncio.sleep(0.1)  # Slow consumer

    chain = builder.source(producer, int).sink(consumer, queue_size=2)  # Small queue

    await chain.execute(duration=0.5)

    # Assertions
    assert produced > 0, "Should have produced items"
    assert consumed > 0, "Should have consumed items"
    # With a queue size of 2 and slow consumer, producer should be throttled
    # Allow some margin for timing variations
    assert produced <= consumed + 3, (
        f"Producer ({produced}) should be limited by consumer ({consumed}) + small buffer"
    )


@pytest.mark.asyncio
async def test_filtering():
    """Test filtering functionality."""
    builder = flow("Filter")

    counter = 0

    def numbers() -> int:
        nonlocal counter
        counter += 1
        return counter

    def is_even(x: int) -> bool:
        return x % 2 == 0

    even_numbers = []

    def collect_even(x: int) -> None:
        even_numbers.append(x)

    chain = builder.source(numbers, int).filter(is_even).sink(collect_even)

    await chain.execute(duration=0.1)

    # Assertions
    assert len(even_numbers) > 0, "Should have collected even numbers"
    assert all(x % 2 == 0 for x in even_numbers), "All collected numbers should be even"
    assert 2 in even_numbers, "Should include 2"
    assert 1 not in even_numbers, "Should not include odd numbers"


@pytest.mark.asyncio
async def test_transform_computation():
    """Test transform computation functionality."""
    builder = flow("Transform Test")

    # Track computation count
    computation_count = 0

    values = [1, 2, 3, 2, 1, 3]  # Values to process
    index = 0

    def source() -> int:
        nonlocal index
        if index >= len(values):
            return 0
        val = values[index]
        index += 1
        return val

    def compute_cube(x: int) -> int:
        nonlocal computation_count
        if x == 0:
            return 0
        computation_count += 1
        return x * x * x  # Cube

    results = []

    def collect(x: int) -> None:
        if x != 0:
            results.append(x)

    chain = (
        builder.source(source, int)
        .transform(compute_cube, int)  # Transform without caching
        .sink(collect)
    )

    # Run until complete
    await chain.execute(duration=0.5)

    # Assertions
    assert len(results) == 6, "Should process all values"
    assert computation_count == 6, "Should compute all values (no caching)"
    assert results == [1, 8, 27, 8, 1, 27], "Results should match cubed values"
