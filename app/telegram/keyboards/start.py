from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.telegram.dto import Callback, CallbackActions


def main_menu_keyboard(utm_source: str | None = None) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    url = "https://cryptorockets.net/"
    if utm_source:
        url += f"?utm_source={utm_source}"

    builder.row(
        InlineKeyboardButton(
            text="Привет!",
            web_app=WebAppInfo(url=url),
        )
    )

    return builder.as_markup()
