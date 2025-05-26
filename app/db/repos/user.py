from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User
from app.db.repos.base.base import BaseRepo


class UserRepo(BaseRepo):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session)

    async def create_user(self, **kwargs) -> User:
        stmt = insert(User).values(**kwargs).on_conflict_do_nothing()
        await self.session.execute(stmt)
        return User(**kwargs)

    async def get_user_by_telegram_id(self, telegram_id: int = None) -> User | None:
        stmt = select(User).filter(User.telegram_id == telegram_id)
        query = await self.session.execute(stmt)
        return query.scalar_one_or_none()

    async def get_user_for_update(self, telegram_id: int = None) -> User:
        stmt = select(User).where(User.telegram_id == telegram_id).with_for_update()

        query = await self.session.execute(stmt)
        return query.scalar_one()

    async def update_user(self, telegram_id: int, **kwargs) -> User:
        return await self.update(User, User.telegram_id == telegram_id, **kwargs)
