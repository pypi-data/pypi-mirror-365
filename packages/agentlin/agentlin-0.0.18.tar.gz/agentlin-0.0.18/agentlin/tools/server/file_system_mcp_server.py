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
from agentlin.tools.tool_read_many_files import read_many_files as fs_read_many_files


TARGET_DIRECTORY = "."  # 默认目标目录，可以通过命令行参数覆盖

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
    path: Annotated[Optional[str], "要列出的目录路径"] = None,
    ignore: Annotated[Optional[List[str]], "要忽略的文件或目录列表，支持glob模式"] = None,
    respect_git_ignore: Annotated[bool, "是否遵循 .gitignore 文件规则"] = True,
) -> str:
    """列出指定目录中的文件和子目录"""
    if not path:
        global TARGET_DIRECTORY
        path = TARGET_DIRECTORY
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
    absolute_file_path: Annotated[str, "要写入的文件的绝对路径"],
    content: Annotated[str, "要写入文件的内容"],
) -> str:
    """将内容写入指定文件"""
    return fs_write_file(absolute_file_path, content)


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
    if not path:
        global TARGET_DIRECTORY
        path = TARGET_DIRECTORY
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
    if not path:
        global TARGET_DIRECTORY
        path = TARGET_DIRECTORY
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


@mcp.tool(
    name="read_many_files",
    title="ReadManyFiles",
    description="""
从由路径或 glob 模式指定的多个文件中读取内容。对于文本文件，将其内容连接到单个字符串中。
主要设计用于基于文本的文件。但是，如果在 'paths' 参数中明确包含文件名或扩展名，
它也可以处理图像（如 .png、.jpg）和 PDF (.pdf) 文件。对于这些明确请求的非文本文件，
其数据以适合模型使用的格式（如 base64 编码）读取和包含。

此工具在需要理解或分析文件集合时很有用，例如：
- 获取代码库或其部分的概览（如 'src' 目录中的所有 TypeScript 文件）
- 如果用户询问关于代码的广泛问题，找到特定功能的实现位置
- 审查文档文件（如 'docs' 目录中的所有 Markdown 文件）
- 从多个配置文件收集上下文
- 当用户要求"读取 X 目录中的所有文件"或"显示所有 Y 文件的内容"时

当用户的查询暗示需要同时获取多个文件的内容以进行上下文分析或总结时，请使用此工具。
对于文本文件，使用默认的 UTF-8 编码和文件内容之间的 '--- {filePath} ---' 分隔符。
确保路径相对于目标目录。支持 'src/**/*.js' 等 glob 模式。
除非明确请求为图像/PDF，否则通常跳过其他二进制文件。
除非 'useDefaultExcludes' 为 false，否则默认排除适用于常见非文本文件和大型依赖目录。
""".strip(),
)
def read_many_files(
    paths: Annotated[List[str], "必需。相对于工具目标目录的 glob 模式或路径数组。例如：['src/**/*.ts'], ['README.md', 'docs/']"],
    include: Annotated[Optional[List[str]], "可选。要包含的额外 glob 模式。这些与 `paths` 合并。例如：['*.test.ts'] 来专门添加测试文件"] = None,
    exclude: Annotated[Optional[List[str]], "可选。要排除的 glob 模式。这些与 `paths` 合并。例如：['*.spec.ts'] 来专门排除测试文件"] = None,
    recursive: Annotated[bool, "可选。是否递归搜索（主要由 glob 模式中的 `**` 控制）。默认为 true"] = True,
    use_default_excludes: Annotated[bool, "可选。是否应用默认排除模式列表（如 node_modules、.git、二进制文件）。默认为 true"] = True,
    respect_git_ignore: Annotated[bool, "可选。是否遵循 .gitignore 文件规则。默认为 true"] = True,
) -> str:
    """从多个文件中读取内容"""
    global TARGET_DIRECTORY
    return fs_read_many_files(
        paths,
        include,
        exclude,
        recursive,
        TARGET_DIRECTORY,
        use_default_excludes,
        respect_git_ignore,
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run MCP SSE-based server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=7779, help="Port to listen on")
    parser.add_argument("--home", type=str, default=None, help="Target directory for file operations")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    args = parser.parse_args()
    if args.home:
        TARGET_DIRECTORY = args.home

    logger.info("Starting File System MCP Server...")
    logger.info("Available tools: list_directory, read_file, write_file, glob, search_file_content, replace")

    mcp.run("http", host=args.host, port=args.port, log_level="debug" if args.debug else "info")
