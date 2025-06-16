from datetime import datetime
from datetime import timedelta

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dto.base import PaginatedRequest
from app.config.constants import ROCKET_CAPACITY_DEFAULT, ROCKET_CAPACITY_PREMIUM
from app.config.constants import ROCKET_CAPACITY_OFFLINE
from app.config.constants import ROCKET_TIMEOUT_DEFAULT
from app.config.constants import ROCKET_TIMEOUT_OFFLINE
from app.config.constants import ROCKET_TIMEOUT_PREMIUM
from app.config.constants import WHEEL_TIMEOUT
from app.db.models import Rocket, RocketTypeEnum, User
from app.db.repos.base.base import BaseRepo, PaginatedResult


class UserRepo(BaseRepo):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session)

    async def get_user_by_referral(self, telegram_id: int) -> User | None:
        stmt = select(User).filter(User.referral_from == telegram_id)
        query = await self.session.execute(stmt)
        return query.scalar_one_or_none()

    async def create_user(self, **kwargs) -> User:
        kwargs['wheel_balance'] = kwargs.get('wheel_balance', 3)
        kwargs['next_default_rocket_at'] = datetime.utcnow() + timedelta(minutes=ROCKET_TIMEOUT_DEFAULT)
        kwargs['next_offline_rocket_at'] = datetime.utcnow() + timedelta(minutes=ROCKET_TIMEOUT_OFFLINE)
        kwargs['next_premium_rocket_at'] = datetime.utcnow() + timedelta(minutes=ROCKET_TIMEOUT_PREMIUM)
        kwargs['next_wheel_at'] = datetime.utcnow() + timedelta(minutes=WHEEL_TIMEOUT)
        kwargs['next_wheel_ad_at'] = datetime.utcnow()

        user = User(**kwargs)

        user.rockets = [
            Rocket(
                type=RocketTypeEnum.premium,
                fuel_capacity=ROCKET_CAPACITY_PREMIUM,
                current_fuel=ROCKET_CAPACITY_PREMIUM,
            ),
            Rocket(
                type=RocketTypeEnum.premium,
                fuel_capacity=ROCKET_CAPACITY_PREMIUM,
                current_fuel=0,
            ),
            Rocket(
                type=RocketTypeEnum.offline,
                fuel_capacity=ROCKET_CAPACITY_OFFLINE,
                current_fuel=0,
            ),
            Rocket(
                type=RocketTypeEnum.default,
                fuel_capacity=ROCKET_CAPACITY_DEFAULT,
                current_fuel=0,
            ),
            Rocket(
                type=RocketTypeEnum.default,
                fuel_capacity=ROCKET_CAPACITY_DEFAULT,
                current_fuel=0,
            ),
        ]
        self.session.add(user)
        return user

    async def create_user_rocket(self, **kwargs) -> Rocket:
        rocket = Rocket(**kwargs)
        self.session.add(rocket)
        return rocket

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

    async def get_referrals(self, telegram_id: int, pagination: PaginatedRequest) -> PaginatedResult[User]:
        stmt = select(User).where(User.referral_from == telegram_id)
        return await self.paginate(stmt=stmt, pagination=pagination, count=User.id)

    async def set_seen(self, telegram_id: int) -> None:
        stmt = update(Rocket).where(Rocket.user_id == telegram_id).values(seen=True)
        await self.session.execute(stmt)
