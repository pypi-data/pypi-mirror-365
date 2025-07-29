"""Test module for running doctests from the flow package."""

import doctest
from pathlib import Path
import sys

# Add the parent directory to the path so we can import flow
sys.path.insert(0, str(Path(__file__).parent.parent))

import flow
import flow.core
import flow.factory
import flow.flow_builder
import flow.middleware


def test_doctests():
    """Run all doctests in the flow package."""
    modules = [
        flow,
        flow.flow_builder,
        flow.middleware,
        flow.factory,
        flow.core,
    ]

    failures = 0
    tests = 0

    for module in modules:
        module_failures, module_tests = doctest.testmod(
            module,
            verbose=False,
            optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS,
        )
        failures += module_failures
        tests += module_tests

        if module_failures > 0:
            print(f"Doctest failures in {module.__name__}")

    assert failures == 0, f"{failures} doctest(s) failed out of {tests} total"


if __name__ == "__main__":
    test_doctests()
