import asyncio

import structlog
from pydantic_core import from_json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from starlette.websockets import WebSocket, WebSocketState

from app.adapters.base import Adapters
from app.services.base.base import BaseService
from app.services.dto.websocket import WsEventsEnum, WSMessage

REDIS_CHANNEL = "websockets"

logger = structlog.stdlib.get_logger()


class WebsocketService(BaseService):
    def __init__(self, adapters: Adapters, session_factory: sessionmaker, session: AsyncSession = None):
        super().__init__(session_factory=session_factory, adapters=adapters, session=session)

        self.repo = self.repos.user
        self.adapters = adapters
        self.session_factory = session_factory

        self._clients: dict[str, dict[int, WebSocket]] = {topic: {} for topic in WsEventsEnum}

    async def consume(self) -> None:
        coroutine = self._consume_channel()
        asyncio.create_task(coroutine)

    def _find_websocket(self, event: WsEventsEnum, telegram_id: int) -> WebSocket | None:
        try:
            return self._clients[event][telegram_id]
        except KeyError:
            logger.debug(f"Websocket {telegram_id} ({event}) not found. {self._clients=}")
            return

    async def _add_consumer(self, event: WsEventsEnum, telegram_id: int, websocket: WebSocket) -> None:
        self._clients[event][telegram_id] = websocket

    async def _delete_consumer(self, event: WsEventsEnum, telegram_id: int) -> None:
        try:
            websocket = self._clients[event][telegram_id]
        except KeyError:
            return

        try:
            await websocket.close(code=1000, reason="Failed")
        except Exception:  # noqa
            pass

        try:
            del self._clients[event][telegram_id]
        except KeyError:
            return

    async def _consume_channel(self) -> None:
        channel = self.adapters.redis.redis.pubsub(ignore_subscribe_messages=True)
        await channel.subscribe(REDIS_CHANNEL)
        logger.info("Websocket channel subscribed")

        async for msg in channel.listen():
            data = from_json(msg.get("data"))
            logger.info(f"Got {data=}")
            message = WSMessage(**data)

            websocket = self._find_websocket(event=message.event, telegram_id=message.telegram_id)

            if not websocket:
                websocket = self._find_websocket(
                    event=WsEventsEnum.user_notification,
                    telegram_id=message.telegram_id,
                )

            if not websocket:
                logger.info(f"Websocket not found for {data=}. {self._clients=}")
                continue

            logger.info(f"Websocket channel received: {data}")

            if websocket.state == WebSocketState.DISCONNECTED:
                await self._delete_consumer(telegram_id=message.telegram_id, event=message.event)
                return

            data = message.model_dump_json()
            logger.info(f"Sending to websocket: {data}")
            await websocket.send_text(data=data)

    async def subscribe(self, websocket: WebSocket, telegram_id: int) -> None:
        event = WsEventsEnum.user_notification
        await self._add_consumer(event=event, telegram_id=telegram_id, websocket=websocket)

        try:
            while True:
                await websocket.receive()
        except Exception as e:
            logger.info(f"Failed to socket: {type(e)=}; {e=}. {telegram_id=}")
            await self._delete_consumer(telegram_id=telegram_id, event=event)

    @BaseService.log_exception
    async def publish(self, message: WSMessage) -> None:
        data = message.model_dump_json()

        async with self.adapters.redis.redis.client():
            logger.info(f"Sending to websocket: {data}")
            await self.adapters.redis.redis.publish(channel=REDIS_CHANNEL, message=data)
