import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from agentlin.tools.types import BaseTool, ToolResult, ToolParams

# 配置常量
AGENTLIN_CONFIG_DIR = '.agentlin'
DEFAULT_MEMORY_FILENAME = 'MEMORY.md'
MEMORY_SECTION_HEADER = '## AgentLin Memory Bank'

# 全局内存字典（用于临时存储）
memo: dict[str, str] = {}

class MemoryTool(BaseTool):
    """
    保存特定信息或事实到长期记忆的工具。

    当用户明确要求记住某些内容，或当他们陈述重要的、简洁的事实时使用此工具。
    """

    def __init__(self):
        schema = {
            "type": "object",
            "properties": {
                "fact": {
                    "type": "string",
                    "description": "要记住的特定事实或信息。应该是一个清晰的、自包含的陈述。"
                },
                "category": {
                    "type": "string",
                    "description": "记忆的分类，如 'preference'、'personal'、'project'、'setting' 等。可选参数。",
                    "default": "general"
                }
            },
            "required": ["fact"]
        }

        description = """
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
""".strip()

        super().__init__(
            name="save_memory",
            title="保存记忆",
            description=description,
            parameter_schema=schema,
            is_output_markdown=True,
            can_update_output=False,
        )

    def get_global_memory_file_path(self) -> str:
        """获取全局记忆文件路径"""
        home_dir = Path.home()
        config_dir = home_dir / AGENTLIN_CONFIG_DIR
        return str(config_dir / DEFAULT_MEMORY_FILENAME)

    def ensure_newline_separation(self, current_content: str) -> str:
        """确保正确的换行分隔"""
        if len(current_content) == 0:
            return ''
        if current_content.endswith('\n\n'):
            return ''
        if current_content.endswith('\n'):
            return '\n'
        return '\n\n'

    async def perform_add_memory_entry(self, text: str, memory_file_path: str, category: str = "general") -> None:
        """添加记忆条目到文件"""
        # 处理文本
        processed_text = text.strip()
        # 移除可能被误解为 markdown 列表项的前导连字符和空格
        processed_text = processed_text.lstrip('- ').strip()

        # 添加时间戳和分类
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        new_memory_item = f"- [{timestamp}] [{category}] {processed_text}"

        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(memory_file_path), exist_ok=True)

            content = ''
            try:
                with open(memory_file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except FileNotFoundError:
                # 文件不存在，将创建包含标题和条目的新文件
                pass

            header_index = content.find(MEMORY_SECTION_HEADER)

            if header_index == -1:
                # 未找到标题，追加标题然后是条目
                separator = self.ensure_newline_separation(content)
                content += f"{separator}{MEMORY_SECTION_HEADER}\n{new_memory_item}\n"
            else:
                # 找到标题，找到插入新记忆条目的位置
                start_of_section_content = header_index + len(MEMORY_SECTION_HEADER)
                end_of_section_index = content.find('\n## ', start_of_section_content)
                if end_of_section_index == -1:
                    end_of_section_index = len(content)  # 文件末尾

                before_section_marker = content[:start_of_section_content].rstrip()
                section_content = content[start_of_section_content:end_of_section_index].rstrip()
                after_section_marker = content[end_of_section_index:]

                section_content += f"\n{new_memory_item}"
                content = f"{before_section_marker}\n{section_content.lstrip()}\n{after_section_marker}".rstrip() + '\n'

            with open(memory_file_path, 'w', encoding='utf-8') as f:
                f.write(content)

        except Exception as error:
            raise Exception(f"添加记忆条目失败: {str(error)}")

    async def execute(self, params: ToolParams) -> ToolResult:
        """执行保存记忆操作"""
        fact = params.get('fact')
        category = params.get('category', 'general')

        if not fact or not isinstance(fact, str) or not fact.strip():
            error_message = '参数 "fact" 必须是非空字符串。'
            return ToolResult(
                message_content=[{"type": "text", "text": f"错误: {error_message}"}],
                block_list=[{"type": "text", "text": f"错误: {error_message}"}],
            )

        try:
            # 同时保存到内存字典和文件
            memo[f"{category}_{datetime.now().isoformat()}"] = fact

            # 保存到文件
            memory_file_path = self.get_global_memory_file_path()
            await self.perform_add_memory_entry(fact, memory_file_path, category)

            success_message = f'好的，我已经记住了："{fact}"'
            if category != 'general':
                success_message += f' (分类：{category})'

            return ToolResult(
                message_content=[{"type": "text", "text": success_message}],
                block_list=[{"type": "text", "text": success_message}],
                data={"success": True, "message": success_message, "category": category}
            )

        except Exception as error:
            error_message = f"保存记忆失败: {str(error)}"
            return ToolResult(
                message_content=[{"type": "text", "text": f"错误: {error_message}"}],
                block_list=[{"type": "text", "text": f"错误: {error_message}"}],
                data={"success": False, "error": error_message}
            )


def read_memory() -> ToolResult:
    """读取内存中的记忆"""
    if not memo:
        message = "内存中暂无记忆内容。"
    else:
        message = "内存中的记忆：\n" + json.dumps(memo, indent=2, ensure_ascii=False)

    return ToolResult(
        message_content=[{"type": "text", "text": message}],
        block_list=[{"type": "text", "text": message}],
        data=memo,
    )


def read_memory_file(file_path: Optional[str] = None) -> ToolResult:
    """读取记忆文件内容"""
    if file_path is None:
        home_dir = Path.home()
        config_dir = home_dir / AGENTLIN_CONFIG_DIR
        file_path = str(config_dir / DEFAULT_MEMORY_FILENAME)

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if not content.strip():
            message = "记忆文件为空。"
        else:
            message = f"记忆文件内容：\n{content}"

        return ToolResult(
            message_content=[{"type": "text", "text": message}],
            block_list=[{"type": "text", "text": message}],
            data={"file_path": file_path, "content": content}
        )

    except FileNotFoundError:
        message = f"记忆文件不存在：{file_path}"
        return ToolResult(
            message_content=[{"type": "text", "text": message}],
            block_list=[{"type": "text", "text": message}],
            data={"file_path": file_path, "exists": False}
        )
    except Exception as error:
        error_message = f"读取记忆文件失败: {str(error)}"
        return ToolResult(
            message_content=[{"type": "text", "text": error_message}],
            block_list=[{"type": "text", "text": error_message}],
            data={"error": error_message}
        )


# 向后兼容的函数
def ReadMemo():
    """向后兼容的函数，返回内存字典"""
    print(json.dumps(memo, indent=2, ensure_ascii=False))
    return memo


# 创建工具实例
memory_tool = MemoryTool()
