from pathlib import Path
from typing_extensions import Any, AsyncGenerator, Union, AsyncIterable
import asyncio
import os
import sys

from agentlin.core.types import *
from agentlin.core.agent_schema import AgentCore, parse_config_from_ipynb
from agentlin.route.task_manager import InMemoryTaskManager
from agentlin.route.agent_message_queue import AgentMessageQueue


class CodeInterpreterConfig(BaseModel):
    jupyter_host: str  # Jupyter host URL
    jupyter_port: int  # Jupyter port
    jupyter_token: str  # Jupyter token
    jupyter_timeout: int  # Jupyter timeout
    jupyter_username: str  # Jupyter username


class AgentConfig(BaseModel):
    id: str
    name: str
    description: str
    version: str
    engine: str
    model: str
    developer_prompt: str
    code_for_agent: str
    code_for_interpreter: str
    tool_mcp_config: dict[str, Any] = {
        "mcpServers": {
            "aime_sse_server": {"url": "http://localhost:7778/tool_mcp"},
        }
    }
    code_mcp_config: dict[str, Any] = {
        "mcpServers": {
            "aime_sse_server": {"url": "http://localhost:7778/code_mcp"},
        }
    }
    a2a_config: dict[str, Any] = {}
    code_interpreter_config: CodeInterpreterConfig
    inference_args: dict[str, Any] = {}

    # 内置工具列表
    builtin_tools: list[dict[str, Any]] = [
        {
            "type": "function",
            "function": {
                "name": "CodeInterpreter",
                "description": "在受限、安全的沙盒环境中执行 Python 3 代码的解释器，可用于数据处理、科学计算、自动化脚本、可视化等任务，支持大多数标准库及常见第三方科学计算库。",
                "parameters": {
                    "type": "object",
                    "required": ["code"],
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "要执行的 Python 代码",
                        }
                    },
                },
            },
        },
    ]


async def get_agent_id(host_frontend_id: str) -> str:
    frontend_to_agent_map = {
        "AInvest": "aime",
        "iWencai": "wencai",
    }
    return frontend_to_agent_map.get(host_frontend_id, "aime")


async def get_agent_config(agent_id: str) -> AgentConfig:
    # 这里可以根据 agent_id 从数据库或配置文件中获取 AgentConfig
    # 这里使用一个示例配置
    path = Path(__file__).parent.parent.parent / "assets/aime/main.ipynb"
    code_for_interpreter, code_for_agent, developer_prompt = parse_config_from_ipynb(path)
    json_data = {
        "id": "aime",
        "name": "AIME Agent",
        "description": "AIME Agent for handling user requests",
        "version": "1.0.0",
        "engine": "api",
        "model": "o3",
        "developer_prompt": developer_prompt,
        "code_for_interpreter": code_for_interpreter,
        "code_for_agent": code_for_agent,
        "a2a_config": {},
        "tool_mcp_config": {
            "mcpServers": {
                # "aime_sse_server": {"url": "http://localhost:7778/tool_mcp"},
                # "web": {"url": "http://localhost:7779/web_mcp"},
                "file_system": {"url": "http://localhost:7779/file_system_mcp"},
            }
        },
        "code_mcp_config": {
            "mcpServers": {
                "aime_sse_server": {"url": "http://localhost:7778/code_mcp"},
            }
        },
        "code_interpreter_config": {
            "jupyter_host": "localhost",
            "jupyter_port": 8888,
            "jupyter_token": "jupyter_server_token",
            "jupyter_timeout": 60,
            "jupyter_username": "user",
        },
        "inference_args": {
            "debug": True,
        },
        "builtin_tools": [
            {
                "type": "function",
                "function": {
                    "name": "CodeInterpreter",
                    "description": "在受限、安全的沙盒环境中执行 Python 3 代码的解释器，可用于数据处理、科学计算、自动化脚本、可视化等任务，支持大多数标准库及常见第三方科学计算库。",
                    "parameters": {
                        "type": "object",
                        "required": ["code"],
                        "properties": {
                            "code": {
                                "type": "string",
                                "description": "要执行的 Python 代码",
                            }
                        },
                    },
                },
            },
        ],
        # user
        "language": "zh",
        "instruction": "我喜欢含有图表的回答，请尽量使用图表来展示数据。",
    }
    config = AgentConfig.model_validate(json_data)
    return config


class AgentTaskManager(InMemoryTaskManager, AgentMessageQueue):
    def __init__(
        self,
        agent_id: str,
        *,
        rabbitmq_host: str = "localhost",
        rabbitmq_port: int = 5672,
        auto_ack: bool = False,
        reconnect_initial_delay: float = 5.0,
        reconnect_max_delay: float = 60.0,
        message_timeout: float = 30.0,
        rpc_timeout: float = 30.0,
    ):
        InMemoryTaskManager.__init__(self)
        AgentMessageQueue.__init__(
            self,
            agent_id=agent_id,
            rabbitmq_host=rabbitmq_host,
            rabbitmq_port=rabbitmq_port,
            auto_ack=auto_ack,
            reconnect_initial_delay=reconnect_initial_delay,
            reconnect_max_delay=reconnect_max_delay,
            message_timeout=message_timeout,
            rpc_timeout=rpc_timeout,
        )

    async def on_send_task_subscribe(self, request: SendTaskStreamingRequest) -> AsyncIterable[SendTaskStreamingResponse]:
        await self.upsert_task(request.params)
        task_send_params: TaskSendParams = request.params
        return self._stream_generator(request, request.id, task_send_params.id)

    async def _stream_generator(self, request: SendTaskStreamingRequest, request_id: str, task_id: str) -> AsyncIterable[SendTaskStreamingResponse]:
        task_send_params: TaskSendParams = request.params
        payload = task_send_params.payload
        session_id = task_send_params.sessionId
        history_messages: list[DialogData] = payload["history_messages"]
        inference_args: dict = payload.get("inference_args", {})

        # 获取OpenAI配置
        model = inference_args.get("model", "gpt-4")
        max_tokens = inference_args.get("max_tokens", 10 * 1024)
        temperature = inference_args.get("temperature", 0.7)
        tools = inference_args.get("tools", None)

        try:
            # 发送任务状态更新 - 开始处理
            resp = await self.working_streaming_response(request_id, task_id)
            yield resp

            # 调用OpenAI流式API
            stream = await self.client.chat.completions.create(
                model=model,
                messages=history_messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True,
                tools=tools,
            )

            # 处理流式响应
            async for chunk in stream:
                # 发送增量内容更新
                yield SendTaskStreamingResponse(
                    id=request.id,
                    result=TaskArtifactUpdateEvent(
                        id=task_send_params.id,
                        metadata=chunk.model_dump(),
                    ),
                )
            # 发送最终完成响应
            resp = await self.complete_streaming_response(request_id, task_id)
            yield resp

        except Exception as e:
            # 处理错误情况
            error = JSONRPCError(code=-32000, message=f"处理请求时发生错误: {str(e)}")
            resp = await self.fail_streaming_response(request_id, task_id, error)
            yield resp

    async def on_send_task(self, request: SendTaskRequest) -> SendTaskResponse:
        await self.upsert_task(request.params)
        return await self._invoke(request)

    async def _invoke(self, request: SendTaskRequest) -> SendTaskResponse:
        task_send_params: TaskSendParams = request.params
        payload = task_send_params.payload
        session_id = task_send_params.sessionId
        history_messages: list[DialogData] = payload["history_messages"]
        inference_args: dict = payload.get("inference_args", {})
        response = self.agent.inference(history_messages, **inference_args)
        task = await self.update_store(
            task_send_params.id,
            TaskStatus(state=TaskState.COMPLETED),
            response,
        )
        return SendTaskResponse(id=request.id, result=task)
