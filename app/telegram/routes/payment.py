from aiogram import F, Router
from aiogram.methods import TelegramMethod
from aiogram.types import CallbackQuery
from aiogram.types import Message, PreCheckoutQuery

from app.db.models import CurrenciesEnum
from app.services.base.services import Services
from app.services.dto.shop import PaymentCallbackDTO
from app.telegram.dto import Callback
from app.telegram.dto import CallbackActions

router = Router()


@router.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery) -> TelegramMethod:
    return pre_checkout_query.answer(ok=True)


@router.message(F.successful_payment)
async def success_payment_handler(message: Message, services: Services) -> None:
    return await services.shop.handle_payment_callback(
        data=PaymentCallbackDTO(
            telegram_id=message.from_user.id,
            item_id=int(message.successful_payment.invoice_payload),
            amount=message.successful_payment.total_amount,
            usd_amount=message.successful_payment.total_amount * 0.013,
            currency=CurrenciesEnum.xtr,
            external_id=message.successful_payment.provider_payment_charge_id,
            callback_data=message.successful_payment.model_dump(),
        )
    )


@router.callback_query(Callback.filter(F.action.in_({CallbackActions.gift_view})))
async def gift_view(callback: CallbackQuery, services: Services, callback_data: Callback) -> None:
    return await services.bot.gift_view(callback=callback, gift_id=int(callback_data.data))
