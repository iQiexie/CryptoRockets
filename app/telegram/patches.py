import asyncio
import datetime
import json
import os
import secrets
from contextlib import asynccontextmanager
from enum import Enum
from typing import Any, Dict, Union

import structlog
from aiogram import Bot as _Bot
from aiogram.client.default import Default
from aiogram.exceptions import (
    TelegramBadRequest,
    TelegramForbiddenError,
    TelegramRetryAfter,
)
from aiogram.types import InputFile, Message, TelegramObject
from fastapi import FastAPI

from app.config.config import TelegramBotConfig
from app.db.models import User
from app.telegram.keyboards.start import main_menu_keyboard
from i18n.service import I18n

logger = structlog.stdlib.get_logger()


class Bot(_Bot):
    def __init__(self, config: TelegramBotConfig, i18n: I18n, *args, **kwargs) -> None:
        self.config = config
        super().__init__(*args, **kwargs)
        self.i18n = i18n

    async def send_message(self, *args, **kwargs) -> Message | None:
        try:
            return await super().send_message(*args, **kwargs)
        except TelegramForbiddenError:
            return

    async def edit_message_text(self, *args, **kwargs) -> Union[Message, bool]:
        try:
            return await super().edit_message_text(*args, **kwargs)
        except TelegramBadRequest as e:
            if "exactly the same" in e.message:
                return False

            raise e

    async def _setup_webhook(self) -> None:
        try:
            logger.info(f"Setting webhook for bot {self.id=}; {self.config.TELEGRAM_BOT_WEBHOOK_HOST=}")
            random = os.urandom(5).hex()
            await self.set_webhook(
                max_connections=100,
                url=f"{self.config.TELEGRAM_BOT_WEBHOOK_HOST}/api/v1/telegram?r={random}",
                secret_token=self.config.TELEGRAM_BOT_WEBHOOK_SECRET,
            )
        except TelegramRetryAfter as e:
            logger.info(f"Retrying webhook after {e.retry_after} for bot {self.id=}, {e=}")
            await asyncio.sleep(e.retry_after)
            await self._setup_webhook()

    @asynccontextmanager
    async def setup(self, app: FastAPI) -> None:  # noqa
        await self._setup_webhook()
        yield

    async def send_menu(
        self,
        user: User,
        utm_source: str | None = None,
        custom_text: str | None = None,
    ) -> None:
        await self.send_message(
            chat_id=user.telegram_id,
            text=custom_text or "Привет!",
            reply_markup=main_menu_keyboard(utm_source=utm_source),
        )


def prepare_value(
    value: Any,
    bot: Bot,
    files: Dict[str, Any],
    _dumps_json: bool = True,
) -> Any:
    """
    from aiogram.client.session.aiohttp.BaseSession
    """

    if value is None:
        return None
    if isinstance(value, str):
        return value
    if isinstance(value, Default):
        default_value = bot.default[value.name]
        return prepare_value(default_value, bot=bot, files=files, _dumps_json=_dumps_json)
    if isinstance(value, InputFile):
        key = secrets.token_urlsafe(10)
        files[key] = value
        return f"attach://{key}"
    if isinstance(value, dict):
        value = {
            key: prepared_item
            for key, item in value.items()
            if (prepared_item := prepare_value(item, bot=bot, files=files, _dumps_json=False)) is not None
        }
        if _dumps_json:
            return json.dumps(value)
        return value
    if isinstance(value, list):
        value = [
            prepared_item
            for item in value
            if (prepared_item := prepare_value(item, bot=bot, files=files, _dumps_json=False)) is not None
        ]
        if _dumps_json:
            return json.dumps(value)
        return value
    if isinstance(value, datetime.timedelta):
        now = datetime.datetime.utcnow()
        return str(round((now + value).timestamp()))
    if isinstance(value, datetime.datetime):
        return str(round(value.timestamp()))
    if isinstance(value, Enum):
        return prepare_value(value.value, bot=bot, files=files)
    if isinstance(value, TelegramObject):
        return prepare_value(
            value.model_dump(warnings=False),
            bot=bot,
            files=files,
            _dumps_json=_dumps_json,
        )

    if _dumps_json:
        return json.dumps(value)

    return value
