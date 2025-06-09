import json
import random
import string
import traceback
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any, Callable

import structlog
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, Message

if TYPE_CHECKING:
    from app.telegram.patches import Bot

logger = structlog.stdlib.get_logger()


class SafeList(list):
    def get(self, index: int, default: Any = None) -> Any:
        try:
            return self[index]
        except IndexError:
            return default


def struct_log(event: str, special_logger: Callable = None, **kwargs) -> None:
    payload = dict(event=event, payload=kwargs)

    try:
        log = json.dumps(payload)
    except TypeError:
        log = payload

    if special_logger:
        special_logger(log)
    else:
        logger.info(log)


@contextmanager
def suppress() -> None:
    try:
        yield
    except Exception as e:
        logger.error("Error has occurred", exception=traceback.format_exception(e))


def chunk_list(lst: list, size: int) -> list[list]:
    return [lst[i : i + size] for i in range(0, len(lst), size)]


async def safe_delete(message: Message | CallbackQuery | int, bot: "Bot" = None) -> None:
    try:
        if isinstance(message, Message):
            await message.delete()

        if isinstance(message, CallbackQuery):
            await message.message.delete()

        if isinstance(message, int):
            await bot.delete_message(chat_id=message, message_id=message)

    except TelegramBadRequest:
        pass


async def safe_answer(message: Message | CallbackQuery | int) -> None:
    try:
        await message.answer()
    except TelegramBadRequest:
        pass


def generate_random_string(seed: int, length: int = 10) -> str:
    random.seed(seed)
    characters = string.ascii_letters + string.digits
    return "".join(random.choices(characters, k=length))  # noqa: S311


def iota_generator() -> Callable[[], int]:
    counter = -1

    def next_label() -> int:
        nonlocal counter
        counter += 1
        return counter

    return next_label
