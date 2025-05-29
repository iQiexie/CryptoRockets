from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Invoice
from app.db.repos.base.base import BaseRepo


class ShopRepo(BaseRepo):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session)

    async def create_invoice(self, **kwargs) -> Invoice:
        model = Invoice(**kwargs)
        self.session.add(model)
        return model
