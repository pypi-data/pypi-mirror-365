"""Test DROP_OLD with proper understanding of the flow."""

import asyncio

import pytest

from flow import QueueFullStrategy, flow


@pytest.mark.asyncio
async def test_drop_old_expected_behavior():
    """Test what DROP_OLD should actually do."""

    # Source that sends 0-100
    sent = []

    def number_source():
        for i in range(101):
            sent.append(i)
            yield i

    # Sink that processes slowly
    received = []

    async def slow_sink(x):
        print(f"Processing: {x}")
        received.append(x)
        await asyncio.sleep(0.1)  # 0.1 second per item

    # Run for a specific duration
    print("Starting execution...")
    await (
        flow("DROP_OLD Test")
        .source(number_source, int)
        .sink(slow_sink, queue_size=1, full_strategy=QueueFullStrategy.DROP_OLD)
        .execute(duration=1.0, auto_stop=False)
    )  # Run for 1 second

    print("\nResults after 1 second:")
    print(f"Sent: {len(sent)} values (0-{sent[-1] if sent else 'none'})")
    print(f"Received: {len(received)} values")
    print(f"Received values: {received}")

    # With queue size 1 and DROP_OLD:
    # - First value (0) starts processing immediately
    # - While processing (0.1s), source sends many more values
    # - Queue can only hold 1, so it keeps dropping old and keeping newest
    # - After 0.1s, sink takes the newest value from queue
    # - This repeats

    # So we expect to see large jumps between consecutive received values
    if len(received) > 1:
        jumps = []
        for i in range(1, len(received)):
            jump = received[i] - received[i - 1]
            jumps.append(jump)
        print(f"\nJumps between consecutive values: {jumps}")
        print(f"Average jump: {sum(jumps) / len(jumps):.1f}")

        # We should see the last received value is near the end
        print(f"\nLast received value: {received[-1]}")
        print(f"Last sent value: {sent[-1] if sent else 'none'}")

    return received


@pytest.mark.asyncio
async def test_drop_old_vs_drop_new():
    """Compare DROP_OLD vs DROP_NEW behavior."""

    print("\n" + "=" * 60)
    print("Comparing DROP_OLD vs DROP_NEW")
    print("=" * 60)

    async def run_with_strategy(strategy, name):
        sent = []

        def source():
            for i in range(20):
                sent.append(i)
                yield i

        received = []

        async def sink(x):
            received.append(x)
            await asyncio.sleep(0.1)

        await (
            flow(f"{name} Test")
            .source(source, int)
            .sink(sink, queue_size=2, full_strategy=strategy)
            .execute(duration=0.5, auto_stop=False)
        )

        print(f"\n{name}:")
        print(f"Sent: {sent}")
        print(f"Received: {received}")

        return received

    drop_old = await run_with_strategy(QueueFullStrategy.DROP_OLD, "DROP_OLD")
    drop_new = await run_with_strategy(QueueFullStrategy.DROP_NEW, "DROP_NEW")

    print("\nAnalysis:")
    print(f"DROP_OLD kept values: {drop_old} (should favor later values)")
    print(f"DROP_NEW kept values: {drop_new} (should favor earlier values)")


if __name__ == "__main__":
    asyncio.run(test_drop_old_expected_behavior())
    asyncio.run(test_drop_old_vs_drop_new())
