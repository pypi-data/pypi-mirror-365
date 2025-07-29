#!/usr/bin/env python3
"""Test and demonstrate the middleware system."""

import asyncio
import pytest

from flow import (
    LoggingMiddleware,
    MetricsMiddleware,
    Middleware,
    RetryMiddleware,
    ThrottleMiddleware,
    flow,
)


class UppercaseMiddleware(Middleware):
    """Custom middleware that uppercases string values."""

    async def process(self, context, next_middleware):
        # Process normally
        result = await next_middleware(context)

        # Modify output if it's a string
        if hasattr(context, "output_value") and isinstance(context.output_value, str):
            context.output_value = context.output_value.upper()

        return result


@pytest.mark.asyncio
async def test_logging_middleware():
    """Test logging middleware."""
    print("\n=== Testing Logging Middleware ===")

    logger = LoggingMiddleware(log_inputs=True, log_outputs=True)
    results = []

    await (
        flow()
        .source(lambda: ["hello", "world"], str)
        .with_middleware(logger)
        .transform(lambda x: f"processed-{x}", str)
        .sink(lambda x: results.append(x))
        .execute(duration=0.5)
    )

    print(f"Results: {results}")
    return len(results) == 2


@pytest.mark.asyncio
async def test_metrics_middleware():
    """Test metrics middleware."""
    print("\n=== Testing Metrics Middleware ===")

    metrics = MetricsMiddleware()
    results = []

    await (
        flow()
        .source(lambda: [1, 2, 3, 4, 5], int)
        .with_middleware(metrics)
        .transform(lambda x: x * 2, int)
        .filter(lambda x: x > 4)
        .sink(lambda x: results.append(x))
        .execute(duration=0.5)
    )

    print(f"Results: {results}")
    print(f"Metrics: {metrics.get_metrics()}")

    return metrics.get_metrics()["total_processed"] > 0


@pytest.mark.asyncio
async def test_throttle_middleware():
    """Test throttle middleware."""
    print("\n=== Testing Throttle Middleware ===")

    import time

    throttle = ThrottleMiddleware(delay_seconds=0.1)
    results = []

    start_time = time.time()
    await (
        flow()
        .source(lambda: [1, 2], int)
        .with_middleware(throttle)
        .transform(lambda x: x * 2, int)
        .sink(lambda x: results.append(x))
        .execute(duration=1.0)
    )

    duration = time.time() - start_time
    print(f"Results: {results}")
    print(f"Duration: {duration:.2f}s (should be > 0.2s due to throttling)")

    return duration > 0.15  # Account for some timing variance


@pytest.mark.asyncio
async def test_retry_middleware():
    """Test retry middleware with a flaky function."""
    print("\n=== Testing Retry Middleware ===")

    class FlakyFunction:
        def __init__(self):
            self.call_count = 0

        async def __call__(self, x):
            self.call_count += 1
            if self.call_count <= 2:  # Fail first 2 calls
                raise Exception(f"Flaky failure #{self.call_count}")
            return x * 2

    retry = RetryMiddleware(max_attempts=3, backoff=0.01)
    flaky = FlakyFunction()
    results = []

    try:
        await (
            flow()
            .source(lambda: [1], int)
            .with_middleware(retry)
            .transform(flaky, int)
            .sink(lambda x: results.append(x))
            .execute(duration=0.5)
        )

        print(f"Results: {results} (after {flaky.call_count} attempts)")
        return len(results) == 1 and flaky.call_count == 3

    except Exception as e:
        print(f"Failed: {e}")
        return False


@pytest.mark.asyncio
async def test_custom_middleware():
    """Test custom middleware."""
    print("\n=== Testing Custom Middleware ===")

    uppercase = UppercaseMiddleware()
    results = []

    await (
        flow()
        .source(lambda: ["hello", "world"], str)
        .with_middleware(uppercase)
        .transform(lambda x: f"processed-{x}", str)
        .sink(lambda x: results.append(x))
        .execute(duration=0.5)
    )

    print(f"Results: {results}")
    return all("PROCESSED" in result.upper() for result in results)


@pytest.mark.asyncio
async def test_middleware_chaining():
    """Test multiple middleware working together."""
    print("\n=== Testing Middleware Chaining ===")

    logger = LoggingMiddleware(log_inputs=False, log_outputs=True)
    metrics = MetricsMiddleware()
    throttle = ThrottleMiddleware(delay_seconds=0.01)

    results = []

    await (
        flow()
        .source(lambda: [1, 2, 3], int)
        .with_middleware(logger, metrics, throttle)
        .transform(lambda x: x * 10, int)
        .sink(lambda x: results.append(x))
        .execute(duration=1.0)
    )

    print(f"Results: {results}")
    print(f"Metrics: {metrics.get_metrics()}")

    return (
        len(results) == 3 and metrics.get_metrics()["total_processed"] == 6
    )  # 3 source + 3 transform


async def main():
    """Run all middleware tests."""
    print("🧪 Testing Flokkit Flow Middleware System")

    tests = [
        test_logging_middleware,
        test_metrics_middleware,
        test_throttle_middleware,
        test_retry_middleware,
        test_custom_middleware,
        test_middleware_chaining,
    ]

    passed = 0
    for test in tests:
        try:
            if await test():
                print("✅ PASSED")
                passed += 1
            else:
                print("❌ FAILED")
        except Exception as e:
            print(f"❌ ERROR: {e}")

    print(f"\n📊 Results: {passed}/{len(tests)} tests passed")

    if passed == len(tests):
        print("🎉 All middleware tests passed!")
    else:
        print("⚠️  Some tests failed")


if __name__ == "__main__":
    asyncio.run(main())
