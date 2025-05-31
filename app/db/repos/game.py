from typing import Sequence

from sqlalchemy import func, literal_column, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.db.models import Rocket, RocketTypeEnum, WheelPrize
from app.db.repos.base.base import BaseRepo


class GameRepo(BaseRepo):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session)

    async def get_rocket(self, rocket_type: RocketTypeEnum) -> Rocket:
        stmt = select(Rocket).where(Rocket.type == rocket_type)
        query = await self.session.execute(stmt)
        return query.scalar_one()

    async def get_wheel_winners(self) -> Sequence[WheelPrize]:
        stmt = (
            select(WheelPrize)
            .where(WheelPrize.created_at > (func.now() - literal_column("interval '60 seconds'")))
            .options(joinedload(WheelPrize.user))
        )

        query = await self.session.execute(stmt)
        return query.scalars().all()

    async def create_prize(self, **kwargs) -> WheelPrize:
        model = WheelPrize(**kwargs)
        self.session.add(model)
        return model

    async def get_rocket_for_update(
        self, telegram_id: int, rocket_type: RocketTypeEnum | None = None, rocket_id: int | None = None
    ) -> Rocket:
        stmt = select(Rocket).where(Rocket.user_id == telegram_id).with_for_update()

        if rocket_type:
            stmt = stmt.where(Rocket.type == rocket_type)

        if rocket_id:
            stmt = stmt.where(Rocket.id == rocket_id)

        stmt = await self.session.execute(stmt)
        return stmt.scalar_one_or_none()

    async def update_rocket(self, rocket_id: int, **kwargs) -> Rocket:
        return await self.update(Rocket, Rocket.id == rocket_id, **kwargs)
