from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.telegram.dto import Callback, CallbackActions


def main_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text="Привет!",
            web_app=WebAppInfo(url="https://cryptorockets.net/"),
        )
    )

    return builder.as_markup()
