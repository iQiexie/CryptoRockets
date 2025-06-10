from typing import Annotated
import structlog
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from starlette import status

from app.adapters.base import Adapters
from app.api.dependencies.stubs import (
    dependency_adapters,
    dependency_session_factory,
    placeholder,
)
from app.api.dto.ads.request import AdCheckRequest
from app.api.dto.ads.request import AdRequest
from app.api.exceptions import ClientError
from app.db.models import AdStatusEnum
from app.db.models import Advert
from app.db.models import Rocket
from app.services.base.base import BaseService
from app.services.dto.auth import WebappData

logger = structlog.stdlib.get_logger()


class AdsService(BaseService):
    def __init__(
        self,
        adapters: Annotated[Adapters, Depends(dependency_adapters)],
        session_factory: Annotated[sessionmaker, Depends(dependency_session_factory)],
        session: Annotated[AsyncSession, Depends(placeholder)] = None,
    ):
        super().__init__(session_factory=session_factory, adapters=adapters, session=session)

        self.repo = self.repos.ads
        self.adapters = adapters

    @staticmethod
    def xor_encrypt(data: str, key: str) -> bytes:
        # SEE https://chatgpt.com/share/6847287d-8eec-8006-b40b-e96a140bfcc2

        data_bytes = data.encode()
        key_bytes = key.encode()
        encrypted = bytes(b ^ key_bytes[i % len(key_bytes)] for i, b in enumerate(data_bytes))
        return encrypted

    @BaseService.single_transaction
    async def create_ad(self, data: AdRequest, current_user: WebappData) -> Advert:
        ad = await self.repo.create_ad(
            user_id=current_user.telegram_id,
            provider=data.provider,
            status=AdStatusEnum.created,
            rocket_id=data.rocket_id,
        )

        return ad

    @BaseService.single_transaction
    async def verify_offer(self, current_user: WebappData, data: AdCheckRequest) -> Rocket:
        payload, hash_ = data.token.split("-")
        actual_hash_ = self.xor_encrypt(
            data=payload,
            key=f'rocket_type_{current_user.telegram_id}_{data.id}'
        ).hex()

        if hash_ != actual_hash_:
            raise ClientError(message="Offer not found", status_code=status.HTTP_404_NOT_FOUND)

        ad = await self.repo.get_ad(ad_id=data.id)
        if not ad:
            raise ClientError(message="Offer not found", status_code=status.HTTP_404_NOT_FOUND)

        rocket = await self.repos.game.get_rocket_for_update(
            telegram_id=current_user.telegram_id,
            rocket_id=ad.rocket_id,
        )

        r = await self.repos.game.update_rocket(rocket_id=rocket.id, current_fuel=rocket.current_fuel + 1)
        await self.repo.update_ad(ad_id=data.id, status=AdStatusEnum.watched)
        await self.session.refresh(r)

        return r
