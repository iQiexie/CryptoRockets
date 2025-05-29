from aiogram import F, Router
from aiogram.methods import TelegramMethod
from aiogram.types import Message, PreCheckoutQuery

from app.db.models import CurrenciesEnum
from app.services.base.services import Services
from app.services.dto.shop import XTRPaymentCallbackDTO

router = Router()


@router.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery) -> TelegramMethod:
    return pre_checkout_query.answer(ok=True)


@router.message(F.successful_payment)
async def success_payment_handler(message: Message, services: Services) -> None:
    return await services.shop.handle_payment_callback(
        data=XTRPaymentCallbackDTO(
            telegram_id=message.from_user.id,
            item_id=int(message.successful_payment.invoice_payload),
            amount=message.successful_payment.total_amount,
            usd_amount=message.successful_payment.total_amount * 0.013,
            currency=CurrenciesEnum.xtr,
            external_id=message.successful_payment.provider_payment_charge_id,
            callback_data=message.successful_payment,
        )
    )
