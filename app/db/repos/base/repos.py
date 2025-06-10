from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repos.ads import AdsRepo
from app.db.repos.game import GameRepo
from app.db.repos.shop import ShopRepo
from app.db.repos.task import TaskRepo
from app.db.repos.transaction import TransactionRepo
from app.db.repos.user import UserRepo
from app.db.repos.user_task import UserTaskRepo


class Repos:
    def __init__(self, session: AsyncSession):
        self.session = session

    @property
    def user(self) -> UserRepo:
        return UserRepo(session=self.session)

    @property
    def task(self) -> TaskRepo:
        return TaskRepo(session=self.session)

    @property
    def game(self) -> GameRepo:
        return GameRepo(session=self.session)

    @property
    def transaction(self) -> TransactionRepo:
        return TransactionRepo(session=self.session)

    @property
    def user_task(self) -> UserTaskRepo:
        return UserTaskRepo(session=self.session)

    @property
    def shop(self) -> ShopRepo:
        return ShopRepo(session=self.session)

    @property
    def ads(self) -> AdsRepo:
        return AdsRepo(session=self.session)
