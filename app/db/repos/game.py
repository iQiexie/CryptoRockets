from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Rocket, RocketTypeEnum
from app.db.repos.base.base import BaseRepo


class GameRepo(BaseRepo):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session)

    async def get_rocket_for_update(self, telegram_id: int, rocket_type: RocketTypeEnum) -> Rocket:
        stmt = select(Rocket).where(Rocket.type == rocket_type, Rocket.user_id == telegram_id).with_for_update()

        stmt = await self.session.execute(stmt)
        return stmt.scalar_one_or_none()

    async def update_rocket(self, rocket_id: int, **kwargs) -> Rocket:
        return await self.update(Rocket, Rocket.id == rocket_id, **kwargs)
