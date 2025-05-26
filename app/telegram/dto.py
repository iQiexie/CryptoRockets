from enum import Enum

from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.state import State, StatesGroup


class States(StatesGroup):
    example = State()


class CallbackActions(str, Enum):
    menu = "a"  # todo iota


class Callback(CallbackData, prefix="t"):
    action: CallbackActions
    data: str | None = None
