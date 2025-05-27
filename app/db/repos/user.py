from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Rocket, RocketTypeEnum, User
from app.db.repos.base.base import BaseRepo


class UserRepo(BaseRepo):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session)

    async def get_user_by_referral(self, referral: str) -> User | None:
        stmt = select(User).filter(User.referral == referral)
        query = await self.session.execute(stmt)
        return query.scalar_one_or_none()

    async def create_user(self, **kwargs) -> User:
        user = User(**kwargs)

        rocket1 = Rocket(type=RocketTypeEnum.default, fuel_capacity=60, current_fuel=0)
        rocket2 = Rocket(type=RocketTypeEnum.offline, fuel_capacity=120, current_fuel=0)
        rocket3 = Rocket(type=RocketTypeEnum.premium, fuel_capacity=180, current_fuel=0)

        user.rockets = [rocket1, rocket2, rocket3]
        self.session.add(user)
        return user

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
