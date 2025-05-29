from typing import Annotated

import structlog
from aiogram.types import SuccessfulPayment
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
from app.api.dto.shop.response import UrlResponse
from app.db.models import TransactionStatusEnum, TransactionTypeEnum
from app.services.base.base import BaseService
from app.services.dto.auth import WebappData

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
    async def handle_payment_callback(self, telegram_id: int, item_id: int, data: SuccessfulPayment) -> None:
        item = SHOP_ITEMS[item_id]

        transaction_id = None
        rocket_id = None

        if item.amount and item.currency:
            tx = await self.services.transaction.change_user_balance(
                telegram_id=telegram_id,
                currency=item.currency,
                amount=item.amount,
                tx_type=TransactionTypeEnum.purchase,
            )
            transaction_id = tx.transaction.id
        elif item.rocket_skin and item.rocket_type:
            rocket = await self.repos.game.get_rocket_for_update(telegram_id=telegram_id, rocket_type=item.rocket_type,)
            await self.repos.game.update_rocket(
                rocket_id=rocket.id,
                rocket_skins=list(rocket.skins) + [item.rocket_skin],
                current_skin=item.rocket_skin,
            )
            rocket_id = rocket.id
        else:
            raise NotImplementedError

        await self.repo.create_invoice(
            user_id=telegram_id,
            external_id=data.telegram_payment_charge_id,
            status=TransactionStatusEnum.success,
            currency="XTR",
            amount=data.total_amount,
            currency_fee=0,
            usd_amount=data.total_amount * 0.013,
            transaction_id=transaction_id,
            rocket_id=rocket_id,
            rocket_skin=item.rocket_skin,
            callback_data=data.model_dump(),
        )

    async def get_invoice_url(self, shop_item_id: int, current_user: WebappData) -> UrlResponse:
        item = SHOP_ITEMS[shop_item_id]

        item_label = self.adapters.i18n.t(message=item.label, lang=current_user.language_code)
        description = self.adapters.i18n.t(message=item.description, lang=current_user.language_code)

        params = {
            "currency": "XTR",
            "description": description,
            "payload": f"{item.id}",
            "prices": to_json([{"label": item_label, "amount": item.price}]).decode("utf-8"),
            "title": item_label,
        }

        resp = await self.adapters.telegram.send_method(method="createInvoiceLink", params=params)
        return UrlResponse(url=resp["result"])
