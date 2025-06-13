import traceback
from datetime import datetime, timedelta
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
from app.config.constants import (
    ROCKET_CAPACITY_DEFAULT,
    ROCKET_CAPACITY_OFFLINE,
    ROCKET_CAPACITY_PREMIUM,
    ROCKET_TIMEOUT_DEFAULT,
    ROCKET_TIMEOUT_OFFLINE,
    ROCKET_TIMEOUT_PREMIUM,
)
from app.config.constants import WHEEL_TIMEOUT
from app.db.models import CurrenciesEnum, RocketTypeEnum, User
from app.services.base.base import BaseService

logger = structlog.stdlib.get_logger()


class TaskService(BaseService):
    def __init__(
        self,
        adapters: Annotated[Adapters, Depends(dependency_adapters)],
        session_factory: Annotated[sessionmaker, Depends(dependency_session_factory)],
        session: Annotated[AsyncSession, Depends(placeholder)] = None,
    ):
        super().__init__(session_factory=session_factory, adapters=adapters, session=session)

        self.repo = self.repos.task
        self.adapters = adapters

    @BaseService.single_transaction
    async def give_rocket(self, rocket_type: RocketTypeEnum, full: bool, telegram_id: int) -> None:
        fuel_capacity = {
            RocketTypeEnum.default: ROCKET_CAPACITY_DEFAULT,
            RocketTypeEnum.offline: ROCKET_CAPACITY_OFFLINE,
            RocketTypeEnum.premium: ROCKET_CAPACITY_PREMIUM,
        }[rocket_type]

        await self.repos.user.create_user_rocket(
            type=rocket_type,
            user_id=telegram_id,
            fuel_capacity=fuel_capacity,
            current_fuel=fuel_capacity if full else 0,
        )

    async def grant_rocket(self, user: User) -> None:
        rockets_data = [
            dict(
                type=RocketTypeEnum.default,
                fuel_capacity=ROCKET_CAPACITY_DEFAULT,
                timeout=ROCKET_TIMEOUT_DEFAULT,
            ),
            dict(
                type=RocketTypeEnum.offline,
                fuel_capacity=ROCKET_CAPACITY_OFFLINE,
                timeout=ROCKET_TIMEOUT_OFFLINE,
            ),
            dict(
                type=RocketTypeEnum.premium,
                fuel_capacity=ROCKET_CAPACITY_PREMIUM,
                timeout=ROCKET_TIMEOUT_PREMIUM,
            ),
        ]

        existing_rockets = {rocket.type for rocket in user.rockets}

        if {i["type"].value for i in rockets_data}.issubset(existing_rockets):
            logger.info(f"User {user.telegram_id} already has rockets.")
            return

        given_rockets = list()

        async with self.repo.transaction() as t:
            for rocket in rockets_data:
                if rocket["type"].value in existing_rockets:
                    continue

                next_receive = getattr(user, f"next_{rocket['type'].value}_rocket_at")
                if next_receive > datetime.utcnow():
                    continue

                logger.info(f"Giving {rocket['type'].value} rocket to user {user.telegram_id}")

                await self.repos.user.create_user_rocket(
                    type=rocket["type"],
                    user_id=user.telegram_id,
                    fuel_capacity=rocket["fuel_capacity"],
                    current_fuel=0,
                )

                await self.repos.user.update_user(
                    **{
                        "telegram_id": user.telegram_id,
                        f"next_{rocket['type'].value}_rocket_at": datetime.utcnow() + timedelta(minutes=rocket["timeout"]),
                    }
                )

                given_rockets.append(rocket["type"].value)

            await t.commit()

        if RocketTypeEnum.premium in given_rockets:
            await self.adapters.bot.send_menu(
                user=user, custom_text=self.adapters.i18n.t("task.premium_rocket_given", user.tg_language_code)
            )

    async def give_offline_rocket(self) -> None:
        async with self.repo.transaction():
            users = await self.repo.get_offline_rocket_users()

        for user in users:
            try:
                await self.grant_rocket(user)
            except Exception as e:
                logger.error(
                    event=f"Failed to give offline rocket to user {user.telegram_id}: {e}",
                    exception=traceback.format_exception(e),
                )

    async def _give_wheel(self, user: User) -> None:
        async with self.repo.transaction() as t:
            await self.services.transaction.change_user_balance(
                telegram_id=user.telegram_id,
                currency=CurrenciesEnum.wheel,
                amount=1,
                user_kwargs=dict(next_wheel_at=datetime.utcnow() + timedelta(minutes=WHEEL_TIMEOUT)),
            )
            await t.commit()

        await self.adapters.bot.send_menu(
            user=user, custom_text=self.adapters.i18n.t("task.wheel_given", user.tg_language_code)
        )

    async def give_wheel(self) -> None:
        async with self.repo.transaction():
            users = await self.repo.get_wheel_users()

        for user in users:
            try:
                await self._give_wheel(user)
            except Exception as e:
                logger.error(
                    event=f"Failed to give wheel to user {user.telegram_id}: {e}",
                    exception=traceback.format_exception(e),
                )
