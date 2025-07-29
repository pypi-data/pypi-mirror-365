# Flokkit Flow

A type-safe, async-first flow-based programming (FBP) framework for Python with zero dependencies.

## Features

- 🔒 **Type-safe** - Full type safety across the entire flow graph
- ⚡ **Async-first** - Built on asyncio with automatic sync function adaptation  
- 🚦 **Backpressure** - Bounded queues with configurable strategies
- 🔄 **DAG Safety** - Automatic cycle detection prevents deadlocks
- 📦 **Zero Dependencies** - Pure Python, no external packages required
- 🔌 **Lifecycle Hooks** - Proper resource management with init/cleanup
- 🏭 **Flexible Patterns** - Support for both pipeline and server patterns
- 🎯 **Middleware System** - Extensible processing pipeline with logging, metrics, throttling, and retry support

## Installation

```bash
pip install flokkit-flow
```

## Documentation

Full documentation is available at: https://flokkit.gitlab.io/flow/

### Quick Install

```bash
# Using uv (replace {project_id} with actual ID)
# From source
uv pip install git+https://gitlab.com/flokkit/flow.git
```

### For Development

```bash
# Clone and install in editable mode
git clone https://gitlab.com/flokkit/flow.git
cd flow
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

## Quick Start

```python
from flow import flow

# Build a simple pipeline
async def main():
    builder = flow("My Pipeline")
    
    def generate_numbers():
        return 42
    
    def double(x):
        return x * 2
    
    def print_result(x):
        print(f"Result: {x}")
    
    # Connect the nodes
    (builder
        .source(generate_numbers, int)
        .transform(double, int)
        .to(print_result))
    
    # Run the pipeline
    await builder.execute(duration=1.0)

# Run it
import asyncio
asyncio.run(main())
```

### Using Middleware

```python
from flow import flow, LoggingMiddleware, MetricsMiddleware

async def main():
    # Create middleware instances
    logger = LoggingMiddleware()
    metrics = MetricsMiddleware()
    
    # Build pipeline with middleware
    builder = flow("Monitored Pipeline")
    
    results = []
    await (
        builder
        .with_middleware(logger, metrics)  # Add middleware to all nodes
        .source(lambda: [1, 2, 3, 4, 5], int)
        .filter(lambda x: x % 2 == 0)
        .transform(lambda x: x ** 2, int)
        .to(results.append)
        .execute(duration=1.0)
    )
    
    print(f"Results: {results}")
    print(f"Metrics: {metrics.get_metrics()}")

asyncio.run(main())
```

## Examples

See the `examples/` directory for comprehensive examples:
- Basic flows and transformations
- Backpressure and queue strategies
- Split/merge patterns
- Async I/O and blocking operations
- Pipeline vs server patterns
- Lifecycle management

## Development

This project uses [just](https://github.com/casey/just) for development commands and [uv](https://github.com/astral-sh/uv) for fast dependency management.

```bash
# Install tools
curl -LsSf https://astral.sh/uv/install.sh | sh  # Install uv
brew install just                                 # Install just (macOS)

# Set up development environment
uv venv                    # Create virtual environment
source .venv/bin/activate  # Activate it
just install-dev          # Install all dev dependencies

# Development commands
just                      # List all commands
just test                 # Run tests
just typecheck           # Run type checker
just check               # Run all checks
just example 1           # Run specific example
```

### Common Commands

```bash
# Development workflow
just dev          # Run checks and watch for changes
just test         # Run tests (auto-detects pytest)
just typecheck    # Run basedpyright
just check        # Run all checks

# Examples
just example      # List examples
just example 5    # Run example 5
just examples     # Run all examples

# Utilities
just clean        # Clean generated files
just stats        # Show project statistics
```

## Documentation

### Building Documentation Locally

Flokkit Flow uses Sphinx for documentation with the modern Python documentation toolchain:

```bash
# Install documentation dependencies
just install-docs

# Build documentation
just docs-build

# Serve with auto-reload for development
just docs-serve

# Open in browser
just docs-open
```

### Documentation Structure

- **Getting Started**: Installation, quickstart, and core concepts
- **User Guide**: In-depth guides for common use cases
- **API Reference**: Complete API documentation with examples
- **Examples**: Practical examples with explanations

### Online Documentation

Documentation is automatically built and hosted on [Read the Docs](https://flokkit-flow.readthedocs.io) (when published).

## License

MIT