from typing import Sequence
from sqlalchemy import func
from sqlalchemy import or_
from sqlalchemy import select
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.constants import ROCKET_TIMEOUT_DEFAULT
from app.config.constants import ROCKET_TIMEOUT_OFFLINE
from app.config.constants import ROCKET_TIMEOUT_PREMIUM
from app.config.constants import WHEEL_TIMEOUT
from app.db.models import User
from app.db.repos.base.base import BaseRepo


class TaskRepo(BaseRepo):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session)

    async def get_offline_rocket_users(self) -> Sequence[User]:
        min_timeout = min(ROCKET_TIMEOUT_DEFAULT, ROCKET_TIMEOUT_OFFLINE, ROCKET_TIMEOUT_PREMIUM)
        interval_str = f"INTERVAL '{min_timeout} minutes'"

        stmt = (
            select(User)
            .where(
                or_(
                    User.default_rocket_received <= func.now() - text(interval_str),
                    User.offline_rocket_received <= func.now() - text(interval_str),
                    User.premium_rocket_received <= func.now() - text(interval_str),
                )
            )
        )

        query = await self.session.execute(stmt)
        return query.scalars().all()

    async def get_wheel_users(self) -> Sequence[User]:
        stmt = (
            select(User)
            .where(
                User.wheel_received <= func.now() - text(f"INTERVAL '{WHEEL_TIMEOUT} minutes'"),
                User.updated_at >= func.now() - text("INTERVAL '1 day'"),
            )
        )

        query = await self.session.execute(stmt)
        return query.scalars().all()
