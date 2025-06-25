from sqlalchemy import or_
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Advert
from app.db.repos.base.base import BaseRepo


class AdsRepo(BaseRepo):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session)

    async def create_ad(self, **kwargs) -> Advert:
        model = Advert(**kwargs)
        self.session.add(model)
        return model

    async def update_ad(self, ad_id: int, **kwargs) -> Advert:
        return await self.update(Advert, Advert.id == ad_id, **kwargs)

    async def get_ad(self, ad_id: int, token: str) -> Advert | None:
        stmt = select(Advert).where(Advert.id == ad_id, or_(Advert.token != token, Advert.token.is_(None)))
        query = await self.session.execute(stmt)
        return query.scalar_one_or_none()
