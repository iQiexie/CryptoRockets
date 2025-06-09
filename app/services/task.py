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
from app.db.models import RocketTypeEnum
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

        self.repo = self.repos.user
        self.adapters = adapters

    @BaseService.single_transaction
    async def give_rocket(self, rocket_type: RocketTypeEnum, fool: bool, telegram_id: int) -> None:
        fuel_capacity = {
            RocketTypeEnum.default: ROCKET_CAPACITY_DEFAULT,
            RocketTypeEnum.offline: ROCKET_CAPACITY_OFFLINE,
            RocketTypeEnum.premium: ROCKET_CAPACITY_PREMIUM,
        }[rocket_type]

        await self.repo.create_user_rocket(
            type=rocket_type,
            user_id=telegram_id,
            fuel_capacity=fuel_capacity,
            current_fuel=fuel_capacity if fool else 0,
        )
