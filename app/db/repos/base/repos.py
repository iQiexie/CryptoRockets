from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repos.game import GameRepo
from app.db.repos.transaction import TransactionRepo
from app.db.repos.user import UserRepo


class Repos:
    def __init__(self, session: AsyncSession):
        self.session = session

    @property
    def user(self) -> UserRepo:
        return UserRepo(session=self.session)

    @property
    def game(self) -> GameRepo:
        return GameRepo(session=self.session)

    @property
    def transaction(self) -> TransactionRepo:
        return TransactionRepo(session=self.session)
