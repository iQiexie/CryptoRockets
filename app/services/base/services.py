from typing import TYPE_CHECKING

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.adapters.base import Adapters

if TYPE_CHECKING:
    from app.services.auth import AuthService
    from app.services.game import GameService
    from app.services.shop import ShopService
    from app.services.task import TaskService
    from app.services.transaction import TransactionService
    from app.services.user import UserService
    from app.services.user_task import UserTaskService
    from app.services.websocket import WebsocketService
    from app.services.ads import AdsService


class Services:
    def __init__(
        self,
        session_factory: sessionmaker,
        adapters: Adapters,
        session: AsyncSession | None = None,
        engine: AsyncEngine | None = None,
    ):
        self._session = session
        self.adapters = adapters
        self.session_factory = session_factory
        self.engine = engine

    @property
    def session(self) -> AsyncSession:
        if self._session:
            return self._session

        self._session = self.session_factory()
        return self._session

    @property
    def auth(self) -> "AuthService":
        from app.services.auth import AuthService

        return AuthService(session_factory=self.session_factory, adapters=self.adapters, session=self.session)

    @property
    def websocket(self) -> "WebsocketService":
        from app.services.websocket import WebsocketService

        return WebsocketService(session_factory=self.session_factory, adapters=self.adapters, session=self.session)

    @property
    def task(self) -> "TaskService":
        from app.services.task import TaskService

        return TaskService(session_factory=self.session_factory, adapters=self.adapters, session=self.session)

    @property
    def user(self) -> "UserService":
        from app.services.user import UserService

        return UserService(session_factory=self.session_factory, adapters=self.adapters, session=self.session)

    @property
    def game(self) -> "GameService":
        from app.services.game import GameService

        return GameService(session_factory=self.session_factory, adapters=self.adapters, session=self.session)

    @property
    def transaction(self) -> "TransactionService":
        from app.services.transaction import TransactionService

        return TransactionService(session_factory=self.session_factory, adapters=self.adapters, session=self.session)

    @property
    def user_task(self) -> "UserTaskService":
        from app.services.user_task import UserTaskService

        return UserTaskService(session_factory=self.session_factory, adapters=self.adapters, session=self.session)

    @property
    def shop(self) -> "ShopService":
        from app.services.shop import ShopService

        return ShopService(session_factory=self.session_factory, adapters=self.adapters, session=self.session)

    @property
    def ads(self) -> "AdsService":
        from app.services.ads import AdsService

        return AdsService(session_factory=self.session_factory, adapters=self.adapters, session=self.session)
