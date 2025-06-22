from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Roll
from app.db.models import Transaction
from app.db.repos.base.base import BaseRepo


class TransactionRepo(BaseRepo):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session)

    async def create_roll(self, **kwargs) -> Roll:
        model = Roll(**kwargs)
        self.session.add(model)
        return model

    async def create_transaction(self, **kwargs) -> Transaction:
        model = Transaction(**kwargs)
        self.session.add(model)
        return model
