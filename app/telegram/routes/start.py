from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.services.base.services import Services
from app.services.dto.auth import WebappData
from app.telegram.dto import Callback, CallbackActions
from app.telegram.patches import Bot
from app.utils import safe_answer

router = Router()


@router.message(CommandStart())
@router.callback_query(Callback.filter(F.action.in_({CallbackActions.menu})))
async def command_start(message: Message | CallbackQuery, services: Services, state: FSMContext, bot: Bot) -> None:
    if isinstance(message, CallbackQuery):
        await safe_answer(message)

    try:
        payload = message.text.split("/start")[1].strip()
    except Exception:  # noqa
        payload = ""

    user = await services.user.get_or_create_user(
        data=WebappData(
            telegram_id=message.from_user.id,
            start_param=payload,
            **message.from_user.model_dump(),
        )
    )

    await bot.send_menu(user=user)
    await state.clear()
