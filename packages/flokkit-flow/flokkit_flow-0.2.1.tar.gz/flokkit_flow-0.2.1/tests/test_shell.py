"""Tests for shell command integration."""

import asyncio
import tempfile
from pathlib import Path

import pytest

from flow import flow
from flow.shell import ShellCommand, shell_sink, shell_source, shell_transform


@pytest.mark.asyncio
async def test_shell_command_basic():
    """Test basic ShellCommand execution."""
    cmd = ShellCommand("echo hello")
    result = await cmd.run()
    
    assert result.success
    assert result.returncode == 0
    assert result.stdout.strip() == "hello"
    assert result.stderr == ""


@pytest.mark.asyncio
async def test_shell_command_with_input():
    """Test ShellCommand with stdin input."""
    cmd = ShellCommand("cat", input_mode="stdin")
    result = await cmd.run("test input")
    
    assert result.success
    assert result.stdout == "test input"


@pytest.mark.asyncio
async def test_shell_command_args():
    """Test ShellCommand with argument input."""
    cmd = ShellCommand("echo", input_mode="args")
    output = await cmd("hello world")
    
    assert output == "hello world"


@pytest.mark.asyncio
async def test_shell_command_failure():
    """Test ShellCommand error handling."""
    cmd = ShellCommand("false", check=True)
    
    with pytest.raises(RuntimeError) as exc_info:
        await cmd.run()
    
    assert "return code 1" in str(exc_info.value)


@pytest.mark.asyncio
async def test_shell_command_no_check():
    """Test ShellCommand with check=False."""
    cmd = ShellCommand("false", check=False)
    result = await cmd.run()
    
    assert not result.success
    assert result.returncode == 1


@pytest.mark.asyncio
async def test_shell_source():
    """Test shell command as source."""
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write("line1\nline2\nline3\n")
        temp_file = f.name
    
    try:
        source = shell_source(f"cat {temp_file}")
        results = []
        
        await (
            flow()
            .source(source, str)
            .sink(results.append)
            .execute()
        )
        
        assert results == ["line1", "line2", "line3"]
    finally:
        Path(temp_file).unlink()


@pytest.mark.asyncio
async def test_shell_source_with_parser():
    """Test shell source with custom parser."""
    # Create temporary file with numbers
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write("1\n2\n3\n")
        temp_file = f.name
    
    try:
        source = shell_source(f"cat {temp_file}", int, parser=int)
        results = []
        
        await (
            flow()
            .source(source, int)
            .transform(lambda x: x * 2, int)
            .sink(results.append)
            .execute()
        )
        
        assert results == [2, 4, 6]
    finally:
        Path(temp_file).unlink()


@pytest.mark.asyncio
async def test_shell_transform():
    """Test shell command as transform."""
    uppercase = shell_transform("tr '[:lower:]' '[:upper:]'")
    
    results = []
    await (
        flow()
        .source(["hello", "world"], str)
        .transform(uppercase, str)
        .sink(results.append)
        .execute()
    )
    
    assert results == ["HELLO", "WORLD"]


@pytest.mark.asyncio
async def test_shell_transform_with_parser():
    """Test shell transform with output parser."""
    # Use expr to add 10
    def parse_int(s: str) -> int:
        return int(s.strip())
    
    add_ten = shell_transform("expr 10 +", int, input_mode="args", parser=parse_int)
    
    results = []
    await (
        flow()
        .source([5, 15, 25], int)
        .transform(add_ten, int)
        .sink(results.append)
        .execute()
    )
    
    assert results == [15, 25, 35]


@pytest.mark.asyncio
async def test_shell_sink():
    """Test shell command as sink."""
    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
    temp_file.close()
    
    try:
        append = shell_sink(f"tee -a {temp_file.name}")
        
        await (
            flow()
            .source(["line 1", "line 2", "line 3"], str)
            .sink(append)
            .execute()
        )
        
        # Verify file contents
        with open(temp_file.name) as f:
            content = f.read()
        
        assert "line 1" in content
        assert "line 2" in content
        assert "line 3" in content
    finally:
        Path(temp_file.name).unlink()


@pytest.mark.asyncio
async def test_shell_pipeline():
    """Test pipeline with multiple shell commands."""
    # Pipeline: generate numbers -> square them -> filter even
    square = shell_transform("awk '{print $1 * $1}'", int, parser=int)
    
    # Use grep to filter lines (which won't output empty lines)
    def is_even(n: int) -> bool:
        return n % 2 == 0
    
    results = []
    await (
        flow()
        .source([1, 2, 3, 4, 5], int)
        .transform(square, int)
        .filter(is_even)
        .sink(results.append)
        .execute()
    )
    
    assert results == [4, 16]  # 2^2 and 4^2


@pytest.mark.asyncio
async def test_shell_streaming():
    """Test streaming with shell commands."""
    cmd = ShellCommand("cat", input_mode="none", output_mode="lines")
    
    # Create a test file
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        for i in range(5):
            f.write(f"Line {i}\n")
        temp_file = f.name
    
    try:
        # Update command to read the file
        cmd.args = ["cat", temp_file]
        
        lines = []
        async for line in cmd.stream_output():
            lines.append(line)
        
        assert len(lines) == 5
        assert lines[0] == "Line 0"
        assert lines[4] == "Line 4"
    finally:
        Path(temp_file).unlink()


@pytest.mark.asyncio
async def test_shell_timeout():
    """Test shell command timeout."""
    # Command that sleeps longer than timeout
    cmd = ShellCommand("sleep 10", timeout=0.1)
    
    with pytest.raises(TimeoutError):
        await cmd.run()


@pytest.mark.asyncio
async def test_shell_environment():
    """Test shell command with custom environment."""
    cmd = ShellCommand("echo $CUSTOM_VAR", shell=True, env={"CUSTOM_VAR": "test123"})
    result = await cmd.run()
    
    assert result.stdout.strip() == "test123"


@pytest.mark.asyncio
async def test_shell_working_directory():
    """Test shell command with custom working directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a file in the temp directory
        test_file = Path(tmpdir) / "test.txt"
        test_file.write_text("content")
        
        # Run ls in that directory
        cmd = ShellCommand("ls", cwd=tmpdir)
        result = await cmd.run()
        
        assert "test.txt" in result.stdout


@pytest.mark.asyncio
async def test_shell_with_middleware():
    """Test shell commands with middleware."""
    from flow import LoggingMiddleware, MetricsMiddleware
    
    # Create a simple echo transform
    echo_upper = shell_transform("tr '[:lower:]' '[:upper:]'")
    
    results = []
    
    # Use both logging and metrics middleware
    logger = LoggingMiddleware()
    metrics = MetricsMiddleware()
    
    await (
        flow()
        .with_middleware(logger, metrics)
        .source(["hello", "world"], str)
        .transform(echo_upper, str)
        .sink(results.append)
        .execute()
    )
    
    assert results == ["HELLO", "WORLD"]
    # Check that metrics were collected
    stats = metrics.get_metrics()
    assert stats["total_processed"] > 0
    assert len(stats["by_node"]) > 0