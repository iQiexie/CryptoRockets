from collections import defaultdict
from typing import Sequence
from sqlalchemy import func, literal_column, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.functions import now

from app.db.models import BetConfig
from app.db.models import GiftUser
from app.db.models import GiftUserStatusEnum
from app.db.models import Rocket, RocketTypeEnum, WheelPrize
from app.db.repos.base.base import BaseRepo


class GameRepo(BaseRepo):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session)

    async def create_gift_user(self, **kwargs) -> GiftUser:
        model = GiftUser(**kwargs)
        self.session.add(model)
        return model

    async def get_user_gifts(self, user_id: int) -> Sequence[GiftUser]:
        stmt = (
            select(GiftUser)
            .where(
                GiftUser.status == GiftUserStatusEnum.created,
                GiftUser.user_id == user_id,
            )
            .options(joinedload(GiftUser.gift))
        )

        query = await self.session.execute(stmt)
        return query.scalars().all()

    async def get_latest_gifts(self) -> Sequence[GiftUser]:
        stmt = (
            select(GiftUser)
            .where(
                GiftUser.status == GiftUserStatusEnum.created,
                GiftUser.created_at <= now(),
            )
            .options(joinedload(GiftUser.gift))
            .limit(50)
        )

        query = await self.session.execute(stmt)
        return query.scalars().all()

    async def get_bets_config_amount(self, amount: float) -> Sequence[BetConfig]:
        stmt = select(BetConfig).options(joinedload(BetConfig.collection)).where(BetConfig.bet_from == amount)
        query = await self.session.execute(stmt)
        return query.scalars().all()

    async def get_bets_config(self) -> dict[list[BetConfig]]:
        stmt = select(BetConfig).options(joinedload(BetConfig.collection))
        query = await self.session.execute(stmt)
        configs = query.scalars().all()

        resp = defaultdict(list)

        for config in configs:
            resp[config.bet_from].append(config)

        return resp

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
