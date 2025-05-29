from typing import Sequence

from sqlalchemy import func
from sqlalchemy import literal_column
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.db.models import Rocket, RocketTypeEnum
from app.db.models import WheelPrize
from app.db.repos.base.base import BaseRepo


class GameRepo(BaseRepo):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session)

    async def get_wheel_winners(self) -> Sequence[WheelPrize]:
        stmt = (
            select(WheelPrize)
            .where(
                WheelPrize.created_at > (func.now() - literal_column("interval '60 seconds'"))
            )
            .options(joinedload(WheelPrize.user))
        )

        query = await self.session.execute(stmt)
        return query.scalars().all()

    async def create_prize(self, **kwargs) -> WheelPrize:
        model = WheelPrize(**kwargs)
        self.session.add(model)
        return model

    async def get_rocket_for_update(self, telegram_id: int, rocket_type: RocketTypeEnum) -> Rocket:
        stmt = select(Rocket).where(Rocket.type == rocket_type, Rocket.user_id == telegram_id).with_for_update()

        stmt = await self.session.execute(stmt)
        return stmt.scalar_one_or_none()

    async def update_rocket(self, rocket_id: int, **kwargs) -> Rocket:
        return await self.update(Rocket, Rocket.id == rocket_id, **kwargs)
