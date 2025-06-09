import base64
from typing import Annotated

import structlog
from fastapi.params import Depends
from pydantic_core import to_json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from tonsdk.boc import Cell

from app.adapters.base import Adapters
from app.api.dependencies.stubs import (
    dependency_adapters,
    dependency_session_factory,
    placeholder,
)
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
from app.db.models import User
from app.services.base.base import BaseService
from app.services.dto.auth import WebappData
from app.services.dto.shop import PaymentCallbackDTO
from app.services.dto.websocket import WSMessage
from app.services.dto.websocket import WsEventsEnum
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
    async def _handle_payment_callback(self, data: PaymentCallbackDTO) -> User:
        item = SHOP_ITEMS[data.item_id]

        transaction_id = None
        rocket_id = None
        user = None
        item_price = getattr(item, f"{data.currency.value}_price", None)

        if item_price < data.amount:
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
            user = _resp.user
        elif item.item in (WheelPrizeEnum.super_rocket, WheelPrizeEnum.mega_rocket, WheelPrizeEnum.ultra_rocket):
            _rocket = await self.repos.user.create_user_rocket(
                user_id=data.telegram_id,
                type=RocketTypeEnum[item.item.value.replace("_rocket", "")],
                fuel_capacity=1,
                current_fuel=1,
            )
            rocket_id = _rocket.id
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

        if not user:
            await self.session.flush()
            user = await self.repos.user.get_user_by_telegram_id(telegram_id=data.telegram_id)

        return user

    async def handle_payment_callback(self, data: PaymentCallbackDTO) -> None:
        user = await self._handle_payment_callback(data=data)
        await self.services.websocket.publish(
            message=WSMessage(
                event=WsEventsEnum.purchase,
                telegram_id=data.telegram_id,
                message=dict(user=UserResponse.model_validate(user).model_dump(by_alias=True))
            )
        )

    async def _get_invoice_url_xtr(self, item: ShopItem, current_user: WebappData) -> UrlResponse:
        item_label = self.adapters.i18n.t(message=item.label, lang=current_user.language_code)

        params = {
            "currency": "XTR",
            "description": item_label,
            "payload": f"{item.id}",
            "prices": to_json([{"label": item_label, "amount": int(item.xtr_price)}]).decode("utf-8"),
            "title": item_label,
        }

        resp = await self.adapters.telegram.send_method(method="createInvoiceLink", params=params)
        return UrlResponse(url=resp["result"])

    async def get_invoice_url(
        self,
        shop_item_id: int,
        current_user: WebappData,
        payment_method: str,
    ) -> UrlResponse:
        item = SHOP_ITEMS[shop_item_id]
        if payment_method == "xtr":
            return await self._get_invoice_url_xtr(item=item, current_user=current_user)
        if payment_method == "ton":
            cell = Cell()
            cell.bits.write_uint(0, 32)  # op_code for text comment
            cell.bits.write_bytes(f"{current_user.telegram_id}:{shop_item_id}".encode('utf-8'))
            return UrlResponse(url=base64.b64encode(cell.to_boc()).decode())

        raise NotImplementedError
