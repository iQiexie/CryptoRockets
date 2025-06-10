import traceback
from datetime import datetime
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
)
from app.db.models import CurrenciesEnum
from app.db.models import RocketTypeEnum
from app.db.models import User
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
    async def give_rocket(self, rocket_type: RocketTypeEnum, fool: bool, telegram_id: int) -> None:
        fuel_capacity = {
            RocketTypeEnum.default: ROCKET_CAPACITY_DEFAULT,
            RocketTypeEnum.offline: ROCKET_CAPACITY_OFFLINE,
            RocketTypeEnum.premium: ROCKET_CAPACITY_PREMIUM,
        }[rocket_type]

        await self.repos.user.create_user_rocket(
            type=rocket_type,
            user_id=telegram_id,
            fuel_capacity=fuel_capacity,
            current_fuel=fuel_capacity if fool else 0,
        )

    async def _give_offline_rocket(self, user: User) -> None:
        for rocket in user.rockets:
            if rocket.type == RocketTypeEnum.offline:
                logger.info(f"User {user.telegram_id} already has an offline rocket.")
                return

        async with self.repo.transaction() as t:
            await self.repos.user.create_user_rocket(
                type=RocketTypeEnum.offline,
                user_id=user.telegram_id,
                fuel_capacity=ROCKET_CAPACITY_OFFLINE,
                current_fuel=ROCKET_CAPACITY_OFFLINE,
            )

            await self.repos.user.update_user(
                telegram_id=user.telegram_id,
                offline_rocket_received=datetime.utcnow(),
            )

            await t.commit()

        await self.adapters.bot.send_menu(
            user=user,
            custom_text=self.adapters.i18n.t("task.offline_rocket_given", user.tg_language_code)
        )

    async def give_offline_rocket(self) -> None:
        async with self.repo.transaction():
            users = await self.repo.get_offline_rocket_users()

        for user in users:
            try:
                await self._give_offline_rocket(user)
            except Exception as e:
                logger.error(
                    event=f"Failed to give offline rocket to user {user.telegram_id}: {e}",
                    exception=traceback.format_exception(e)
                )

    async def _give_wheel(self, user: User) -> None:
        async with self.repo.transaction() as t:
            await self.services.transaction.change_user_balance(
                telegram_id=user.telegram_id,
                currency=CurrenciesEnum.wheel,
                amount=1,
                user_kwargs=dict(wheel_received=datetime.utcnow()),
            )
            await t.commit()

        await self.adapters.bot.send_menu(
            user=user,
            custom_text=self.adapters.i18n.t("task.wheel_given", user.tg_language_code)
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
                    exception=traceback.format_exception(e)
                )
