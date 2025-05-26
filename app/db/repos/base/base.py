from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any, AsyncContextManager, Generic, Type, TypeVar, assert_never

import async_timeout
import structlog
from sqlalchemy import Select, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute

from app.api.dto.base import PaginatedRequest
from app.config.constants import POSTGRES_TIMEOUT
from app.db.models import Base

logger = structlog.stdlib.get_logger()
Model = TypeVar("Model", Base, Base)
ModelOrDict = TypeVar("ModelOrDict", Base | dict, Base | dict)


@dataclass
class PaginatedResult(Generic[ModelOrDict]):
    items: list[ModelOrDict]
    total: int


class BaseRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def paginate(
        self,
        stmt: Select,
        pagination: PaginatedRequest,
        count: InstrumentedAttribute,
        count_column: Any | None = None,
    ) -> PaginatedResult:
        if count is not None:
            stmt = stmt.add_columns(func.count(count).over().label("total"))
        elif count_column is not None:
            stmt = stmt.add_columns(count_column)
        else:
            assert_never((count, count_column))

        if not (pagination.page and pagination.limit):
            return await self._paginate_stmt(stmt=stmt, count=count)

        offset = (pagination.page - 1) * pagination.limit
        stmt = stmt.limit(pagination.limit).offset(offset)

        return await self._paginate_stmt(stmt=stmt, count=count)

    async def _paginate_stmt(self, stmt: Select, count: InstrumentedAttribute) -> PaginatedResult:
        query = await self.session.execute(stmt)
        results = query.mappings().all()

        # Extract the total from the first row (since it's the same for all rows)
        total = results[0]["total"] if results else 0

        # Extract the items
        try:
            items = [row[count.class_.__name__] for row in results]
        except (AttributeError, KeyError):
            items = [dict(row) for row in results]

        # Return in the desired format
        return PaginatedResult(
            items=items,
            total=total,
        )

    def transaction(self, timeout: int | None = None) -> AsyncContextManager[AsyncSession]:
        @asynccontextmanager
        async def wrapped() -> AsyncContextManager[AsyncSession]:
            async with self.session as session:
                try:
                    async with async_timeout.timeout(delay=timeout or POSTGRES_TIMEOUT):
                        yield session
                except Exception as ex:
                    await session.rollback()
                    logger.info(f"Transaction exception: {ex=}, {type(ex)=}")
                    raise ex
                else:
                    await session.close()
                finally:
                    await session.close()

        return wrapped()

    async def update(self, model: Type[Model], *args: Any, **kwargs: Any) -> Model:
        stmt = update(model).where(*args).values(**kwargs).returning(model)
        stmt = select(model).from_statement(stmt).execution_options(synchronize_session="fetch")

        query = await self.session.execute(stmt)
        return query.scalar_one_or_none()
