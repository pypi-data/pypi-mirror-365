from collections import defaultdict
from pathlib import Path
from typing_extensions import Any, AsyncIterable
import json
import uuid
from fastmcp import Client as MCPClient
from loguru import logger

from deeplin.inference_engine import build_inference_engine
from agentlin.core.types import *
from agentlin.core.agent_schema import AgentCore, content_to_text, extract_code, extract_thought, parse_config_from_ipynb, parse_function_call_response, remove_thoughts, messages_to_text
from agentlin.route.agent_task_manager import AgentConfig, CodeInterpreterConfig, get_agent_id, get_agent_config
from agentlin.route.reference_manager import ReferenceManager
from agentlin.route.task_manager import InMemoryTaskManager, merge_streams
from agentlin.route.tool_task_manager import ToolTaskManager
from agentlin.route.code_task_manager import CodeTaskManager, ExecuteRequest
from agentlin.route.model_task_manager import ModelTaskManager
from agentlin.tools.tool_calendar import format_datetime_with_holiday
from agentlin.tools.types import ToolCallSchema, ToolResult



class SessionState(BaseModel):
    session_id: str
    user_id: str
    host_frontend_id: str
    host_agent_id: str
    host_code_kernel_id: Optional[str] = None
    agent_config: AgentConfig

    # 短期记忆
    history_messages: list[DialogData] = []
    thought_messages: list[DialogData] = []
    execution_messages: list[DialogData] = []  # 代码解释器运行记录
    allowed_tools: Optional[list[str]] = None  # 允许的工具列表. None 为允许所有，[] 为不允许任何
    response_id2references: dict[str, ReferenceManager] = {}  # 引用池, 用于溯源

    # 长期记忆
    instruction: str = ""  # 用户指令
    user_profile: str = ""  # 用户个人信息
    language: Literal["zh", "en"] = "en"  # 用户语言

    # 运行时 - 这些属性不参与 BaseModel 的序列化和验证
    model_config = {"arbitrary_types_allowed": True, "extra": "allow"}

    def __init__(self, **data):
        # 提取运行时管理器，避免传入 BaseModel 验证
        model_task_manager = data.pop("model_task_manager", None)
        tool_task_manager = data.pop("tool_task_manager", None)
        code_task_manager = data.pop("code_task_manager", None)

        # 先调用父类的 __init__
        super().__init__(**data)

        # 然后设置运行时属性
        self.model_task_manager: ModelTaskManager = model_task_manager
        self.tool_task_manager: ToolTaskManager = tool_task_manager
        self.code_task_manager: CodeTaskManager = code_task_manager


class SessionRequest(BaseModel):
    trace_id: str
    user_id: str
    host_frontend_id: str
    user_message_content: list[ContentData]

    msg_key: Optional[str] = None
    agent_config: Optional[AgentConfig] = None

    additional_tools: Optional[list[ToolCallSchema]] = None
    additional_allowed_tools: Optional[list[str]] = None
    instruction: Optional[str] = None
    inference_args: Optional[dict[str, Any]] = None
    cwd: Optional[str] = None  # 当前工作目录, 用于 file_system_mcp 和代码解释器


"""
对工具的管理
Tool Index:
1. a: desc
2. b: desc

built-in tools:
load_tools_by_id(["a", "b", "c"])
offload_tools_by_id(["a", "b"]：？
"""

"""
长期记忆
对对话消息历史的管理
<chat-memory>
Dialog ID: 1
2023-10-01 12:00:00 User: 你好，今天的天气怎么样？
2023-10-01 12:00:01 Bot: 你好！今天的天气晴朗，适合出行。

Dialog ID: 2
2023-10-01 12:00:02 User: 明天的天气预报是什么？
2023-10-01 12:00:03 Bot: 明天的天气预报显示有小雨，气温在18到22度之间。
</chat-memory>

built-in tools:
search_dialog(query="a")
fetch_dialog_by_id(["a", "b", "c"])
"""


class SessionTaskManager(InMemoryTaskManager):
    def __init__(self, debug=False):
        super().__init__()
        self.sessions: dict[str, SessionState] = {}
        self.debug = debug

    async def build_model_task_manager(self, session_id: str, agent_config: AgentConfig) -> ModelTaskManager:
        engine = agent_config.engine
        model = agent_config.model
        engine = build_inference_engine(engine, model)
        agent_core = AgentCore(
            engine=engine,
        )
        return ModelTaskManager(agent_core)

    async def build_tool_task_manager(self, session_id: str, agent_config: AgentConfig) -> ToolTaskManager:
        tool_mcp_config = agent_config.tool_mcp_config
        tool_mcp_client = MCPClient(tool_mcp_config)
        # async with tool_mcp_client:
        #     tools = await tool_mcp_client.list_tools()
        tool_task_manager = ToolTaskManager(
            agent_id=agent_config.id,
            config=tool_mcp_config,
        )
        return tool_task_manager

    async def build_code_task_manager(self, session_id: str, agent_config: AgentConfig) -> CodeTaskManager:
        code_interpreter_config = agent_config.code_interpreter_config
        if not code_interpreter_config:
            raise ValueError("Code interpreter configuration is required for CodeTaskManager.")
        return CodeTaskManager(
            jupyter_host=code_interpreter_config.jupyter_host,
            jupyter_port=code_interpreter_config.jupyter_port,
            jupyter_token=code_interpreter_config.jupyter_token,
            jupyter_timeout=code_interpreter_config.jupyter_timeout,
            jupyter_username=code_interpreter_config.jupyter_username,
        )

    def build_system_code(self, session_id: str, session_state: SessionState) -> str:
        code_mcp_config = session_state.agent_config.code_mcp_config
        code_for_interpreter = session_state.agent_config.code_for_interpreter
        total_code = code_for_interpreter.replace("{code_mcp_config}", json.dumps(code_mcp_config, ensure_ascii=False))
        # total_code = total_code + code_for_agent
        if self.debug:
            logger.debug(f"Total system code for session {session_id}:\n{total_code}")
        return total_code

    def build_system_content(self, session_id: str, session_state: SessionState) -> str:
        developer_prompt = session_state.agent_config.developer_prompt
        user_profile = session_state.user_profile
        code_for_agent = session_state.agent_config.code_for_agent

        developer_prompt = developer_prompt.replace("{{code_functions}}", code_for_agent)
        developer_prompt = developer_prompt.replace("{{all_user_profile}}", user_profile)

        system_content = [
            {"type": "text", "text": developer_prompt},
        ]
        return system_content

    def query_nlu(self, query: str):
        # 这里可以调用 NLU 服务进行查询
        return ""

    async def lazy_init_kernel(self, session_id: str, session_state: SessionState) -> str:
        kernel_id = session_state.host_code_kernel_id
        if kernel_id:
            return kernel_id
        code_task_manager = session_state.code_task_manager
        kernel_id = code_task_manager.create_kernel()
        session_state.host_code_kernel_id = kernel_id
        system_code = self.build_system_code(session_id, session_state)
        req = ExecuteRequest(
            kernel_id=kernel_id,
            code=system_code,
            mode="full",
        )
        request = SendTaskRequest(
            params=TaskSendParams(
                sessionId=session_id,
                payload=req.model_dump(),
            )
        )
        await code_task_manager.on_send_task(request)
        return kernel_id

    async def create_session(
        self,
        session_id: str,
        user_id: str,
        host_frontend_id: str,
        agent_config: Optional[AgentConfig] = None,
    ) -> SessionState:
        host_agent_config = agent_config
        if host_agent_config is None:
            host_agent_id = await get_agent_id(host_frontend_id)
            host_agent_config = await get_agent_config(host_agent_id)
        host_agent_id = host_agent_config.id

        model_task_manager = await self.build_model_task_manager(session_id, host_agent_config)
        tool_task_manager = await self.build_tool_task_manager(session_id, host_agent_config)
        code_task_manager = await self.build_code_task_manager(session_id, host_agent_config)

        state = SessionState(
            session_id=session_id,
            user_id=user_id,
            host_frontend_id=host_frontend_id,
            host_agent_id=host_agent_id,
            host_code_kernel_id=None,
            agent_config=host_agent_config,
            tool_task_manager=tool_task_manager,
            code_task_manager=code_task_manager,
            model_task_manager=model_task_manager,
        )
        self.sessions[session_id] = state
        return state

    def get_session(self, session_id: str):
        return self.sessions.get(session_id, None)

    def delete_session(self, session_id: str):
        if session_id in self.sessions:
            session_state = self.sessions[session_id]
            kernel_id = session_state.host_code_kernel_id
            if kernel_id:
                session_state.code_task_manager.delete_kernel(kernel_id)
            del self.sessions[session_id]

    async def _stream_generator(
        self,
        request_id: int | str | None,
        task_id: str,
        session_id: str,
        req: SessionRequest,
    ) -> AsyncIterable[SendTaskStreamingResponse]:
        # 响应优化，立即接受任务
        resp = await self.working_streaming_response(request_id=request_id, task_id=task_id)
        yield resp

        # 开始处理任务

        # 获得上下文
        user_id = req.user_id
        host_frontend_id = req.host_frontend_id
        user_message_content = req.user_message_content
        msg_key = req.msg_key or f"msg_{uuid.uuid4().hex}"

        session_state = self.get_session(session_id)
        if session_state is None or req.agent_config is not None:
            # 新的 session，或者新的 agent，都需要重新开一个 session
            session_state = await self.create_session(
                session_id,
                user_id,
                host_frontend_id,
                agent_config=req.agent_config,
            )
        if req.instruction is not None:
            session_state.instruction = req.instruction

        model_task_manager = session_state.model_task_manager
        tool_task_manager = session_state.tool_task_manager
        code_task_manager = session_state.code_task_manager
        history_messages: list[dict] = session_state.history_messages
        thought_messages: list[dict] = session_state.thought_messages

        # 确认 tools 有哪些
        builtin_tools = session_state.agent_config.builtin_tools
        registered_tools = await tool_task_manager.get_tools(session_state.allowed_tools)
        registered_tools = [{"type": "function", "function": tool} for tool in registered_tools]
        tools = []
        tools.extend(builtin_tools)
        tools.extend(registered_tools)
        if req.additional_tools:
            for tool in req.additional_tools:
                tool_name = tool.get("function", {}).get("name")
                if tool_name in req.additional_allowed_tools:
                    tools.append(tool)

        # if self.debug:
        #     logger.debug(f"Session {session_id} tools: {json.dumps(tools, ensure_ascii=False, indent=2)}")

        # 确认推理参数
        inference_args: dict = {
            "tools": tools,
        }
        inference_args.update(session_state.agent_config.inference_args)
        if req.inference_args:
            inference_args.update(req.inference_args)
        if self.debug:
            logger.debug(f"Session {session_id} inference_args: {json.dumps(inference_args, ensure_ascii=False, indent=2)}")

        # 初始化引用管理器
        reference_manager = ReferenceManager()
        session_state.response_id2references[task_id] = reference_manager

        current_step = 0
        if len(thought_messages) > 0:
            current_step = sum([1 for m in thought_messages if m["role"] == "assistant"])

        if len(history_messages) == 0:
            system_content = self.build_system_content(session_id, session_state)
            history_messages.append({"role": "system", "content": system_content})

        # 我们把跟用户对话时效性强相关的内容放在 role: "user" 中，避免 system content 的缓存失效
        query = content_to_text(user_message_content)
        nlu = self.query_nlu(query)
        language = session_state.language
        current_time = datetime.datetime.now()
        current_time = format_datetime_with_holiday(current_time, language=language)
        if len(history_messages) == 0:
            prefix_content = [
                {"type": "text", "text": session_state.instruction},
                {"type": "text", "text": f"Current time: {current_time}"},
                {"type": "text", "text": f"Language: {language}"},
                {"type": "text", "text": f"NLU: {nlu}" if nlu else ""},
                {"type": "text", "text": f"User Query:\n\n"},
            ]
        else:
            prefix_content = [
                {"type": "text", "text": f"Current time: {current_time}"},
                {"type": "text", "text": f"Language: {language}"},
                {"type": "text", "text": f"NLU: {nlu}" if nlu else ""},
                {"type": "text", "text": f"User Query:\n\n"},
            ]
        history_messages.append({"role": "user", "content": prefix_content + user_message_content})

        while True:
            current_step += 1
            if self.debug:
                logger.debug(f"当前推理深度: {current_step}, 历史消息数量: {len(history_messages)}")
            # 调用推理引擎获取回复
            messages = history_messages + thought_messages
            if self.debug:
                logger.debug(messages_to_text(messages))

            reasoning_content = []
            response = model_task_manager.agent.engine.inference_one(messages, **inference_args)[0]
            if self.debug:
                logger.debug(f"🤖【assistant】: {response}")

            # 先考虑把 tool_calls 整理出来。整理完可能是空列表。
            # "tool_calls": [
            #     {
            #         "function": {
            #             "arguments": "{}",
            #             "name": "Search"
            #         },
            #         "id": "call_g16uvNKM2r7L36PcHmgbPAAo",
            #         "type": "function"
            #     }
            # ]
            tool_calls: list[dict] = []
            if isinstance(response, dict):
                # TODO 把 reasoning 给前端
                tool_calls.append(response)
            elif isinstance(response, list):
                # TODO 把 reasoning 给前端
                tool_calls.extend(response)
            else:
                thought = extract_thought(response)
                if thought:
                    reasoning_content.append({"type": "text", "text": [{"type": "text", "text": "<think>"}]})
                    reasoning_content.append({"type": "text", "text": thought})
                    reasoning_content.append({"type": "text", "text": [{"type": "text", "text": "</think>"}]})

                response_without_thoughts = remove_thoughts(response)
                code = extract_code(response_without_thoughts)
                call_id = f"call_{uuid.uuid4().hex}"
                if code and len(code.strip()) > 0:
                    call_args = {
                        "code": code,
                    }
                    tool_call = {
                        "id": call_id,
                        "type": "function",
                        "function": {
                            "arguments": json.dumps(call_args, ensure_ascii=False),
                            "name": "CodeInterpreter",
                        },
                    }
                    tool_calls.append(tool_call)

            if reasoning_content:
                yield SendTaskStreamingResponse(
                    id=request_id,
                    result=TaskArtifactUpdateEvent(
                        id=task_id,
                        metadata={
                            "block_list": reasoning_content,
                            "msg_key": msg_key,
                            "current_step": current_step,
                            "key": f"{msg_key}_assistant_thought_{current_step}",
                        },
                    ),
                )
                thought_messages.append({"role": "assistant", "content": reasoning_content})

            if tool_calls:
                # 1. 开始执行
                id_name_args_list: list[tuple[str, str, dict[str, Any]]] = []
                block_list = []
                for tool_call in tool_calls:
                    call_id, call_name, call_args = parse_function_call_response(tool_call)
                    id_name_args_list.append((call_id, call_name, call_args))
                    block_list.append(
                        {
                            "type": "tool_call",
                            "data": {
                                "tool_name": call_name,
                                "tool_args": call_args,
                                "call_id": call_id,
                            },
                        }
                    )
                yield SendTaskStreamingResponse(
                    id=request_id,
                    result=TaskArtifactUpdateEvent(
                        id=task_id,
                        metadata={
                            "block_list": block_list,
                            "msg_key": msg_key,
                            "current_step": current_step,
                            "key": f"{msg_key}_assistant_msg_{current_step}",
                        },
                    ),
                )
                # 2. 记录工具调用到上下文
                thought_messages.append({"role": "assistant", "content": "", "tool_calls": tool_calls})

                # 3. 执行
                call_response_streams = []  # 冷流。放进去的流只有定义，还未执行
                call_id_for_code_interpreter = None
                for call_id, call_name, call_args in id_name_args_list:
                    if call_name == "CodeInterpreter":
                        code = call_args.get("code", "")
                        if call_id_for_code_interpreter is not None:
                            error = JSONRPCError(code=-32000, message="Only one CodeInterpreter call is allowed in a single step.")
                            logger.error(error.message)
                            resp = await self.fail_streaming_response(request_id=request_id, task_id=task_id, error=error)
                            yield resp
                            return
                        call_id_for_code_interpreter = call_id
                        kernel_id = await self.lazy_init_kernel(session_id, session_state)

                        # 3. 执行代码
                        req = ExecuteRequest(kernel_id=kernel_id, code=code, mode="full", msg_id=call_id)
                        code_request = SendTaskStreamingRequest(
                            id=request_id,
                            params=TaskSendParams(
                                id=call_id,
                                sessionId=session_id,
                                payload=req.model_dump(),
                            ),
                        )
                        call_response_stream = await code_task_manager.on_send_task_subscribe(code_request)
                    else:
                        # 3. 执行工具调用
                        tool_request = SendTaskRequest(
                            id=request_id,
                            params=TaskSendParams(
                                id=call_id,
                                sessionId=session_id,
                                payload={
                                    "call_name": call_name,
                                    "call_args": call_args,
                                },
                            ),
                        )
                        call_response_stream = await tool_task_manager.on_send_task_subscribe(tool_request)
                    call_response_streams.append(call_response_stream)

                # 4. 处理执行结果, 处理引用
                call_id_to_result: dict[str, ToolResult] = defaultdict(lambda: ToolResult(message_content=[], block_list=[]))
                async for call_response in merge_streams(*call_response_streams):  # 冷流变“热“：开始正式执行。merge 表示多个流的异步并行合并
                    if self.debug:
                        logger.debug(call_response)
                    if isinstance(call_response, SendTaskStreamingResponse):
                        result = call_response.result
                        if isinstance(result, TaskArtifactUpdateEvent):
                            metadata = result.metadata
                            call_id = result.id
                            if metadata:
                                # 要求：
                                # 1. 及时把 streaming response 返回给前端
                                # 2. 记录执行结果到上下文，按照 call_id 区分
                                metadata["msg_key"] = msg_key
                                metadata["current_step"] = current_step
                                if call_id_for_code_interpreter and call_id == call_id_for_code_interpreter:
                                    metadata["key"] = f"{msg_key}_code_result_msg_{current_step}"
                                else:
                                    metadata["key"] = f"{msg_key}_tool_result_msg_{current_step}"

                                message_content_delta = metadata.pop("message_content", [])
                                block_list_delta = metadata.pop("block_list", [])
                                tool_result = ToolResult(
                                    message_content=message_content_delta,
                                    block_list=block_list_delta,
                                )
                                new_tool_result = reference_manager.process_tool_result(tool_result)
                                call_id_to_result[call_id].extend_result(new_tool_result)
                                if self.debug:
                                    logger.debug(f"Tool call {call_id} result: {json.dumps(new_tool_result.model_dump(), ensure_ascii=False, indent=2)}")
                                # metadata["message_content"] = new_tool_result.message_content  # 前端不需要 message_content
                                metadata["block_list"] = new_tool_result.block_list  # 前端需要 block_list, 这里的 block_list 已经附带真正的 reference number 了

                                yield SendTaskStreamingResponse(
                                    id=request_id,
                                    result=TaskArtifactUpdateEvent(
                                        id=task_id,
                                        metadata=metadata,
                                    ),
                                )
                        elif isinstance(result, TaskStatusUpdateEvent):
                            pass

                # 5. 记录工具调用结果到上下文
                if not call_id_to_result:
                    # 没有工具调用结果，可能是 CodeInterpreter 没有返回结果
                    logger.debug(f"No tool call results for session {session_id}, current step {current_step}.")
                for call_id, result in call_id_to_result.items():
                    logger.debug(f"Tool call {call_id} result: {json.dumps(result.model_dump(), ensure_ascii=False, indent=2)}")
                    message_content = result.message_content
                    if call_id_for_code_interpreter and call_id == call_id_for_code_interpreter:
                        if not message_content:
                            message_content = [{"type": "text", "text": "ok"}]
                        is_all_text = all([msg["type"] == "text" for msg in message_content])
                        if is_all_text:
                            thought_messages.append({"role": "tool", "content": message_content, "tool_call_id": call_id})
                        else:
                            thought_messages.append({"role": "tool", "content": [{"type": "text", "text": "The execution results of CodeInterpreter will be provided by the user as following:"}], "tool_call_id": call_id})
                            message_content.append({"type": "text", "text": "The execution results of CodeInterpreter are provided as above."})
                            thought_messages.append({"role": "user", "content": message_content})
                    else:
                        thought_messages.append({"role": "tool", "content": message_content, "tool_call_id": call_id})
            else:
                # 没有调工具就是回答了
                response_content = [{"type": "text", "text": remove_thoughts(response)}]

                yield SendTaskStreamingResponse(
                    id=request_id,
                    result=TaskArtifactUpdateEvent(
                        id=task_id,
                        metadata={
                            "block_list": response_content,
                            "msg_key": msg_key,
                            "key": f"{msg_key}_assistant_answer_{current_step}",
                        },
                    ),
                )

                history_messages.append({"role": "assistant", "content": response_content})
                break
        resp = await self.complete_streaming_response(request_id=request_id, task_id=task_id)
        yield resp

    async def streaming_chat(
        self,
        user_message_content: list[ContentData],
        host_frontend_id: str,
        trace_id: str = uuid.uuid4().hex,
        session_id: str = uuid.uuid4().hex,
        task_id: str = uuid.uuid4().hex,
        user_id: str = uuid.uuid4().hex,
        host_agent_config: Optional[AgentConfig] = None,
        additional_allowed_tools: Optional[list[str]] = None,
        additional_tools: Optional[list[ToolCallSchema]] = None,
        instruction: Optional[str] = None,
        inference_args: Optional[dict[str, Any]] = None,
        cwd: Optional[str] = None,
    ):
        """
        向 SessionTaskManager 发送一个任务请求，开始一个会话。
        Args:
            user_message_content: 用户消息内容
            host_frontend_id: 前端 ID, 可选 AInvest, iWencai 等
            trace_id: 跟踪 ID
            session_id: 会话 ID
            task_id: 任务 ID
            user_id: 用户 ID
            host_agent_config: 主机代理配置
            additional_allowed_tools: 额外允许的工具列表
            additional_tools: 额外的工具列表
            instruction: 用户指令
        Returns:
            AsyncIterable[SendTaskStreamingResponse | JSONRPCResponse]: 任务流响应
        """
        req = SessionRequest(
            trace_id=trace_id,
            user_id=user_id if user_id else "default_user",
            host_frontend_id=host_frontend_id,
            user_message_content=user_message_content,
            agent_config=host_agent_config,
            additional_tools=additional_tools,
            additional_allowed_tools=additional_allowed_tools,
            instruction=instruction,
            inference_args=inference_args,
            cwd=cwd,
        )
        request = SendTaskStreamingRequest(
            params=TaskSendParams(
                id=task_id if task_id else uuid.uuid4().hex,
                sessionId=session_id,
                payload=req.model_dump(),
            )
        )
        return await self.on_send_task_subscribe(request)

    async def on_send_task_subscribe(self, request: SendTaskStreamingRequest) -> AsyncIterable[SendTaskStreamingResponse]:
        await self.upsert_task(request.params)
        request_id = request.id
        task_send_params: TaskSendParams = request.params
        task_id = task_send_params.id
        session_id = task_send_params.sessionId
        payload = task_send_params.payload
        req = SessionRequest.model_validate(payload)

        return self._stream_generator(request_id, task_id, session_id, req)

    async def on_send_task(self, request):
        return await super().on_send_task(request)

    async def on_get_task(self, request):
        return await super().on_get_task(request)

    async def on_cancel_task(self, request):
        return await super().on_cancel_task(request)

    async def on_get_task_push_notification(self, request):
        return await super().on_get_task_push_notification(request)

    async def on_resubscribe_to_task(self, request):
        return await super().on_resubscribe_to_task(request)

    async def on_set_task_push_notification(self, request):
        return await super().on_set_task_push_notification(request)
