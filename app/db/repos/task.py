from typing import Sequence

from sqlalchemy import desc
from sqlalchemy import func, or_, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.constants import (
    WHEEL_TIMEOUT,
)
from app.db.models import Collection
from app.db.models import Gift
from app.db.models import User
from app.db.repos.base.base import BaseRepo


class TaskRepo(BaseRepo):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session)

    async def get_collection(self, slug: str) -> Collection | None:
        stmt = select(Collection).where(Collection.slug == slug)
        query = await self.session.execute(stmt)
        return query.scalar_one_or_none()

    async def create_gift(self, **kwargs) -> Gift:
        gift = Gift(**kwargs)
        self.session.add(gift)
        return gift

    async def create_collection(self, **kwargs) -> Collection:
        collection = Collection(**kwargs)
        self.session.add(collection)
        return collection

    async def get_last_gift(self) -> Gift | None:
        stmt = select(Gift).order_by(desc(Gift.transfer_date)).limit(1)
        query = await self.session.execute(stmt)
        return query.scalar_one_or_none()

    async def get_offline_rocket_users(self) -> Sequence[User]:
        stmt = select(User).where(
            or_(
                User.next_default_rocket_at <= func.now(),
                User.next_offline_rocket_at <= func.now(),
                User.next_premium_rocket_at <= func.now(),
            ),
            User.last_online >= func.now() - text(f"INTERVAL '1 day'"),
        )

        query = await self.session.execute(stmt)
        return query.scalars().all()

    async def get_wheel_users(self) -> Sequence[User]:
        stmt = (
            select(User)
            .where(
                User.next_wheel_at <= func.now(),
                User.last_online >= func.now() - text(f"INTERVAL '{WHEEL_TIMEOUT} minutes'"),
            )
        )

        query = await self.session.execute(stmt)
        return query.scalars().all()
