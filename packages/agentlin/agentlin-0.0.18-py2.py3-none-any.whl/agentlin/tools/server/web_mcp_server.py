#!/usr/bin/env python3
import asyncio
from typing import Annotated, Any, Dict, List
from loguru import logger

from fastmcp import FastMCP, Context

from agentlin.tools.tool_web_fetch import web_fetch


mcp = FastMCP(
    "Web Fetch Tool Server",
    version="0.1.0",
)

@mcp.tool(
    name="web_fetch",
    title="WebFetch",
    description="Fetch specific URLs from the news articles to get additional content and context. Use this when you need more details from the original sources.",
)
async def web_fetch_tool(
    urls: Annotated[List[str], "List of URLs to fetch. Only URLs from the provided news articles are available."],
) -> Dict[str, Any]:
    """从URL列表获取网页内容"""
    return await web_fetch(urls)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run Web Fetch MCP SSE-based server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=7780, help="Port to listen on")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    args = parser.parse_args()

    logger.info("Starting Web Fetch MCP Server...")
    logger.info("Available tools: web_fetch")

    mcp.run("http", host=args.host, port=args.port, log_level="debug" if args.debug else "info")
