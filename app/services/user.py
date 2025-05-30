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
from app.api.dto.user.request import UpdateUserRequest
from app.db.models import RocketTypeEnum, User
from app.services.base.base import BaseService
from app.services.dto.auth import WebappData
from app.utils import generate_random_string

logger = structlog.stdlib.get_logger()


class UserService(BaseService):
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
    async def _update_user(self, telegram_id: int, data: UpdateUserRequest) -> None:
        data_to_update = data.model_dump(exclude_none=True)

        if not data_to_update:
            return None

        await self.repo.update_user(telegram_id=telegram_id, **data_to_update)

    async def update_user(self, current_user: WebappData, data: UpdateUserRequest) -> User:
        await self._update_user(telegram_id=current_user.telegram_id, data=data)
        return await self.get_or_create_user(data=current_user)

    @BaseService.single_transaction
    async def get_user(self, telegram_id: int) -> User:
        return await self.repo.get_user_by_telegram_id(telegram_id=telegram_id)

    @BaseService.single_transaction
    async def get_or_create_user(self, data: WebappData) -> User:
        user = await self.repo.get_user_by_telegram_id(telegram_id=data.telegram_id)
        user_data = dict(
            tg_username=data.username,
            tg_first_name=data.first_name,
            tg_last_name=data.last_name,
            tg_is_premium=data.is_premium,
            tg_language_code=data.language_code,
            tg_photo_url=data.photo_url,
        )

        if data.country:
            user_data["country"] = data.country

        if user:
            user = await self.repo.update_user(telegram_id=user.telegram_id, bot_banned=False, **user_data)
            await self.session.commit()
            await self.session.refresh(user)
            return user

        user_data["referral_from"] = data.start_param
        user_data["referral"] = generate_random_string(seed=data.telegram_id)

        referral_from = await self.repo.get_user_by_referral(referral=data.start_param)
        if referral_from:
            await self.handle_referral(referral_from=referral_from, data=data)

        user = await self.repo.create_user(telegram_id=data.telegram_id, **user_data)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def handle_referral(self, referral_from: User, data: WebappData) -> None:
        rocket = await self.repos.game.get_rocket_for_update(
            telegram_id=referral_from.telegram_id,
            rocket_type=RocketTypeEnum.premium,
        )

        current_fuel = rocket.fuel_capacity
        if data.is_premium:
            current_fuel += rocket.fuel_capacity

        await self.repos.game.update_rocket(
            telegram_id=referral_from.telegram_id,
            rocket_type=RocketTypeEnum.premium,
            current_fuel=current_fuel,
        )
