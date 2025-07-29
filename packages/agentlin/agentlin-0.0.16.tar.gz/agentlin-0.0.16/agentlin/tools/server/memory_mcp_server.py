#!/usr/bin/env python3
import asyncio
import datetime
from typing import Any, Dict, Optional, Annotated
from loguru import logger

from fastmcp import FastMCP, Context

from agentlin.tools.tool_memo import memory_tool, read_memory, read_memory_file


mcp = FastMCP(
    "Memory Tool Server",
    version="0.1.0",
)

@mcp.tool(
    name="save_memory",
    title="保存记忆",
    description="""
保存特定信息或事实到长期记忆。

使用此工具的情况：
- 当用户明确要求记住某些内容时（例如："记住我喜欢在披萨上放菠萝"、"请保存这个：我的猫叫 Whiskers"）
- 当用户陈述关于他们自己、他们的偏好或环境的清晰、简洁的事实，这些事实对于未来的交互提供更个性化和有效的帮助很重要时

不要使用此工具：
- 记住只与当前会话相关的对话上下文
- 保存长篇、复杂或冗长的文本。事实应该相对简短和切中要点
- 如果你不确定信息是否值得长期记住。如有疑问，你可以询问用户："我应该为你记住这个吗？"

参数：
- fact (string, 必需): 要记住的特定事实或信息。这应该是一个清晰的、自包含的陈述
- category (string, 可选): 记忆分类，默认为 'general'
""".strip(),
)
async def save_memory_tool(
    ctx: Context,
    fact: Annotated[str, "要记住的特定事实或信息"],
    category: Annotated[str, "记忆分类，默认为 'general'"] = "general",
):
    """保存记忆到长期存储"""
    result = await ctx.elicit(
        f"""
保存记忆：
分类：{category}
内容：{fact}
""".strip(),
        None,
    )
    if result.action == "accept":
        return await memory_tool.execute({"fact": fact, "category": category})
    else:
        return {
            "success": False,
            "error": "Memory save not accepted",
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }


@mcp.tool(
    name="read_memory",
    title="读取内存记忆",
    description="读取内存中的临时记忆内容。",
)
async def read_memory_tool(ctx: Context):
    """读取内存中的记忆"""
    tool_result = read_memory()
    return {
        "success": True,
        "data": tool_result.data,
        "message": "内存记忆读取成功",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }


@mcp.tool(
    name="read_memory_file",
    title="读取记忆文件",
    description="读取存储在文件中的长期记忆内容。",
)
async def read_memory_file_tool(
    file_path: Annotated[Optional[str], "要读取的记忆文件路径，None 表示使用默认路径 .agentlin/MEMORY.md"] = None,
):
    """读取记忆文件内容"""
    return read_memory_file(file_path)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run MCP SSE-based server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=7778, help="Port to listen on")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    args = parser.parse_args()

    logger.info("Starting Memory MCP Server...")
    logger.info("Available tools: save_memory, read_memory, read_memory_file")

    mcp.run("http", host=args.host, port=args.port, log_level="debug" if args.debug else "info")

