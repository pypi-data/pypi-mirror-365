"""
支持通过路径或 glob 模式读取多个文件的内容。
对于文本文件，将内容连接成单个字符串；对于图像、PDF、音频和视频文件，返回 base64 编码的数据。
"""

import os
import glob
import mimetypes
import base64
from pathlib import Path
from typing import List, Optional, Dict, Any, Union, Set
import fnmatch
import re

from agentlin.tools.types import BaseTool, ToolResult, ToolParams


# 默认排除模式（与 TypeScript 版本保持一致）
DEFAULT_EXCLUDES = [
    '**/node_modules/**',
    '**/.git/**',
    '**/.vscode/**',
    '**/.idea/**',
    '**/dist/**',
    '**/build/**',
    '**/coverage/**',
    '**/__pycache__/**',
    '**/*.pyc',
    '**/*.pyo',
    '**/*.bin',
    '**/*.exe',
    '**/*.dll',
    '**/*.so',
    '**/*.dylib',
    '**/*.class',
    '**/*.jar',
    '**/*.war',
    '**/*.zip',
    '**/*.tar',
    '**/*.gz',
    '**/*.bz2',
    '**/*.rar',
    '**/*.7z',
    '**/*.doc',
    '**/*.docx',
    '**/*.xls',
    '**/*.xlsx',
    '**/*.ppt',
    '**/*.pptx',
    '**/*.odt',
    '**/*.ods',
    '**/*.odp',
    '**/.DS_Store',
    '**/.env',
]

# 文件类型常量
DEFAULT_ENCODING = 'utf-8'
DEFAULT_MAX_LINES_TEXT_FILE = 2000
MAX_LINE_LENGTH_TEXT_FILE = 2000
DEFAULT_OUTPUT_SEPARATOR_FORMAT = '--- {filePath} ---'
MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024  # 20MB
SVG_MAX_SIZE_BYTES = 1 * 1024 * 1024  # 1MB for SVG files


def _is_within_root(path_to_check: str, root_directory: str) -> bool:
    """检查路径是否在给定的根目录内"""
    normalized_path = os.path.abspath(path_to_check)
    normalized_root = os.path.abspath(root_directory)

    # 确保根目录路径以分隔符结尾以进行正确的 startswith 比较
    if not normalized_root.endswith(os.sep):
        normalized_root += os.sep

    return (
        normalized_path == normalized_root.rstrip(os.sep) or
        normalized_path.startswith(normalized_root)
    )

def _is_binary_file(file_path: str) -> bool:
    """基于内容采样确定文件是否可能是二进制文件"""
    try:
        with open(file_path, 'rb') as f:
            # 读取最多 4KB 或文件大小，取较小者
            file_size = os.path.getsize(file_path)
            if file_size == 0:
                return False  # 空文件不被视为二进制

            buffer_size = min(4096, file_size)
            buffer = f.read(buffer_size)

            if len(buffer) == 0:
                return False

            # 空字节是强指示符
            if b'\x00' in buffer:
                return True

            # 如果 >30% 的非可打印字符，则视为二进制
            non_printable_count = 0
            for byte in buffer:
                if byte < 9 or (byte > 13 and byte < 32):
                    non_printable_count += 1

            return non_printable_count / len(buffer) > 0.3

    except Exception as e:
        # 如果发生任何错误，在这里视为非二进制文件
        return False

def _detect_file_type(file_path: str) -> str:
    """检测文件类型：'text', 'image', 'pdf', 'audio', 'video', 'binary', 'svg'"""
    ext = os.path.splitext(file_path)[1].lower()

    # TypeScript 文件的特殊处理
    if ext == '.ts':
        return 'text'

    if ext == '.svg':
        return 'svg'

    # 使用 mimetypes 模块
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type:
        if mime_type.startswith('image/'):
            return 'image'
        if mime_type.startswith('audio/'):
            return 'audio'
        if mime_type.startswith('video/'):
            return 'video'
        if mime_type == 'application/pdf':
            return 'pdf'

    # 严格的二进制检查，用于常见的非文本扩展名
    binary_extensions = {
        '.zip', '.tar', '.gz', '.exe', '.dll', '.so', '.class', '.jar',
        '.war', '.7z', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
        '.odt', '.ods', '.odp', '.bin', '.dat', '.obj', '.o', '.a',
        '.lib', '.wasm', '.pyc', '.pyo'
    }

    if ext in binary_extensions:
        return 'binary'

    # 基于内容的回退检查
    if _is_binary_file(file_path):
        return 'binary'

    return 'text'


def _process_single_file_content(
    target_directory: str,
    file_path: str,
    offset: Optional[int] = None,
    limit: Optional[int] = None,
) -> Dict[str, Any]:
    """处理单个文件，返回包含内容和元数据的字典"""
    try:
        if not os.path.exists(file_path):
            return {
                'content': None,
                'display': 'File not found.',
                'error': f'File not found: {file_path}',
                'type': 'error'
            }

        if os.path.isdir(file_path):
            return {
                'content': None,
                'display': 'Path is a directory.',
                'error': f'Path is a directory, not a file: {file_path}',
                'type': 'error'
            }

        file_size = os.path.getsize(file_path)
        if file_size > MAX_FILE_SIZE_BYTES:
            return {
                'content': None,
                'display': f'File too large: {file_size / (1024*1024):.2f}MB',
                'error': f'File size exceeds 20MB limit: {file_path}',
                'type': 'error'
            }

        file_type = _detect_file_type(file_path)
        relative_path = os.path.relpath(file_path, target_directory).replace('\\', '/')

        if file_type == 'binary':
            return {
                'content': f'Cannot display content of binary file: {relative_path}',
                'display': f'Skipped binary file: {relative_path}',
                'type': 'binary',
                'relative_path': relative_path
            }

        elif file_type == 'svg':
            if file_size > SVG_MAX_SIZE_BYTES:
                return {
                    'content': None,
                    'display': f'SVG file too large: {file_size / 1024:.1f}KB',
                    'error': f'SVG file exceeds 1MB limit: {file_path}',
                    'type': 'error'
                }

            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            return {
                'content': content,
                'display': f'Read SVG as text: {relative_path}',
                'type': 'text',
                'relative_path': relative_path
            }

        elif file_type == 'text':
            with open(file_path, 'r', encoding=DEFAULT_ENCODING, errors='replace') as f:
                content = f.read()

            lines = content.split('\n')
            original_line_count = len(lines)

            start_line = offset or 0
            effective_limit = limit if limit is not None else DEFAULT_MAX_LINES_TEXT_FILE
            end_line = min(start_line + effective_limit, original_line_count)
            actual_start_line = min(start_line, original_line_count)

            selected_lines = lines[actual_start_line:end_line]

            # 处理行长度截断
            lines_were_truncated_in_length = False
            formatted_lines = []
            for line in selected_lines:
                if len(line) > MAX_LINE_LENGTH_TEXT_FILE:
                    formatted_lines.append(line[:MAX_LINE_LENGTH_TEXT_FILE] + '...[line truncated]')
                    lines_were_truncated_in_length = True
                else:
                    formatted_lines.append(line)

            content_range_truncated = end_line < original_line_count
            is_truncated = content_range_truncated or lines_were_truncated_in_length

            text_content = ''
            if content_range_truncated:
                text_content += f'[Content truncated: showing lines {actual_start_line + 1}-{end_line} of {original_line_count} total lines]\n'
            elif lines_were_truncated_in_length:
                text_content += f'[Some lines truncated at {MAX_LINE_LENGTH_TEXT_FILE} characters]\n'

            text_content += '\n'.join(formatted_lines)

            return {
                'content': text_content,
                'display': '(truncated)' if is_truncated else '',
                'type': 'text',
                'is_truncated': is_truncated,
                'original_line_count': original_line_count,
                'lines_shown': [actual_start_line + 1, end_line],
                'relative_path': relative_path
            }

        elif file_type in ['image', 'pdf', 'audio', 'video']:
            with open(file_path, 'rb') as f:
                content_buffer = f.read()

            base64_data = base64.b64encode(content_buffer).decode('utf-8')

            # 确定 MIME 类型
            mime_type, _ = mimetypes.guess_type(file_path)
            if not mime_type:
                ext = os.path.splitext(file_path)[1].lower()
                if file_type == 'image':
                    mime_type = f'image/{ext[1:]}' if ext else 'image/png'
                elif file_type == 'pdf':
                    mime_type = 'application/pdf'
                elif file_type == 'audio':
                    mime_type = f'audio/{ext[1:]}' if ext else 'audio/mpeg'
                elif file_type == 'video':
                    mime_type = f'video/{ext[1:]}' if ext else 'video/mp4'

            # 返回字典格式的文件内容
            file_content = {
                'type': 'file',
                'inlineData': {
                    'mimeType': mime_type,
                    'data': base64_data
                }
            }

            return {
                'content': file_content,
                'display': f'Read {file_type} file: {relative_path}',
                'type': file_type,
                'relative_path': relative_path
            }

        else:
            return {
                'content': f'Unhandled file type: {file_type}',
                'display': f'Skipped unhandled file type: {relative_path}',
                'error': f'Unhandled file type for {file_path}',
                'type': 'error'
            }

    except Exception as e:
        error_message = str(e)
        display_path = os.path.relpath(file_path, target_directory).replace('\\', '/')
        return {
            'content': f'Error reading file {display_path}: {error_message}',
            'display': f'Error reading file {display_path}: {error_message}',
            'error': f'Error reading file {file_path}: {error_message}',
            'type': 'error'
        }



def _find_files_by_patterns(
    target_directory: str,
    patterns: List[str],
    exclude_patterns: List[str],
    respect_git_ignore: bool = True,
) -> Set[str]:
    """使用 glob 模式查找文件，应用排除规则"""
    files_to_consider = set()

    # 读取 .gitignore 模式
    gitignore_patterns = []
    if respect_git_ignore:
        gitignore_path = os.path.join(target_directory, '.gitignore')
        if os.path.exists(gitignore_path):
            try:
                with open(gitignore_path, 'r', encoding='utf-8') as f:
                    gitignore_patterns = [
                        line.strip() for line in f.readlines()
                        if line.strip() and not line.startswith('#')
                    ]
            except Exception:
                pass  # 忽略读取错误

    # 应用搜索模式
    for pattern in patterns:
        # 确保模式是相对于目标目录的
        if os.path.isabs(pattern):
            pattern = os.path.relpath(pattern, target_directory)

        full_pattern = os.path.join(target_directory, pattern)

        # 使用 glob 查找文件
        try:
            matches = glob.glob(full_pattern, recursive=True)
            for match in matches:
                if os.path.isfile(match) and _is_within_root(match, target_directory):
                    files_to_consider.add(os.path.abspath(match))
        except Exception:
            continue  # 忽略无效模式

    # 应用排除模式
    filtered_files = set()
    all_exclude_patterns = exclude_patterns + gitignore_patterns

    for file_path in files_to_consider:
        relative_path = os.path.relpath(file_path, target_directory).replace('\\', '/')
        should_exclude = False

        for exclude_pattern in all_exclude_patterns:
            # 标准化模式以进行匹配
            if exclude_pattern.startswith('/'):
                exclude_pattern = exclude_pattern[1:]

            # 标准化模式路径分隔符
            exclude_pattern = exclude_pattern.replace('\\', '/')

            # 使用 fnmatch 进行模式匹配
            # 1. 完整路径匹配
            if fnmatch.fnmatch(relative_path, exclude_pattern):
                should_exclude = True
                break

            # 2. 如果模式以 **/ 开头，则匹配任何深度的路径
            if exclude_pattern.startswith('**/'):
                pattern_without_prefix = exclude_pattern[3:]  # 移除 **/
                # 检查文件名是否匹配
                if fnmatch.fnmatch(os.path.basename(file_path), pattern_without_prefix):
                    should_exclude = True
                    break
                # 检查路径的任何部分是否匹配完整模式
                path_parts = relative_path.split('/')
                for i in range(len(path_parts)):
                    sub_path = '/'.join(path_parts[i:])
                    if fnmatch.fnmatch(sub_path, pattern_without_prefix):
                        should_exclude = True
                        break
                if should_exclude:
                    break

            # 3. 简单的文件名匹配
            if fnmatch.fnmatch(os.path.basename(file_path), exclude_pattern):
                should_exclude = True
                break

        if not should_exclude:
            filtered_files.add(file_path)

    return filtered_files


async def read_many_files(
    paths: List[str],
    include: Optional[List[str]] = None,
    exclude: Optional[List[str]] = None,
    recursive: bool = True,
    target_directory: Optional[str] = None,
    use_default_excludes: bool = True,
    respect_git_ignore: bool = True,
) -> Dict[str, Any]:
    """
    读取多个文件的便利函数

    Args:
        paths: 文件路径或 glob 模式列表
        include: 要包含的额外模式
        exclude: 要排除的模式
        recursive: 是否递归搜索
        target_directory: 目标目录
        use_default_excludes: 是否使用默认排除列表
        respect_git_ignore: 是否遵循 .gitignore

    Returns:
        包含处理结果的字典
    """
    try:
        if not paths:
            return ToolResult(
                message_content=[{"type": "text", "text": "Error: No paths provided"}],
                block_list=[],
                data={'error': 'No paths provided'}
            )

        # 准备排除模式
        effective_excludes = []
        if use_default_excludes:
            effective_excludes.extend(DEFAULT_EXCLUDES)
        effective_excludes.extend(exclude)

        # 合并搜索模式
        search_patterns = paths + include

        # 查找文件
        files_to_consider = _find_files_by_patterns(
            target_directory,
            search_patterns,
            effective_excludes,
            respect_git_ignore,
        )

        if not files_to_consider:
            return ToolResult(
                message_content=[{"type": "text", "text": f"No files found matching patterns: {search_patterns}"}],
                block_list=[],
                data={'processed_files': [], 'skipped_files': [], 'target_directory': target_directory}
            )

        # 处理文件
        sorted_files = sorted(files_to_consider)
        processed_files = []
        skipped_files = []
        content_parts = []

        for file_path in sorted_files:
            result = _process_single_file_content(target_directory, file_path)

            if result['type'] == 'error' or result['type'] == 'binary':
                skipped_files.append({
                    'path': result.get('relative_path', file_path),
                    'reason': result['display']
                })
            else:
                processed_files.append(result['relative_path'])

                if result['type'] == 'text':
                    # 为文本文件添加分隔符和内容
                    separator = DEFAULT_OUTPUT_SEPARATOR_FORMAT.format(
                        filePath=result['relative_path'],
                    )
                    content_parts.append({"type": "text", "text": f"\n{separator}\n"})
                    content_parts.append({"type": "text", "text": result['content']})
                else:
                    # 对于图像/PDF/音频/视频文件，添加文件内容
                    content_parts.append(result['content'])

        # 构建显示消息
        display_message = f"### ReadManyFiles Result (Target Dir: `{target_directory}`)\n\n"

        if processed_files:
            display_message += f"**Processed {len(processed_files)} files:**\n"
            for file_path in processed_files:
                display_message += f"- `{file_path}`\n"
            display_message += "\n"

        if skipped_files:
            display_message += f"**Skipped {len(skipped_files)} files:**\n"
            for skipped in skipped_files:
                display_message += f"- `{skipped['path']}`: {skipped['reason']}\n"
            display_message += "\n"

        if not processed_files and not skipped_files:
            display_message += "No files were found or processed.\n"

        # 如果没有内容，添加错误消息
        if not content_parts:
            content_parts.append({"type": "text", "text": "No file content was successfully read."})

        return ToolResult(
            message_content=content_parts,
            block_list=[],
            data={
                'processed_files': processed_files,
                'skipped_files': skipped_files,
                'target_directory': target_directory,
            }
        )

    except Exception as e:
        error_message = f"Error executing multi-file read: {str(e)}"
        return ToolResult(
            message_content=[{"type": "text", "text": error_message}],
            block_list=[],
            data={'error': error_message}
        )


class MultiFilesReadTool(BaseTool):
    """
    用于读取多个文件内容的工具。

    支持通过路径或 glob 模式指定文件，对文本文件连接内容，
    对图像、PDF、音频和视频文件返回 base64 编码数据。
    """

    def __init__(self, target_directory: str = None):
        """
        初始化多文件读取工具

        Args:
            target_directory: 目标目录，如果为 None 则使用当前工作目录
        """
        self.target_directory = target_directory or os.getcwd()

        schema = {
            "type": "object",
            "properties": {
                "paths": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "minLength": 1,
                    },
                    "minItems": 1,
                    "description": "必需。相对于工具目标目录的 glob 模式或路径数组。例如：['src/**/*.ts'], ['README.md', 'docs/']"
                },
                "include": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "minLength": 1,
                    },
                    "description": "可选。要包含的额外 glob 模式。这些与 `paths` 合并。例如：['*.test.ts'] 来专门添加测试文件",
                    "default": []
                },
                "exclude": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "minLength": 1,
                    },
                    "description": "可选。要排除的文件/目录的 glob 模式。如果 useDefaultExcludes 为 true，则添加到默认排除列表。例如：['**/*.log', 'temp/']",
                    "default": []
                },
                "recursive": {
                    "type": "boolean",
                    "description": "可选。是否递归搜索（主要由 glob 模式中的 `**` 控制）。默认为 true",
                    "default": True
                },
                "useDefaultExcludes": {
                    "type": "boolean",
                    "description": "可选。是否应用默认排除模式列表（如 node_modules、.git、二进制文件）。默认为 true",
                    "default": True
                },
                "respect_git_ignore": {
                    "type": "boolean",
                    "description": "可选。是否遵循 .gitignore 模式。默认为 true",
                    "default": True
                }
            },
            "required": ["paths"]
        }

        description = """
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
        """.strip()

        super().__init__(
            name="read_many_files",
            title="读取多个文件",
            description=description,
            parameter_schema=schema,
            is_output_markdown=True,
            can_update_output=False,
        )

    async def execute(self, params: ToolParams) -> ToolResult:
        """执行多文件读取操作

        Args:
            params: 包含读取文件所需参数的字典

        Returns:
            ToolResult 对象，包含处理结果
        """
        paths = params.get('paths', [])
        include = params.get('include', [])
        exclude = params.get('exclude', [])
        recursive = params.get('recursive', True)
        use_default_excludes = params.get('useDefaultExcludes', True)
        respect_git_ignore = params.get('respect_git_ignore', True)

        return await read_many_files(
            paths=paths,
            include=include,
            exclude=exclude,
            recursive=recursive,
            target_directory=self.target_directory,
            use_default_excludes=use_default_excludes,
            respect_git_ignore=respect_git_ignore
        )