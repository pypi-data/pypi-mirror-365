"""Test merge functionality after the fix."""

import asyncio

import pytest

from flow import flow


class TestMergeFunctionality:
    """Test the fixed merge functionality."""

    @pytest.mark.asyncio
    async def test_merge_two_flows(self):
        """Test merging two simple flows."""
        results = []

        # Create two flows
        flow1 = flow("test1").source(lambda: [1, 2], int)
        flow2 = flow("test2").source(lambda: [3, 4], int)

        # Merge and execute
        await flow1.merge_with(flow2).sink(lambda x: results.append(x)).execute()

        # Results can arrive in any order
        assert sorted(results) == [1, 2, 3, 4]

    @pytest.mark.asyncio
    async def test_merge_three_flows(self):
        """Test merging three flows."""
        results = []

        # Create three flows
        flow1 = flow("test1").source(lambda: [1, 2], int)
        flow2 = flow("test2").source(lambda: [3, 4], int)
        flow3 = flow("test3").source(lambda: [5, 6], int)

        # Merge all three
        await flow1.merge_with(flow2, flow3).sink(lambda x: results.append(x)).execute()

        assert sorted(results) == [1, 2, 3, 4, 5, 6]

    @pytest.mark.asyncio
    async def test_merge_with_transforms(self):
        """Test merging flows that have transforms."""
        results = []

        # Create flows with transforms
        flow1 = (
            flow("test1").source(lambda: [1, 2], int).transform(lambda x: x * 10, int)
        )

        flow2 = (
            flow("test2").source(lambda: [3, 4], int).transform(lambda x: x * 100, int)
        )

        # Merge and execute
        await flow1.merge_with(flow2).sink(lambda x: results.append(x)).execute()

        assert sorted(results) == [10, 20, 300, 400]

    @pytest.mark.asyncio
    async def test_merge_with_filter(self):
        """Test merging with filtering."""
        results = []

        # Create flows with different filters
        flow1 = (
            flow("test1").source(lambda: range(10), int).filter(lambda x: x % 2 == 0)
        )  # Even numbers

        flow2 = (
            flow("test2").source(lambda: range(10), int).filter(lambda x: x % 2 == 1)
        )  # Odd numbers

        # Merge and execute
        await flow1.merge_with(flow2).sink(lambda x: results.append(x)).execute()

        assert sorted(results) == list(range(10))

    @pytest.mark.asyncio
    async def test_merge_type_mismatch_error(self):
        """Test that merging incompatible types raises error."""
        flow1 = flow("test1").source(lambda: [1, 2], int)
        flow2 = flow("test2").source(lambda: ["a", "b"], str)

        with pytest.raises(TypeError, match="Type mismatch"):
            flow1.merge_with(flow2)

    @pytest.mark.asyncio
    async def test_merge_with_custom_name(self):
        """Test merge with custom node name."""
        results = []

        flow1 = flow("test1").source(lambda: [1], int)
        flow2 = flow("test2").source(lambda: [2], int)

        # Use custom merge node name and execute
        await (
            flow1.merge_with(flow2, name="my_merger")
            .sink(lambda x: results.append(x))
            .execute()
        )

        assert sorted(results) == [1, 2]

    @pytest.mark.asyncio
    async def test_merge_async_sources(self):
        """Test merging async sources."""
        results = []

        async def async_source1():
            for i in [1, 2]:
                yield i
                await asyncio.sleep(0.01)

        async def async_source2():
            for i in [3, 4]:
                yield i
                await asyncio.sleep(0.01)

        flow1 = flow("test1").source(async_source1, int)
        flow2 = flow("test2").source(async_source2, int)

        await flow1.merge_with(flow2).sink(lambda x: results.append(x)).execute()

        assert sorted(results) == [1, 2, 3, 4]
