#!/usr/bin/env python3
import asyncio
import datetime
from typing import Any, Dict, Optional
from loguru import logger

from fastmcp import FastMCP, Context

from agentlin.tools.tool_bash import execute_command


mcp = FastMCP(
    "Bash Command Tool Server",
    version="0.1.0",
)

@mcp.tool(
    name="execute_command",
    title="ExecuteCommand",
    description="Execute a bash command on the host machine and return the result with stdout, stderr, and exit code.",
)
async def execute_command_tool(
    ctx: Context,
    command: str,
    cwd: Optional[str] = None,
    timeout: int = 30,
):
    """执行bash命令并返回结果"""
    result = await ctx.elicit(
        f"""
```bash
{command}
```
""".strip(),
        None,
    )
    if result.action == "accept":
        result = await execute_command(command, cwd, timeout)
    else:
        result = {
            "success": False,
            "error": "Command not accepted",
            "stdout": "",
            "stderr": "",
            "code": -1,
            "command": command,
            "executedAt": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }
    return result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run MCP SSE-based server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=7779, help="Port to listen on")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    args = parser.parse_args()

    logger.info("Starting Bash Command MCP Server...")
    logger.info("Available tools: execute_command")

    mcp.run("http", host=args.host, port=args.port, log_level="debug" if args.debug else "info")
