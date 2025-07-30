import json
from typing import AsyncIterable
from typing_extensions import Any, AsyncGenerator
import uuid

from fastmcp import Client
from fastmcp.client.transports import ClientTransportT

from loguru import logger

from agentlin.route.task_manager import InMemoryTaskManager
from agentlin.core.types import *


class CallToolRequest(BaseModel):
    call_name: str
    call_args: dict[str, Any]


class ToolTaskManager(InMemoryTaskManager):
    def __init__(self, config: ClientTransportT, callback_url: str):
        super().__init__()
        self.callback_url = callback_url
        self.client = Client(
            config,
            # elicitation_handler=self.elicitation_handler,
        )

    def set_client(self, client: Client):
        self.client = client

    async def get_tools(self, allowed_tools: Optional[list[str]] = None) -> list[dict[str, Any]]:
        async with self.client:
            tools = await self.client.list_tools()
            results = []
            for tool in tools:
                if allowed_tools is None:
                    results.append(tool.model_dump())
                    continue
                # 如果指定了 allowed_tools，则只返回这些工具
                tool_name = tool.name
                if tool_name in allowed_tools:
                    results.append(tool.model_dump())
        return results

    async def on_send_task_subscribe(self, request: SendTaskStreamingRequest) -> AsyncIterable[SendTaskStreamingResponse]:
        await self.upsert_task(request.params)
        task_send_params: TaskSendParams = request.params
        session_id = task_send_params.sessionId
        payload = task_send_params.payload
        call_name: str = payload.get("call_name", "unknown_function")
        call_args: dict[str, Any] = payload.get("call_args", {})
        return self._stream_generator(request.id, task_send_params.id, call_name, call_args)

    async def _stream_generator(
        self,
        request_id: str,
        task_id: str,
        call_name: str,
        call_args: dict[str, Any],
    ) -> AsyncIterable[SendTaskStreamingResponse]:
        resp = await self.working_streaming_response(request_id=request_id, task_id=task_id)
        yield resp

        try:
            async with self.client:
                result = await self.client.call_tool(
                    name=call_name,
                    arguments=call_args,
                )
            logger.debug(f"Tool call {call_name} result: {result}")
            logger.debug(f"Tool call {call_name} result: {result.content}")
            logger.debug(f"Tool call {call_name} result: {result.structured_content}")
            content = result.content
            structured_content = result.structured_content
            data = structured_content
            block_list = structured_content.pop("block_list", [])
            if not block_list:
                block_list = [i.model_dump() for i in content]

            yield SendTaskStreamingResponse(
                id=request_id,
                result=TaskArtifactUpdateEvent(
                    id=task_id,
                    metadata={
                        "message_content": [i.model_dump() for i in content],
                        "block_list": block_list,
                        "data": data,
                    },
                ),
            )

        except Exception as exc:
            logger.error(f"Error in tool task: {exc}")
            error = JSONRPCError(code=-32000, message=str(exc))
            resp = await self.fail_streaming_response(request_id=request_id, task_id=task_id, error=error)
            yield resp
        finally:
            resp = await self.complete_streaming_response(request_id=request_id, task_id=task_id)
            yield resp

    async def on_send_task(self, request: SendTaskRequest) -> SendTaskResponse:
        await self.upsert_task(request.params)
        return await self._invoke(request)

    async def _invoke(self, request: SendTaskRequest) -> SendTaskResponse:
        task_send_params: TaskSendParams = request.params
        session_id = task_send_params.sessionId
        payload = task_send_params.payload
        call_id: str = payload.get("call_id", f"call_{uuid.uuid4().hex}")
        call_name: str = payload.get("call_name", "unknown_function")
        call_args: dict[str, Any] = payload.get("call_args", {})

        try:
            result = await self.client.call_tool(
                name=call_name,
                arguments=call_args,
            )

            task = await self.update_store(
                task_send_params.id,
                TaskStatus(state=TaskState.COMPLETED),
                result,
            )
            return SendTaskResponse(id=request.id, result=task)
        except Exception as exc:
            logger.error(f"Error in tool task: {exc}")
            return SendTaskResponse(id=request.id, error=JSONRPCError(code=-32000, message=str(exc)))
