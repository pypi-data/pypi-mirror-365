"""Shell command integration for Flokkit Flow.

This module provides utilities for integrating shell commands as nodes in flow graphs.
Shell commands can be used as sources, transforms, or sinks, with full support for
streaming, backpressure, and type safety.
"""

import asyncio
import shlex
import sys
from pathlib import Path
from typing import (
    AsyncIterator,
    Callable,
    Dict,
    List,
    Optional,
    TypeVar,
    Union,
    overload,
)

T = TypeVar("T")
U = TypeVar("U")


class ShellResult:
    """Result of a shell command execution."""

    def __init__(
        self,
        stdout: str,
        stderr: str,
        returncode: int,
        command: str,
    ):
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode
        self.command = command
        self.success = returncode == 0

    def __repr__(self) -> str:
        return f"ShellResult(command={self.command!r}, returncode={self.returncode}, success={self.success})"


class ShellCommand:
    """A shell command that can be used as a node in a flow.
    
    This class provides flexible ways to integrate shell commands:
    - As a source: Command output lines are streamed as items
    - As a transform: Input is passed via stdin, output via stdout
    - As a sink: Input is passed as arguments or stdin
    
    Examples:
        # As a source - stream log file lines
        >>> cmd = ShellCommand("tail -f /var/log/app.log")
        >>> await flow().source(cmd, str).transform(parse_log, LogEntry).sink(store_log).execute()
        
        # As a transform - use grep to filter
        >>> grep = ShellCommand("grep ERROR", input_mode="stdin")
        >>> await flow().source(logs, str).transform(grep, str).sink(print).execute()
        
        # As a sink - append to file
        >>> append = ShellCommand("tee -a output.log", input_mode="stdin")
        >>> await flow().source(data, str).sink(append).execute()
    """

    def __init__(
        self,
        command: Union[str, List[str]],
        *,
        input_mode: str = "args",  # "args", "stdin", or "none"
        output_mode: str = "lines",  # "lines", "all", or "none"
        cwd: Optional[Union[str, Path]] = None,
        env: Optional[Dict[str, str]] = None,
        shell: bool = False,
        timeout: Optional[float] = None,
        check: bool = True,
        encoding: str = "utf-8",
        errors: str = "strict",
    ):
        """Initialize a shell command.
        
        Args:
            command: Command to run (string or list of arguments)
            input_mode: How to pass input ("args", "stdin", or "none")
            output_mode: How to capture output ("lines", "all", or "none")
            cwd: Working directory for the command
            env: Environment variables (None means inherit)
            shell: Whether to run through shell (security risk!)
            timeout: Command timeout in seconds
            check: Whether to raise on non-zero exit
            encoding: Text encoding for stdin/stdout
            errors: How to handle encoding errors
        """
        self.command = command
        self.input_mode = input_mode
        self.output_mode = output_mode
        self.cwd = Path(cwd) if cwd else None
        self.env = env
        self.shell = shell
        self.timeout = timeout
        self.check = check
        self.encoding = encoding
        self.errors = errors
        
        # Parse command if string
        if isinstance(command, str) and not shell:
            self.args = shlex.split(command)
        else:
            self.args = command if isinstance(command, list) else [command]

    async def run(self, input_data: Optional[str] = None) -> ShellResult:
        """Run the command once with optional input."""
        if self.shell:
            cmd = self.command if isinstance(self.command, str) else " ".join(self.args)
            proc = await asyncio.create_subprocess_shell(
                cmd,
                stdin=asyncio.subprocess.PIPE if input_data else None,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.cwd,
                env=self.env,
            )
        else:
            proc = await asyncio.create_subprocess_exec(
                *self.args,
                stdin=asyncio.subprocess.PIPE if input_data else None,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.cwd,
                env=self.env,
            )
        
        try:
            stdout_bytes, stderr_bytes = await asyncio.wait_for(
                proc.communicate(
                    input_data.encode(self.encoding) if input_data else None
                ),
                timeout=self.timeout,
            )
        except asyncio.TimeoutError:
            proc.kill()
            await proc.wait()
            raise TimeoutError(f"Command timed out after {self.timeout}s: {self.command}")
        
        stdout = stdout_bytes.decode(self.encoding, errors=self.errors)
        stderr = stderr_bytes.decode(self.encoding, errors=self.errors)
        
        result = ShellResult(stdout, stderr, proc.returncode, str(self.command))
        
        if self.check and proc.returncode != 0:
            raise RuntimeError(
                f"Command failed with return code {proc.returncode}: {self.command}\n"
                f"stderr: {stderr}"
            )
        
        return result

    async def stream_output(self) -> AsyncIterator[str]:
        """Stream command output line by line (for use as source)."""
        if self.shell:
            cmd = self.command if isinstance(self.command, str) else " ".join(self.args)
            proc = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.cwd,
                env=self.env,
            )
        else:
            proc = await asyncio.create_subprocess_exec(
                *self.args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.cwd,
                env=self.env,
            )
        
        try:
            async for line_bytes in proc.stdout:
                line = line_bytes.decode(self.encoding, errors=self.errors).rstrip('\n\r')
                yield line
        finally:
            if proc.returncode is None:
                proc.kill()
                await proc.wait()

    async def __call__(self, input_item: T) -> Union[str, ShellResult, None]:
        """Make the command callable for use as a transform or sink."""
        if self.input_mode == "none":
            result = await self.run()
        elif self.input_mode == "stdin":
            result = await self.run(str(input_item))
        elif self.input_mode == "args":
            # Append input as additional argument
            original_args = self.args
            self.args = original_args + [str(input_item)]
            try:
                result = await self.run()
            finally:
                self.args = original_args
        else:
            raise ValueError(f"Invalid input_mode: {self.input_mode}")
        
        # Return based on output mode
        if self.output_mode == "none":
            return None
        elif self.output_mode == "all":
            return result.stdout
        elif self.output_mode == "lines":
            # For transform, return stdout content
            return result.stdout.rstrip()
        else:
            raise ValueError(f"Invalid output_mode: {self.output_mode}")


def shell_source(
    command: Union[str, List[str]],
    output_type: type[T] = str,
    *,
    cwd: Optional[Union[str, Path]] = None,
    env: Optional[Dict[str, str]] = None,
    shell: bool = False,
    encoding: str = "utf-8",
    parser: Optional[Callable[[str], T]] = None,
) -> Callable[[], AsyncIterator[T]]:
    """Create a source node from a shell command.
    
    The command's stdout is streamed line by line as flow items.
    
    Args:
        command: Command to run
        output_type: Type of output items (default: str)
        cwd: Working directory
        env: Environment variables
        shell: Whether to use shell
        encoding: Output encoding
        parser: Optional function to parse each line
        
    Returns:
        An async generator function suitable for use with .source()
        
    Examples:
        # Stream system logs
        >>> logs = shell_source("tail -f /var/log/syslog")
        >>> await flow().source(logs, str).sink(print).execute()
        
        # Parse structured data
        >>> def parse_json(line: str) -> dict:
        ...     return json.loads(line)
        >>> events = shell_source("my-event-stream", parser=parse_json)
        >>> await flow().source(events, dict).sink(process_event).execute()
    """
    cmd = ShellCommand(
        command,
        input_mode="none",
        output_mode="lines",
        cwd=cwd,
        env=env,
        shell=shell,
        encoding=encoding,
    )
    
    async def source() -> AsyncIterator[T]:
        async for line in cmd.stream_output():
            if parser:
                yield parser(line)
            else:
                yield line  # type: ignore
    
    return source


def shell_transform(
    command: Union[str, List[str]],
    output_type: type[U] = str,
    *,
    input_mode: str = "stdin",
    cwd: Optional[Union[str, Path]] = None,
    env: Optional[Dict[str, str]] = None,
    shell: bool = False,
    timeout: Optional[float] = None,
    encoding: str = "utf-8",
    parser: Optional[Callable[[str], U]] = None,
) -> Callable[[T], U]:
    """Create a transform node from a shell command.
    
    Input items are passed to the command via stdin or args,
    and stdout is returned as the transformed output.
    
    Args:
        command: Command to run
        output_type: Type of output items
        input_mode: How to pass input ("stdin" or "args")
        cwd: Working directory
        env: Environment variables
        shell: Whether to use shell
        timeout: Command timeout
        encoding: I/O encoding
        parser: Optional function to parse output
        
    Returns:
        An async function suitable for use with .transform()
        
    Examples:
        # Use jq to transform JSON
        >>> jq_filter = shell_transform("jq '.data'", dict, parser=json.loads)
        >>> await flow().source(json_docs, str).transform(jq_filter, dict).sink(save).execute()
        
        # Use sed for text transformation
        >>> clean = shell_transform("sed 's/[^a-zA-Z0-9 ]//g'")
        >>> await flow().source(texts, str).transform(clean, str).sink(print).execute()
    """
    cmd = ShellCommand(
        command,
        input_mode=input_mode,
        output_mode="all",
        cwd=cwd,
        env=env,
        shell=shell,
        timeout=timeout,
        encoding=encoding,
    )
    
    async def transform(item: T) -> U:
        output = await cmd(item)
        if parser and output:
            return parser(output)
        return output  # type: ignore
    
    return transform


def shell_sink(
    command: Union[str, List[str]],
    *,
    input_mode: str = "stdin",
    cwd: Optional[Union[str, Path]] = None,
    env: Optional[Dict[str, str]] = None,
    shell: bool = False,
    timeout: Optional[float] = None,
    encoding: str = "utf-8",
    check: bool = True,
) -> Callable[[T], None]:
    """Create a sink node from a shell command.
    
    Input items are passed to the command, and the command is
    executed for its side effects (no output is returned).
    
    Args:
        command: Command to run
        input_mode: How to pass input ("stdin", "args", or "none")
        cwd: Working directory
        env: Environment variables
        shell: Whether to use shell
        timeout: Command timeout
        encoding: Input encoding
        check: Whether to raise on non-zero exit
        
    Returns:
        An async function suitable for use with .sink()
        
    Examples:
        # Append to file
        >>> append_log = shell_sink("tee -a app.log")
        >>> await flow().source(events, str).sink(append_log).execute()
        
        # Send notifications
        >>> notify = shell_sink("notify-send", input_mode="args")
        >>> await flow().source(alerts, str).sink(notify).execute()
    """
    cmd = ShellCommand(
        command,
        input_mode=input_mode,
        output_mode="none",
        cwd=cwd,
        env=env,
        shell=shell,
        timeout=timeout,
        encoding=encoding,
        check=check,
    )
    
    async def sink(item: T) -> None:
        await cmd(item)
    
    return sink