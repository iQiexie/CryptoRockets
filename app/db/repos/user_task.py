from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import coalesce

from app.db.models import Task, TaskStatusEnum, TaskUser, User
from app.db.repos.base.base import BaseRepo


class UserTaskRepo(BaseRepo):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session)

    async def get_user_referrals(self, telegram_id: int) -> Sequence[User]:
        stmt = select(User).where(User.referral_from == telegram_id)
        query = await self.session.execute(stmt)
        return query.scalars().all()

    async def get_user_task(self, task_id: int, telegram_id: int) -> TaskUser | None:
        stmt = select(TaskUser).where(
            TaskUser.task_id == task_id,
            TaskUser.user_id == telegram_id,
            TaskUser.status == TaskStatusEnum.completed,
        )
        query = await self.session.execute(stmt)
        return query.scalar_one_or_none()

    async def create_user_task(self, task_id: int, telegram_id: int) -> TaskUser:
        model = TaskUser(task_id=task_id, user_id=telegram_id)
        self.session.add(model)
        return model

    async def get_task(self, task_id: int) -> Task:
        stmt = select(Task).where(Task.id == task_id)
        query = await self.session.execute(stmt)
        return query.scalar_one()

    async def get_user_tasks(self, telegram_id: int) -> list[Task]:
        stmt = (
            select(Task)
            .add_columns(coalesce(TaskUser.status, TaskStatusEnum.new.value).label("status"))
            .outerjoin(
                TaskUser,
                (Task.id == TaskUser.task_id)
                & (TaskUser.user_id == telegram_id)
                & (TaskUser.status == TaskStatusEnum.completed),
            )
        )

        query = await self.session.execute(stmt)
        tasks = query.mappings().all()

        response = []
        for row_mapping in tasks:
            task, status = row_mapping.values()
            task.status = status
            response.append(task)

        return response
