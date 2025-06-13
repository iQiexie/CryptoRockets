from datetime import datetime
from datetime import timedelta
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
from app.api.dto.ads.request import AdCheckRequest, AdRequest
from app.api.dto.ads.response import VerifyAdResponse
from app.api.dto.user.response import RocketResponse
from app.api.dto.user.response import UserResponse
from app.api.exceptions import ClientError
from app.config.constants import WHEEL_AD_TIMEOUT
from app.db.models import AdStatusEnum, Advert, Rocket
from app.db.models import CurrenciesEnum
from app.db.models import TransactionTypeEnum
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
    def xor_encrypt(data: str, key: str) -> str:
        # SEE https://chatgpt.com/share/6847287d-8eec-8006-b40b-e96a140bfcc2

        data_bytes = data.encode()
        key_bytes = key.encode()
        encrypted = bytes(b ^ key_bytes[i % len(key_bytes)] for i, b in enumerate(data_bytes))
        return encrypted.hex()

    @BaseService.single_transaction
    async def create_ad(self, data: AdRequest, current_user: WebappData) -> Advert:
        ad = await self.repo.create_ad(
            user_id=current_user.telegram_id,
            provider=data.provider,
            status=AdStatusEnum.created,
            rocket_id=data.rocket_id,
            wheel_amount=1 if data.for_wheel else 0,
        )

        return ad

    @BaseService.single_transaction
    async def verify_offer(self, current_user: WebappData, data: AdCheckRequest) -> VerifyAdResponse:
        payload, hash_ = data.token.split("-")
        actual_hash_ = self.xor_encrypt(data=payload, key=f"rocket_type_{current_user.telegram_id}_{data.id}")

        if hash_ != actual_hash_:
            raise ClientError(message="Offer not found", status_code=status.HTTP_404_NOT_FOUND)

        ad = await self.repo.get_ad(ad_id=data.id)
        if not ad:
            raise ClientError(message="Offer not found", status_code=status.HTTP_404_NOT_FOUND)

        user = None
        rocket = None

        if ad.rocket_id:
            rocket = await self.repos.game.get_rocket_for_update(
                telegram_id=current_user.telegram_id,
                rocket_id=ad.rocket_id,
            )

            r = await self.repos.game.update_rocket(rocket_id=rocket.id, current_fuel=rocket.current_fuel + 1)
            await self.repo.update_ad(ad_id=data.id, status=AdStatusEnum.watched)
            await self.session.refresh(r)
            await self.session.commit()
            user = await self.repos.user.get_user_by_telegram_id(telegram_id=current_user.telegram_id)
            rocket = r
        elif ad.wheel_amount:
            await self.repos.user.update_user(
                telegram_id=current_user.telegram_id,
                next_wheel_ad_at=datetime.utcnow() + timedelta(minutes=WHEEL_AD_TIMEOUT),
            )
            resp = await self.services.transaction.change_user_balance(
                telegram_id=current_user.telegram_id,
                currency=CurrenciesEnum.wheel,
                amount=ad.wheel_amount,
                tx_type=TransactionTypeEnum.ads
            )

            user = resp.user

        return VerifyAdResponse(
            user=UserResponse.model_validate(user) if user else None,
            rocket=RocketResponse.model_validate(rocket) if rocket else None,
        )
