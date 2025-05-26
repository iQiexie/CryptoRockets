from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repos.user import UserRepo


class Repos:
    def __init__(self, session: AsyncSession):
        self.session = session

    @property
    def user(self) -> UserRepo:
        return UserRepo(session=self.session)
