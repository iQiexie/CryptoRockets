from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.telegram.dto import Callback, CallbackActions


def main_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text="Привет!",
            callback_data=Callback(action=CallbackActions.menu).pack(),
        )
    )

    return builder.as_markup()
