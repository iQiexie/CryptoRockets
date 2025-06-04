from pydantic import Field

from app.api.dto.base import BaseResponse
from app.api.dto.user.response import PublicUserResponse
from app.db.models import WheelPrizeEnum


class WheelPrizeResponse(BaseResponse):
    type: WheelPrizeEnum
    amount: float
    icon: str
    chance: float = Field(exclude=True)


class LatestWheelPrizeResponse(BaseResponse):
    type: WheelPrizeEnum
    amount: float
    icon: str
    user: PublicUserResponse


class LaunchResponse(BaseResponse):
    new_balance_usdt: float | None = None
    new_balance_ton: float | None = None


WHEEL_PRIZES = [
    WheelPrizeResponse(
        type=WheelPrizeEnum.premium_rocket,
        amount=1,
        icon="NotImplemented",
        chance=10,
    ),
    WheelPrizeResponse(
        type=WheelPrizeEnum.premium_rocket_full,
        amount=1,
        icon="NotImplemented",
        chance=10,
    ),
    WheelPrizeResponse(
        type=WheelPrizeEnum.usdt,
        amount=20,
        icon="NotImplemented",
        chance=10,
    ),
    WheelPrizeResponse(
        type=WheelPrizeEnum.ton,
        amount=40,
        icon="NotImplemented",
        chance=10,
    ),
    WheelPrizeResponse(
        type=WheelPrizeEnum.wheel,
        amount=60,
        icon="NotImplemented",
        chance=10,
    ),
    WheelPrizeResponse(
        type=WheelPrizeEnum.token,
        amount=1_000,
        icon="NotImplemented",
        chance=10,
    ),
    WheelPrizeResponse(
        type=WheelPrizeEnum.token,
        amount=2_000,
        icon="NotImplemented",
        chance=10,
    ),
    WheelPrizeResponse(
        type=WheelPrizeEnum.token,
        amount=5_000,
        icon="NotImplemented",
        chance=10,
    ),
]
