"""Quick debug with timeout."""

import asyncio

import pytest

from flow import flow


@pytest.mark.asyncio
async def test_with_timeout():
    """Test with timeout to avoid hanging."""

    def source():
        print("Source: yielding 0")
        yield 0
        print("Source: yielding 1")
        yield 1
        print("Source: done")

    results = []

    async def sink(x):
        print(f"Sink: got {x}")
        results.append(x)
        await asyncio.sleep(0.1)
        print(f"Sink: done with {x}")

    print("Starting...")
    try:
        await asyncio.wait_for(
            flow("Timeout Test").source(source, int).sink(sink).execute(), timeout=2.0
        )
        print("Completed normally")
    except asyncio.TimeoutError:
        print("TIMEOUT!")

    print(f"Results: {results}")


if __name__ == "__main__":
    asyncio.run(test_with_timeout())
