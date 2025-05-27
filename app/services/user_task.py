from typing import Annotated

import structlog
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from app.adapters.base import Adapters
from app.api.dependencies.stubs import dependency_adapters
from app.api.dependencies.stubs import dependency_session_factory
from app.api.dependencies.stubs import placeholder
from app.db.models import Task
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
