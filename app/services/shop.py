import asyncio
import base64
import traceback
from typing import Annotated

import structlog
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from fastapi.params import Depends
from pydantic_core import to_json
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from tonsdk.boc import Cell

from app.adapters.base import Adapters
from app.api.dependencies.stubs import (
    dependency_adapters,
    dependency_session_factory,
    placeholder,
)
from app.api.dto.game.response import GiftUserWithdrawResponse
from app.api.dto.shop.request import SHOP_ITEMS, ShopItem
from app.api.dto.shop.response import UrlResponse
from app.api.dto.user.response import UserResponse
from app.api.exceptions import ClientError
from app.db.models import (
    CurrenciesEnum,
    RocketTypeEnum,
    TransactionStatusEnum,
    TransactionTypeEnum,
    WheelPrizeEnum,
)
from app.db.models import GiftUserStatusEnum
from app.services.base.base import BaseService
from app.services.dto.auth import WebappData
from app.services.dto.shop import PaymentCallbackDTO
from app.services.dto.websocket import WsEventsEnum, WSMessage
from app.telegram.dto import Callback
from app.telegram.dto import CallbackActions
from app.utils import struct_log

logger = structlog.stdlib.get_logger()


class ShopService(BaseService):
    def __init__(
        self,
        adapters: Annotated[Adapters, Depends(dependency_adapters)],
        session_factory: Annotated[sessionmaker, Depends(dependency_session_factory)],
        session: Annotated[AsyncSession, Depends(placeholder)] = None,
    ):
        super().__init__(session_factory=session_factory, adapters=adapters, session=session)

        self.repo = self.repos.shop
        self.adapters = adapters

    @BaseService.single_transaction
    async def _handle_payment_callback(self, data: PaymentCallbackDTO) -> None:
        item = SHOP_ITEMS[data.item_id]

        transaction_id = None
        rocket_id = None
        item_price = getattr(item, f"{data.currency.value}_price", None)

        if data.amount < (item_price * data.item_amount):
            struct_log(
                event="Payment amount mismatch",
                item_id=item.id,
                expected_amount=item_price,
                received_amount=data.amount,
            )

            raise ClientError(message="Payment amount mismatch")

        if item.item in (WheelPrizeEnum.token, WheelPrizeEnum.usdt, WheelPrizeEnum.ton, WheelPrizeEnum.wheel):
            _resp = await self.services.transaction.change_user_balance(
                telegram_id=data.telegram_id,
                currency=CurrenciesEnum[item.item.value],
                amount=item.amount,
                tx_type=TransactionTypeEnum.purchase,
            )

            transaction_id = _resp.transaction.id
        elif item.item in (WheelPrizeEnum.super_rocket, WheelPrizeEnum.mega_rocket, WheelPrizeEnum.ultra_rocket):
            _rocket = await self.repos.user.create_user_rocket(
                user_id=data.telegram_id,
                type=RocketTypeEnum[item.item.value.replace("_rocket", "")],
                fuel_capacity=1,
                current_fuel=1,
            )
            rocket_id = _rocket.id
        elif item.item == WheelPrizeEnum.rolls:
            user = await self.repos.user.get_user_for_update(telegram_id=data.telegram_id)
            new_rolls = user.rolls_dict
            new_rolls[item.ton_price] = (new_rolls.get(item.ton_price, 0) + item.amount) * data.item_amount
            await self.repos.user.update_user(telegram_id=data.telegram_id, rolls=new_rolls)
        elif item.item == WheelPrizeEnum.gift_withdrawal:
            gift = await self.repos.game.get_gift_for_update(gift_user_id=data.gift_id)
            await self.repos.game.update_gift_user(gift_user_id=gift.id, status=GiftUserStatusEnum.paid)
            await self.services.websocket.publish(WSMessage(
                telegram_id=gift.user_id,
                event=WsEventsEnum.gift_withdrawal,
                message=GiftUserWithdrawResponse.model_validate(gift).model_dump(by_alias=True),
            ))

            await self.adapters.bot.send_message(
                chat_id=-1002726537985,
                text=f"Юзер {gift.user_id} выводит подарок: {gift.gift_id}",
                reply_markup=(
                    InlineKeyboardBuilder()
                    .row(
                        InlineKeyboardButton(
                            text="Подарок выведен",
                            callback_data=Callback(action=CallbackActions.gift_withdrawn, data=str(gift.id)).pack(),
                        )
                    )
                    .row(
                        InlineKeyboardButton(
                            text="Какой подарок?",
                            callback_data=Callback(action=CallbackActions.gift_view, data=str(gift.id)).pack(),
                        )
                    )
                    .as_markup()
                )
            )

        else:
            raise NotImplementedError(f"Item type {item.model_dump()} is not implemented")
        await self.repo.create_invoice(
            user_id=data.telegram_id,
            external_id=data.external_id,
            status=TransactionStatusEnum.success,
            currency=data.currency,
            currency_amount=data.amount,
            currency_fee=data.fee,
            usd_amount=data.usd_amount,
            transaction_id=transaction_id,
            rocket_id=rocket_id,
            callback_data=data.callback_data,
        )

        try:
            await self.session.flush()
        except IntegrityError as e:
            logger.error(event=f"This invoice already exists: {e=}", exception=traceback.format_exception(e))
            return
        except Exception as e:
            logger.error(event=f"Error while handling callbacl: {e}", exception=traceback.format_exception(e))
            raise ClientError(message="Failed to process payment callback") from e

    async def handle_payment_callback(self, data: PaymentCallbackDTO) -> None:
        await self._handle_payment_callback(data=data)
        async with self.repo.transaction():
            user = await self.repos.user.get_user_by_telegram_id(telegram_id=data.telegram_id)

        asyncio.create_task(
            self.adapters.alerts.send_alert(
                message=(
                    f"Покупочка!!\n\n"
                    f"Пользователь: {data.telegram_id}\n"
                    f"Сумма: {data.usd_amount} USD\n"
                    f"Сумма: {data.amount} {data.currency.upper()}\n"
                ),
                chat_id=-1002726537985,
            )
        )

        await self.services.websocket.publish(
            message=WSMessage(
                event=WsEventsEnum.roll_purchase,
                telegram_id=user.telegram_id,
                message=dict(user=UserResponse.model_validate(user).model_dump(by_alias=True)),
            )
        )

    async def get_invoice_url(
        self,
        shop_item_id: int,
        current_user: WebappData,
        payment_method: str,
        amount: int,
        gift_id: int | None = None,
    ) -> UrlResponse:
        item = SHOP_ITEMS[shop_item_id]
        if item.item == WheelPrizeEnum.gift_withdrawal and not gift_id:
            raise ClientError(message="Gift ID is required for gift withdrawal")

        if payment_method == "xtr":
            item_label = self.adapters.i18n.t(message=item.label, lang=current_user.language_code)

            if item.item == WheelPrizeEnum.gift_withdrawal:
                payload = f"{item.id};{gift_id}"
            else:
                payload = str(item.id)

            params = {
                "currency": "XTR",
                "description": item_label,
                "payload": payload,
                "prices": to_json([{"label": item_label, "amount": int(item.xtr_price) * amount}]).decode("utf-8"),
                "title": item_label,
            }

            resp = await self.adapters.telegram.send_method(method="createInvoiceLink", params=params)
            return UrlResponse(url=resp["result"])
        elif payment_method == "ton":
            cell = Cell()
            cell.bits.write_uint(0, 32)  # op_code for text comment

            if item.item == WheelPrizeEnum.gift_withdrawal:
                payload = f"{current_user.telegram_id};{item.id};{gift_id}"
            else:
                payload = f"{current_user.telegram_id};{item.id};{amount}"

            logger.info(f"Got {payload=}")

            cell.bits.write_bytes(payload.encode("utf-8"))
            return UrlResponse(
                url=base64.b64encode(cell.to_boc()).decode(),
                amount=item.ton_price * amount,
            )

        raise NotImplementedError
