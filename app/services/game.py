import random
from decimal import Decimal
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
from app.api.dto.game.response import (
    WHEEL_PRIZES,
    LaunchResponse,
    WheelPrizeEnum,
    WheelPrizeResponse,
)
from app.api.dto.user.response import RocketResponse
from app.api.dto.user.response import UserResponse
from app.api.exceptions import ClientError
from app.config.constants import FUEL_CAPACITY_MAP
from app.config.constants import MAX_BALANCE
from app.db.models import (
    CurrenciesEnum,
    RocketTypeEnum,
    TransactionTypeEnum,
    User,
    WheelPrize,
)
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
        balance_data = await self.services.transaction.change_user_balance(
            telegram_id=current_user.telegram_id,
            currency=CurrenciesEnum.wheel,
            amount=-1,
            tx_type=TransactionTypeEnum.wheel_spin,
        )

        user = balance_data.user
        rocket = None
        currencies = (WheelPrizeEnum.token, WheelPrizeEnum.usdt, WheelPrizeEnum.ton, WheelPrizeEnum.wheel)
        balance_currencies = (WheelPrizeEnum.usdt, WheelPrizeEnum.ton)

        prize = random.choices(
            population=WHEEL_PRIZES,
            weights=[prize.chance for prize in WHEEL_PRIZES],
            k=1,
        )[0]

        if prize.type in balance_currencies:
            if getattr(user, f"{prize.type.value}_balance") > (MAX_BALANCE - 10):
                logger.info("Scamming user!")
                prize = random.choices(  # noqa: S311
                    population=[i for i in WHEEL_PRIZES if i.type not in balance_currencies],
                    weights=[prize.chance for prize in WHEEL_PRIZES if prize.type not in balance_currencies],
                    k=1,
                )[0]

        try:
            if balance_data.user.spin_count == 0:
                prize = [i for i in WHEEL_PRIZES if i.type == WheelPrizeEnum.ton and i.amount == 1][0]
            elif balance_data.user.spin_count == 2:
                prize = [i for i in WHEEL_PRIZES if i.type == WheelPrizeEnum.usdt and i.amount == 1][0]
        except IndexError:
            logger.error(f"First spin for 1 ton not found: {WHEEL_PRIZES=}")

        if prize.type in currencies:
            _resp = await self.services.transaction.change_user_balance(
                telegram_id=current_user.telegram_id,
                currency=CurrenciesEnum[prize.type.value],
                amount=prize.amount,
                tx_type=TransactionTypeEnum.wheel_spin,
            )
            user = _resp.user
        elif prize.type in (
            WheelPrizeEnum.default_rocket,
            WheelPrizeEnum.offline_rocket,
            WheelPrizeEnum.premium_rocket,
        ):
            rocket_type = RocketTypeEnum[prize.type.value.replace("_rocket", "")]
            rocket = await self.repos.user.create_user_rocket(
                user_id=current_user.telegram_id,
                type=rocket_type,
                fuel_capacity=FUEL_CAPACITY_MAP.get(rocket_type, 1),
                current_fuel=0,
                seen=True,
            )
            user.rockets.append(rocket)
        else:
            raise NotImplementedError(f"Prize type {prize.type} is not implemented")

        await self.repos.user.update_user(telegram_id=current_user.telegram_id, spin_count=user.spin_count + 1)

        await self.repo.create_prize(
            user_id=current_user.telegram_id,
            type=prize.type,
            amount=prize.amount,
            icon=prize.icon,
        )

        prize.user = UserResponse.model_validate(user)
        prize.rocket = RocketResponse.model_validate(rocket) if rocket else None
        return prize

    @staticmethod
    def _get_balance_diff(user: User, currency: CurrenciesEnum, rocket_type: RocketTypeEnum) -> float:
        if currency == CurrenciesEnum.token:
            return random.randint(50, 300)

        if user.usdt_balance + user.ton_balance < 1:
            return round(random.uniform(8, 10), 2)  # noqa: S311

        current_balance = float(getattr(user, f"{currency.value}_balance"))

        if (rocket_type == RocketTypeEnum.super) and (current_balance < MAX_BALANCE - 20):
            return round(random.uniform(2.5, 5.0), 2)  # noqa: S311

        jackpot_chance = 0.015
        if random.random() < jackpot_chance:  # noqa: S311
            if current_balance < (MAX_BALANCE - 20):
                return round(random.uniform(1.5, 3.0), 2)  # noqa: S311
            elif current_balance < MAX_BALANCE - 10:
                return round(random.uniform(0.5, 1), 2)  # noqa: S311
            elif current_balance < MAX_BALANCE - 5:
                return round(random.uniform(0.05, 0.1), 2)  # noqa: S311

        # Нормализуем баланс от 0 до 1
        progress = min(current_balance / MAX_BALANCE, 1.0)

        # 🔀 Рандомный диапазон награды в зависимости от баланса
        min_reward = 0.01 + (1 - progress) * 0.20  # от 0.01 до ~0.21
        max_reward = 0.05 + (1 - progress) * 0.5  # от 0.05 до ~0.55

        # 🧮 Ограничиваем диапазон
        reward = random.uniform(min_reward, max_reward)  # noqa: S311
        return round(min(reward, 2), 2)

    def get_balance_diff(self, user: User, currency: CurrenciesEnum, rocket_type: RocketTypeEnum) -> float:
        if currency == CurrenciesEnum.token:
            return random.randint(50, 300)

        resp = self._get_balance_diff(user=user, currency=currency, rocket_type=rocket_type)
        if getattr(user, f"{currency.value}_balance") + Decimal(resp) >= MAX_BALANCE:
            resp = random.uniform(0.001, 0.01)

        if getattr(user, f"{currency.value}_balance") + Decimal(resp) >= MAX_BALANCE:
            resp = 0.00001

        return resp

    async def _handle_regular_rocket(self, user: User, rocket_type: RocketTypeEnum) -> LaunchResponse:
        currency = random.choices(
            population=[CurrenciesEnum.usdt, CurrenciesEnum.ton, CurrenciesEnum.token],
            weights=[30, 30, 40]
        )[0]
        balance_diff = self.get_balance_diff(user=user, currency=currency, rocket_type=rocket_type)

        await self.services.transaction.change_user_balance(
            telegram_id=user.telegram_id,
            currency=currency,
            amount=balance_diff,
            tx_type=TransactionTypeEnum.rocket_launch,
        )

        return LaunchResponse(**{currency.value: balance_diff})

    async def _handle_premium_rocket(self, user: User, rocket_type: RocketTypeEnum) -> LaunchResponse:
        resp = dict()

        for currency in (CurrenciesEnum.usdt, CurrenciesEnum.ton, CurrenciesEnum.token):
            balance_diff = self.get_balance_diff(user=user, currency=currency, rocket_type=rocket_type)
            await self.services.transaction.change_user_balance(
                telegram_id=user.telegram_id,
                currency=currency,
                amount=balance_diff,
                tx_type=TransactionTypeEnum.rocket_launch,
            )
            resp[currency.value] = balance_diff

        return LaunchResponse(**resp)

    @BaseService.single_transaction
    async def launch_rocket(self, current_user: WebappData, rocket_id: int) -> LaunchResponse:
        rocket = await self.repo.get_rocket_for_update(rocket_id=rocket_id, telegram_id=current_user.telegram_id)

        if not rocket:
            raise ClientError(message="Rocket not found")

        if rocket.current_fuel < rocket.fuel_capacity:
            raise ClientError(message="Rocket is not fully fueled")

        if not rocket.enabled:
            raise ClientError(message="Rocket is not enabled")

        user = await self.repos.user.get_user_by_telegram_id(telegram_id=current_user.telegram_id)

        if rocket.type in (RocketTypeEnum.premium, RocketTypeEnum.super):
            resp = await self._handle_premium_rocket(user=user, rocket_type=rocket.type)
        else:
            resp = await self._handle_regular_rocket(user=user, rocket_type=rocket.type)

        await self.repo.update_rocket(rocket_id=rocket.id, enabled=False, current_fuel=0)
        await self.session.commit()
        await self.session.refresh(user)

        resp.user = UserResponse.model_validate(user)

        return resp
