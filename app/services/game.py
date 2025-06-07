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
from app.api.dto.game.request import UpdateRocketRequest
from app.api.dto.game.response import (
    WHEEL_PRIZES,
    LaunchResponse,
    WheelPrizeEnum,
    WheelPrizeResponse,
)
from app.api.exceptions import ClientError
from app.config.constants import MAX_BALANCE
from app.config.constants import ROCKET_CAPACITY_DEFAULT
from app.config.constants import ROCKET_CAPACITY_OFFLINE
from app.config.constants import ROCKET_CAPACITY_PREMIUM
from app.db.models import (
    CurrenciesEnum,
    Rocket,
    RocketTypeEnum,
    TransactionTypeEnum,
    WheelPrize,
)
from app.db.models import User
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
    async def get_latest_wheel_winners(self) -> list[WheelPrize]:
        return await self.repo.get_wheel_winners()

    @BaseService.single_transaction
    async def spin_wheel(self, current_user: WebappData) -> WheelPrizeResponse:
        await self.services.transaction.change_user_balance(
            telegram_id=current_user.telegram_id,
            currency=CurrenciesEnum.wheel,
            amount=-1,
            tx_type=TransactionTypeEnum.wheel_spin,
        )

        prize = random.choices(  # noqa: S311
            population=WHEEL_PRIZES,
            weights=[prize.chance for prize in WHEEL_PRIZES],
            k=1,
        )[0]

        if prize.type == WheelPrizeEnum.token:
            await self.services.transaction.change_user_balance(
                telegram_id=current_user.telegram_id,
                currency=CurrenciesEnum.token,
                amount=prize.amount,
                tx_type=TransactionTypeEnum.wheel_spin,
            )
        elif prize.type == WheelPrizeEnum.fuel:
            await self.services.transaction.change_user_balance(
                telegram_id=current_user.telegram_id,
                currency=CurrenciesEnum.fuel,
                amount=prize.amount,
                tx_type=TransactionTypeEnum.wheel_spin,
            )
        elif prize.type == WheelPrizeEnum.default_rocket:
            await self.repos.user.create_user_rocket(
                user_id=current_user.telegram_id,
                type=RocketTypeEnum.default,
                fuel_capacity=ROCKET_CAPACITY_DEFAULT,
                current_fuel=ROCKET_CAPACITY_DEFAULT,
            )
        elif prize.type == WheelPrizeEnum.offline_rocket:
            await self.repos.user.create_user_rocket(
                user_id=current_user.telegram_id,
                type=RocketTypeEnum.offline,
                fuel_capacity=ROCKET_CAPACITY_OFFLINE,
                current_fuel=ROCKET_CAPACITY_OFFLINE,
            )
        elif prize.type == WheelPrizeEnum.premium_rocket:
            await self.repos.user.create_user_rocket(
                user_id=current_user.telegram_id,
                type=RocketTypeEnum.premium,
                fuel_capacity=ROCKET_CAPACITY_PREMIUM,
                current_fuel=ROCKET_CAPACITY_PREMIUM,
            )
        else:
            raise NotImplementedError

        await self.repo.create_prize(
            user_id=current_user.telegram_id,
            type=prize.type,
            amount=prize.amount,
            icon=prize.icon,
        )

        return prize

    @staticmethod
    def get_balance_diff(user: User, currency: CurrenciesEnum) -> float:
        if user.usdt_balance + user.ton_balance < 1:
            return round(random.uniform(8, 10), 2)

        current_balance = float(getattr(user, f"{currency.value}_balance"))
        jackpot_chance = 0.015
        if random.random() < jackpot_chance:
            if current_balance < MAX_BALANCE - 20:
                return round(random.uniform(1.5, 3.0), 2)
            elif current_balance < MAX_BALANCE - 10:
                return round(random.uniform(1, 2), 2)
            elif current_balance < MAX_BALANCE - 5:
                return round(random.uniform(0.1, 0.5), 2)

        # Нормализуем баланс от 0 до 1
        progress = min(current_balance / 60, 1.0)

        # 🔀 Рандомный диапазон награды в зависимости от баланса
        min_reward = 0.05 + (1 - progress) * 0.50  # от 0.05 до ~0.55
        max_reward = 0.1 + (1 - progress) * 1  # от 0.1 до ~1.1

        # 🧮 Ограничиваем диапазон
        reward = random.uniform(min_reward, max_reward)
        return round(min(reward, 2), 2)

    @BaseService.single_transaction
    async def launch_rocket(self, current_user: WebappData, rocket_id: int) -> LaunchResponse:
        rocket = await self.repo.get_rocket_for_update(rocket_id=rocket_id, telegram_id=current_user.telegram_id)

        if not rocket:
            raise ClientError(message="Rocket not found")

        if rocket.current_fuel < rocket.fuel_capacity:
            raise ClientError(message="Rocket is not fully fueled")

        if not rocket.enabled:
            raise ClientError(message="Rocket is not enabled")

        currency = random.choice([CurrenciesEnum.usdt, CurrenciesEnum.ton])  # noqa: S311
        user = await self.repos.user.get_user_by_telegram_id(telegram_id=current_user.telegram_id)
        balance_diff = self.get_balance_diff(user=user, currency=currency)

        balance_changes = await self.services.transaction.change_user_balance(
            telegram_id=current_user.telegram_id,
            currency=currency,
            amount=balance_diff,
            tx_type=TransactionTypeEnum.rocket_launch,
        )

        await self.repo.update_rocket(rocket_id=rocket.id, enabled=False, current_fuel=0)

        return LaunchResponse(
            **{
                f"new_balance_{currency.value}": getattr(balance_changes.user, f"{currency.value}_balance"),
            },
        )
