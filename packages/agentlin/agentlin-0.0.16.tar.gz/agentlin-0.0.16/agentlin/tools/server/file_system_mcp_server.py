from loguru import logger
from typing import List, Optional, Annotated

from fastmcp import FastMCP
from mcp.types import TextContent, ImageContent

from agentlin.tools.tool_file_system import (
    list_directory as fs_list_directory,
    read_file as fs_read_file,
    write_file as fs_write_file,
    glob as fs_glob,
    search_file_content as fs_search_file_content,
    replace as fs_replace,
)


mcp = FastMCP(
    "File System Tool Server",
    version="0.1.0",
)


@mcp.tool(
    name="list_directory",
    title="ReadFolder",
    description="Lists the names of files and subdirectories directly within a specified directory path. Can optionally ignore entries matching provided glob patterns.",
)
def list_directory(
    path: Annotated[str, "要列出的目录路径"],
    ignore: Annotated[List[str], "要忽略的文件或目录列表，支持glob模式"] = None,
    respect_git_ignore: Annotated[bool, "是否遵循 .gitignore 文件规则"] = True,
) -> str:
    """列出指定目录中的文件和子目录"""
    return fs_list_directory(path, ignore, respect_git_ignore)


@mcp.tool(
    name="read_file",
    title="ReadFile",
    description="Reads and returns the content of a specified file. Supports text, image (PNG, JPG, GIF, WEBP, SVG, BMP), and PDF files. For text files, can read by line range.",
)
def read_file(
    path: Annotated[str, "要读取的文件的绝对路径"],
    offset: Annotated[Optional[int], "文本文件中开始读取的起始行号（从0开始）"] = None,
    limit: Annotated[Optional[int], "最大读取行数"] = None,
):
    """读取并返回指定文件的内容"""
    result = fs_read_file(path, offset, limit)

    # 如果返回的是字典（图像或PDF），需要转换为适当的MCP内容类型
    if isinstance(result, dict) and "inlineData" in result:
        inline_data = result["inlineData"]
        if inline_data["mimeType"].startswith("image/"):
            return [
                ImageContent(
                    type="image",
                    data=inline_data["data"],
                    mimeType=inline_data["mimeType"],
                )
            ]
        else:  # PDF或其他二进制文件
            return [
                TextContent(
                    type="text",
                    text=f"Binary file content (MIME: {inline_data['mimeType']}): {inline_data['data'][:20]}...",
                )
            ]

    # 文本文件直接返回字符串
    return result


@mcp.tool(
    name="write_file",
    title="WriteFile",
    description="Writes content to a specified file. If the file exists, it will be overwritten. If it doesn't exist, a new file will be created along with any necessary parent directories.",
)
def write_file(
    file_path: Annotated[str, "要写入的文件的绝对路径"],
    content: Annotated[str, "要写入文件的内容"],
) -> str:
    """将内容写入指定文件"""
    return fs_write_file(file_path, content)


@mcp.tool(
    name="glob",
    title="FindFiles",
    description="Finds files matching a specific glob pattern and returns a list of absolute paths sorted by modification time (newest first).",
)
def glob(
    pattern: Annotated[str, "用于匹配的glob模式"],
    path: Annotated[Optional[str], "要搜索的目录的绝对路径，若未指定则在当前目录搜索"] = None,
    case_sensitive: Annotated[bool, "是否区分大小写"] = False,
    respect_git_ignore: Annotated[bool, "是否遵循.gitignore"] = True,
) -> str:
    """查找匹配特定glob模式的文件"""
    return fs_glob(pattern, path, case_sensitive, respect_git_ignore)


@mcp.tool(
    name="search_file_content",
    title="SearchText",
    description="Searches for a regular expression pattern within file contents in a specified directory. Can filter files to search using a glob pattern. Returns matching lines with file paths and line numbers.",
)
def search_file_content(
    pattern: Annotated[str, "要搜索的正则表达式"],
    path: Annotated[Optional[str], "要搜索的目录的绝对路径，默认为当前工作目录"] = None,
    include: Annotated[Optional[str], "过滤要搜索的文件的glob模式"] = None,
) -> str:
    """在指定目录内的文件内容中搜索正则表达式模式"""
    return fs_search_file_content(pattern, path, include)


@mcp.tool(
    name="replace",
    title="Edit",
    description="Replaces text in a file. Designed for precise edits, requires old_string to have enough context to uniquely identify the location to modify. By default replaces only one occurrence.",
)
def replace(
    file_path: Annotated[str, "要修改的文件的绝对路径"],
    old_string: Annotated[str, "要替换的原始字符串。如果为空，将创建新文件"],
    new_string: Annotated[str, "用于替换的内容"],
    expected_replacements: Annotated[int, "期望替换的次数"] = 1,
) -> str:
    """用于替换文件中的文本"""
    return fs_replace(file_path, old_string, new_string, expected_replacements)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run MCP SSE-based server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=7778, help="Port to listen on")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    args = parser.parse_args()

    logger.info("Starting File System MCP Server...")
    logger.info("Available tools: list_directory, read_file, write_file, glob, search_file_content, replace")

    mcp.run("http", host=args.host, port=args.port, log_level="debug" if args.debug else "info")
