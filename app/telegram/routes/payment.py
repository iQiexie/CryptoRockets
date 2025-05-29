from aiogram import F
from aiogram import Router
from aiogram.methods import TelegramMethod
from aiogram.types import Message
from aiogram.types import PreCheckoutQuery
from app.services.base.services import Services

router = Router()


@router.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery) -> TelegramMethod:
    return pre_checkout_query.answer(ok=True)


@router.message(F.successful_payment)
async def success_payment_handler(message: Message, services: Services) -> None:
    return await services.shop.handle_payment_callback(
        telegram_id=message.from_user.id,
        item_id=int(message.successful_payment.invoice_payload),
        data=message.successful_payment,
    )
