from typing import Annotated

import structlog
from aiogram.types import CallbackQuery
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from app.adapters.base import Adapters
from app.api.dependencies.stubs import dependency_adapters
from app.api.dependencies.stubs import dependency_session_factory
from app.api.dependencies.stubs import placeholder
from app.db.models import GiftUserStatusEnum
from app.services.base.base import BaseService

logger = structlog.stdlib.get_logger()


class BotService(BaseService):
    def __init__(
        self,
        adapters: Annotated[Adapters, Depends(dependency_adapters)],
        session_factory: Annotated[sessionmaker, Depends(dependency_session_factory)],
        session: Annotated[AsyncSession, Depends(placeholder)] = None,
    ):
        super().__init__(session_factory=session_factory, adapters=adapters, session=session)

        self.repo = self.repos.game
        self.adapters = adapters

    @BaseService.single_transaction
    async def gift_view(self, callback: CallbackQuery, gift_id: int) -> None:
        gift = await self.repo.get_gift_user(gift_user_id=gift_id)
        await self.adapters.bot.send_message(
            chat_id=callback.message.chat.id,
            text=(
                f"Коллекция: {gift.collection.name}\n"
                f"Fragment: https://fragment.com/gifts/{gift.collection.slug}?sort=price_asc&filter=sale\n"
            ),
        )

    @BaseService.single_transaction
    async def gift_withdrawn(self, callback: CallbackQuery, gift_id: int) -> None:
        gift = await self.repo.get_gift_for_update(gift_user_id=gift_id)
        await self.repo.update_gift_user(gift_user_id=gift.id, status=GiftUserStatusEnum.withdrawn)

        await self.adapters.bot.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            text=callback.message.text + "\n\n✅ Выведен"
        )

