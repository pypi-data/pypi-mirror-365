from typing_extensions import Any, AsyncGenerator, Union, AsyncIterable
import asyncio

import openai
from agentlin.core.types import *
from agentlin.core.agent_schema import AgentCore
from agentlin.route.task_manager import InMemoryTaskManager


class ModelTaskManager(InMemoryTaskManager):
    def __init__(
        self,
        agent: AgentCore,
    ):
        super().__init__()
        self.agent = agent
        self.client = openai.AsyncOpenAI()

    async def on_send_task_subscribe(self, request: SendTaskStreamingRequest) -> AsyncIterable[SendTaskStreamingResponse]:
        await self.upsert_task(request.params)
        return self._stream_generator(request)

    async def _stream_generator(self, request: SendTaskStreamingRequest) -> AsyncIterable[SendTaskStreamingResponse]:
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
            yield SendTaskStreamingResponse(
                id=request.id,
                result=TaskStatusUpdateEvent(
                    id=task_send_params.id,
                    status=TaskStatus(state=TaskState.WORKING),
                ),
            )

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

            # 更新任务状态为完成
            task = await self.update_store(
                task_send_params.id,
                TaskStatus(state=TaskState.COMPLETED),
            )

            # 发送最终完成响应
            yield SendTaskStreamingResponse(
                id=request.id,
                result=TaskStatusUpdateEvent(
                    id=task_send_params.id,
                    final=True,
                    status=TaskStatus(state=TaskState.COMPLETED),
                ),
            )

        except Exception as e:
            # 处理错误情况
            error_message = f"处理请求时发生错误: {str(e)}"

            # 更新任务状态为失败
            await self.update_store(
                task_send_params.id,
                TaskStatus(state=TaskState.FAILED),
                {"error": error_message},
            )

            # 发送错误响应
            yield JSONRPCResponse(id=request.id, error=JSONRPCError(code=-32000, message=error_message))

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
