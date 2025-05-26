import asyncio
import traceback
from typing import Callable, Type, TypeVar

import structlog
from pydantic import BaseModel, TypeAdapter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from starlette import status

from app.adapters.base import Adapters
from app.api.dto.base import PaginatedRequest, PaginatedResponse
from app.db.repos.base.base import PaginatedResult
from app.db.repos.base.repos import Repos
from app.services.base.services import Services

Model = TypeVar("Model", bound=BaseModel)
logger = structlog.stdlib.get_logger()


class BaseService:
    def __init__(self, adapters: Adapters, session_factory: sessionmaker, session: AsyncSession = None):
        if session:
            self.session = session
        else:
            self.session = session_factory()

        self.adapters = adapters
        self.repos = Repos(session=self.session)
        self.services = Services(session=self.session, adapters=self.adapters, session_factory=session_factory)
        self.session_factory = session_factory

    @staticmethod
    def paginate(
        response_model: Type[Model],
        result: PaginatedResult,
        pagination: PaginatedRequest,
    ) -> PaginatedResponse[Model]:
        return PaginatedResponse(
            items=TypeAdapter(list[response_model]).validate_python(result.items),
            total=result.total,
            limit=len(result.items),
            page=pagination.page or 1,
        )

    @staticmethod
    def single_transaction(f: Callable) -> Callable:
        async def wrapper(*args, **kwargs) -> None:
            async with args[0].repo.transaction() as t:
                result = await f(*args, **kwargs)
                await t.commit()

            return result

        return wrapper

    @staticmethod
    def log_exception(f: Callable) -> Callable:
        async def wrapper(*args, **kwargs) -> None:
            try:
                return await f(*args, **kwargs)
            except Exception as e:
                logger.error(
                    event="A server error has occurred (tasks)",
                    exception=traceback.format_exception(e),
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

                asyncio.create_task(
                    args[0].adapters.alerts.handle_alert(
                        response=None,
                        total_time=0,
                        exception=e,
                    )
                )

                raise e

        return wrapper
