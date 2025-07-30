from typing_extensions import Any, AsyncIterable
import json

import httpx
from httpx_sse import connect_sse
from fastmcp.client.elicitation import ElicitRequestParams, ElicitResult, RequestContext, ClientSession, LifespanContextT

from agentlin.core.types import *
from agentlin.route.agent_message_queue import AgentMessageQueue


class Client(AgentMessageQueue):
    def __init__(
        self,
        agent_id: str,
        url: str,
        *,
        rabbitmq_host: str = "localhost",
        rabbitmq_port: int = 5672,
        auto_ack: bool = False,
        reconnect_initial_delay: float = 5.0,
        reconnect_max_delay: float = 60.0,
        message_timeout: float = 30.0,
        rpc_timeout: float = 30.0,
    ):
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
        self.url = url

    async def on_elicitation(
        self,
        message: str,
        response_type: type,
        params: ElicitRequestParams,
        context: RequestContext[ClientSession, LifespanContextT],
    ):
        # Present the message to the user and collect input
        # user_input = input(f"{message}: ")
        print(f"{message}")
        print("===Params===")
        print(params)
        print("===Context===")
        print(context)
        data = {
            "params": params.model_dump(),
        }
        # display_event(Event(type="elicitation", data=data))

        return ElicitResult(action="accept")

    async def send_task_streaming(self, payload: dict[str, Any]) -> AsyncIterable[SendTaskStreamingResponse]:
        request = SendTaskStreamingRequest(params=payload)
        with httpx.Client(timeout=None) as client:
            with connect_sse(client, "POST", self.url, json=request.model_dump()) as event_source:
                for sse in event_source.iter_sse():
                    yield SendTaskStreamingResponse(**json.loads(sse.data))

    async def _send_request(self, request: JSONRPCRequest) -> dict[str, Any]:
        async with httpx.AsyncClient() as client:
            # Image generation could take time, adding timeout
            print(f" -----> {self.url}")
            response = await client.post(self.url, json=request.model_dump(), timeout=60)
            response.raise_for_status()
            return response.json()

    async def send_task(self, payload: dict[str, Any]) -> SendTaskResponse:
        payload = TaskSendParams(**payload)
        request = SendTaskRequest(params=payload)
        return SendTaskResponse(**await self._send_request(request))

    async def get_task(self, payload: dict[str, Any]) -> GetTaskResponse:
        request = GetTaskRequest(params=payload)
        return GetTaskResponse(**await self._send_request(request))

    async def cancel_task(self, payload: dict[str, Any]) -> CancelTaskResponse:
        request = CancelTaskRequest(params=payload)
        return CancelTaskResponse(**await self._send_request(request))

    async def set_task_callback(self, payload: dict[str, Any]) -> SetTaskPushNotificationResponse:
        request = SetTaskPushNotificationRequest(params=payload)
        return SetTaskPushNotificationResponse(**await self._send_request(request))

    async def get_task_callback(self, payload: dict[str, Any]) -> GetTaskPushNotificationResponse:
        request = GetTaskPushNotificationRequest(params=payload)
        return GetTaskPushNotificationResponse(**await self._send_request(request))
