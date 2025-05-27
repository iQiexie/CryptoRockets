from typing import Annotated

import structlog
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from starlette import status

from app.adapters.base import Adapters
from app.api.dependencies.stubs import (
    dependency_adapters,
    dependency_session_factory,
    placeholder,
)
from app.api.exceptions import ClientError
from app.db.models import (
    CurrenciesEnum,
    TransactionStatusEnum,
    TransactionTypeEnum,
)
from app.services.base.base import BaseService
from app.services.dto.transaction import ChangeUserBalanceDTO

logger = structlog.stdlib.get_logger()


class TransactionService(BaseService):
    def __init__(
        self,
        adapters: Annotated[Adapters, Depends(dependency_adapters)],
        session_factory: Annotated[sessionmaker, Depends(dependency_session_factory)],
        session: Annotated[AsyncSession, Depends(placeholder)] = None,
    ):
        super().__init__(session_factory=session_factory, adapters=adapters, session=session)

        self.repo = self.repos.transaction
        self.adapters = adapters

    async def change_user_balance(
        self,
        telegram_id: int,
        currency: CurrenciesEnum,
        amount: float,
        tx_type: TransactionTypeEnum,
        tx_kwargs: dict | None = None,
        user_kwargs: dict | None = None,
    ) -> ChangeUserBalanceDTO:
        user = await self.repos.user.get_user_for_update(telegram_id=telegram_id)

        balance_name = f"balance_{currency.value}"
        balance_before = getattr(user, balance_name)
        balance_after = balance_before + amount

        if not tx_kwargs:
            tx_kwargs = dict()

        if not user_kwargs:
            user_kwargs = dict()

        if balance_after < 0:
            raise ClientError(message="Not enough balance", status_code=status.HTTP_402_PAYMENT_REQUIRED)

        user_kwargs[balance_name] = balance_after

        logger.info(f"Updating user balance {balance_name=} {balance_after=}, diff={amount}")
        await self.repos.user.update_user(user_id=user.id, **user_kwargs)

        tx = await self.repo.create_transaction(
            user_id=telegram_id,
            balance_before=balance_before,
            balance_after=balance_after,
            balance_amount=amount,
            balance_currency=currency,
            tx_type=tx_type,
            status=TransactionStatusEnum.success,
            **tx_kwargs,
        )
        await self.session.flush()

        return ChangeUserBalanceDTO(user=user, transaction=tx)
