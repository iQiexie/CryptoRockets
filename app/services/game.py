import random
from typing import Annotated

import structlog
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from app.adapters.base import Adapters
from app.api.dependencies.stubs import (
    dependency_adapters,
    dependency_session_factory,
    placeholder,
)
from app.api.dto.game.request import LaunchResponse
from app.api.dto.game.response import WHEEL_PRIZES, WheelPrizeEnum, WheelPrizeResponse
from app.api.exceptions import ClientError
from app.config.constants import ROCKET_CAPACITY_PREMIUM
from app.db.models import CurrenciesEnum, RocketTypeEnum, TransactionTypeEnum
from app.services.base.base import BaseService
from app.services.dto.auth import WebappData

logger = structlog.stdlib.get_logger()


class GameService(BaseService):
    def __init__(
        self,
        adapters: Annotated[Adapters, Depends(dependency_adapters)],
        session_factory: Annotated[sessionmaker, Depends(dependency_session_factory)],
        session: Annotated[AsyncSession, Depends(placeholder)] = None,
    ):
        super().__init__(session_factory=session_factory, adapters=adapters, session=session)

        self.repo = self.repos.game
        self.adapters = adapters

    @BaseService.single_transaction
    async def spin_wheel(self, current_user: WebappData) -> WheelPrizeResponse:
        prize = random.choices(  # noqa: S311
            population=WHEEL_PRIZES,
            weights=[prize.weight for prize in WHEEL_PRIZES],
            k=1,
        )[0]

        if prize.type == WheelPrizeEnum.tokens:
            await self.services.transaction.change_user_balance(
                telegram_id=current_user.id,
                currency=CurrenciesEnum.token,
                amount=prize.amount,
                tx_type=TransactionTypeEnum.wheel_spin,
            )
        elif prize.type == WheelPrizeEnum.fuel:
            await self.services.transaction.change_user_balance(
                telegram_id=current_user.id,
                currency=CurrenciesEnum.fuel,
                amount=prize.amount,
                tx_type=TransactionTypeEnum.wheel_spin,
            )
        elif prize.type == WheelPrizeEnum.premium_rocket_full:
            await self.give_rocket(
                telegram_id=current_user.id,
                rocket_type=RocketTypeEnum.premium,
                fuel=ROCKET_CAPACITY_PREMIUM,
            )
        elif prize.type == WheelPrizeEnum.premium_rocket:
            await self.give_rocket(telegram_id=current_user.id, rocket_type=RocketTypeEnum.premium, fuel=0)
        else:
            raise NotImplementedError

        return prize

    async def give_rocket(self, telegram_id: int, rocket_type: RocketTypeEnum, fuel: int) -> None:
        rocket = await self.repo.get_rocket_for_update(telegram_id=telegram_id, rocket_type=rocket_type)
        await self.repo.update_rocket(
            rocket_id=rocket.id,
            current_fuel=rocket.current_fuel + fuel,
            count=rocket.count + 1,
            enabled=True,
        )

    @BaseService.single_transaction
    async def launch_rocket(self, current_user: WebappData, rocket_type: RocketTypeEnum) -> LaunchResponse:
        rocket = await self.repo.get_rocket_for_update(rocket_type=rocket_type, telegram_id=current_user.id)

        if not rocket:
            raise ClientError(message="Rocket not found")

        if rocket.current_fuel < rocket.fuel_capacity:
            raise ClientError(message="Rocket is not fully fueled")

        if not rocket.enabled:
            raise ClientError(message="Rocket is not enabled")

        balance_diff = random.uniform(0.01, 0.1)  # noqa: S311
        currency = random.choice([CurrenciesEnum.usdt, CurrenciesEnum.ton])  # noqa: S311

        balance_changes = await self.services.transaction.change_user_balance(
            telegram_id=current_user.id,
            currency=currency,
            amount=balance_diff,
            tx_type=TransactionTypeEnum.rocket_launch,
        )

        await self.repo.update_rocket(
            rocker_id=rocket.id,
            current_fuel=rocket.current_fuel - rocket.fuel_capacity,
            count=rocket.count - 1 if rocket.type == RocketTypeEnum.premium else rocket.count,
        )

        return LaunchResponse(
            **{
                f"new_balance_{currency.value}": getattr(balance_changes.user, f"balance_{currency.value}"),
            },
        )
