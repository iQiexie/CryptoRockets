from typing import Annotated

import structlog
from aiogram.enums import ChatMemberStatus
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
from app.db.models import CurrenciesEnum, Task, TransactionTypeEnum, User
from app.services.base.base import BaseService
from app.services.dto.auth import WebappData

logger = structlog.stdlib.get_logger()


class UserTaskService(BaseService):
    def __init__(
        self,
        adapters: Annotated[Adapters, Depends(dependency_adapters)],
        session_factory: Annotated[sessionmaker, Depends(dependency_session_factory)],
        session: Annotated[AsyncSession, Depends(placeholder)] = None,
    ):
        super().__init__(session_factory=session_factory, adapters=adapters, session=session)

        self.repo = self.repos.user_task
        self.adapters = adapters

    @BaseService.single_transaction
    async def get_tasks(self, current_user: WebappData) -> list[Task]:
        return await self.repo.get_user_tasks(telegram_id=current_user.telegram_id)

    async def _is_subscribed(self, telegram_id: int, task: Task) -> bool:
        resp = await self.adapters.bot.get_chat_member(
            chat_id=task.telegram_id,
            user_id=telegram_id,
        )

        if resp.status in (ChatMemberStatus.MEMBER, ChatMemberStatus.CREATOR, ChatMemberStatus.ADMINISTRATOR):
            return True

        return False

    async def _complete_task(self, task: Task, telegram_id: int) -> None:
        await self.repo.create_user_task(task_id=task.id, telegram_id=telegram_id)

        if task.rocket_data:
            rocket = await self.repos.game.get_rocket(rocket_type=task.rocket_data["type"])
            fuel = rocket.fuel_capacity if task.rocket_data["full"] else 0
            await self.services.game.give_rocket(
                telegram_id=telegram_id,
                rocket_type=task.rocket_data["type"],
                fuel=fuel,
            )
        else:
            await self.services.transaction.change_user_balance(
                telegram_id=telegram_id,
                currency=CurrenciesEnum[task.reward],
                amount=task.reward_amount,
                tx_type=TransactionTypeEnum.task_completion,
            )

    @BaseService.single_transaction
    async def check_subscription(self, current_user: WebappData, task_id: int) -> User:
        task = await self.repo.get_task(task_id=task_id)
        is_subscribed = await self._is_subscribed(telegram_id=current_user.telegram_id, task=task)

        if not is_subscribed:
            raise ClientError(message="Subscription not found", status_code=status.HTTP_418_IM_A_TEAPOT)

        user_task = await self.repo.get_user_task(task_id=task_id, telegram_id=current_user.telegram_id)

        if user_task:
            raise ClientError(message="Already completed", status_code=status.HTTP_418_IM_A_TEAPOT)

        await self._complete_task(task=task, telegram_id=current_user.telegram_id)
        await self.session.commit()
        return await self.repos.user.get_user_by_telegram_id(telegram_id=current_user.telegram_id)

    @BaseService.single_transaction
    async def check_invite(self, current_user: WebappData, task_id: int) -> User:
        task = await self.repo.get_task(task_id=task_id)
        user_task = await self.repo.get_user_task(task_id=task_id, telegram_id=current_user.telegram_id)

        if user_task:
            raise ClientError(message="Already completed", status_code=status.HTTP_418_IM_A_TEAPOT)

        referrals = await self.repo.get_user_referrals(telegram_id=current_user.telegram_id)

        if len(referrals) < task.amount:
            raise ClientError(
                message=f"Invite at least {task.amount - len(referrals)} more users",
                status_code=status.HTTP_418_IM_A_TEAPOT,
            )

        await self._complete_task(task=task, telegram_id=current_user.telegram_id)
        await self.session.commit()
        return await self.repos.user.get_user_by_telegram_id(telegram_id=current_user.telegram_id)
