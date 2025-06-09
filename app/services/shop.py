from typing import Annotated

import structlog
from fastapi.params import Depends
from pydantic_core import to_json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from app.adapters.base import Adapters
from app.api.dependencies.stubs import (
    dependency_adapters,
    dependency_session_factory,
    placeholder,
)
from app.api.dto.shop.request import SHOP_ITEMS
from app.api.dto.shop.request import ShopItem
from app.api.dto.shop.response import UrlResponse
from app.api.exceptions import ClientError
from app.db.models import CurrenciesEnum
from app.db.models import TransactionStatusEnum, TransactionTypeEnum
from app.db.models import WheelPrizeEnum
from app.services.base.base import BaseService
from app.services.dto.auth import WebappData
from app.services.dto.shop import PaymentCallbackDTO
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
    async def handle_payment_callback(self, data: PaymentCallbackDTO) -> None:
        item = SHOP_ITEMS[data.item_id]

        transaction_id = None
        rocket_id = None
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
            rocket_skin=item.rocket_skin,
            callback_data=data.callback_data,
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

        raise NotImplementedError
