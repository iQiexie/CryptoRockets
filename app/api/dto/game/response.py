from pydantic import Field

from app.api.dto.base import BaseResponse
from app.api.dto.user.response import PublicUserResponse
from app.db.models import WheelPrizeEnum
from app.utils import iota_generator

iota = iota_generator()


class WheelPrizeResponse(BaseResponse):
    id: int
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
    usdt: float | None = None
    ton: float | None = None
    token: float | None = None


WHEEL_PRIZES = [
    WheelPrizeResponse(
        id=iota(),
        type=WheelPrizeEnum.default_rocket,
        amount=1,
        icon="NotImplemented",
        chance=10,
    ),
    WheelPrizeResponse(
        id=iota(),
        type=WheelPrizeEnum.offline_rocket,
        amount=1,
        icon="NotImplemented",
        chance=10,
    ),
    WheelPrizeResponse(
        id=iota(),
        type=WheelPrizeEnum.premium_rocket,
        amount=1,
        icon="NotImplemented",
        chance=10,
    ),
    WheelPrizeResponse(
        id=iota(),
        type=WheelPrizeEnum.wheel,
        amount=1,
        icon="NotImplemented",
        chance=100,
    ),
    WheelPrizeResponse(
        id=iota(),
        type=WheelPrizeEnum.usdt,
        amount=100,
        icon="NotImplemented",
        chance=0,
    ),
    WheelPrizeResponse(
        id=iota(),
        type=WheelPrizeEnum.usdt,
        amount=1,
        icon="NotImplemented",
        chance=10,
    ),
    WheelPrizeResponse(
        id=iota(),
        type=WheelPrizeEnum.ton,
        amount=1,
        icon="NotImplemented",
        chance=10,
    ),
    WheelPrizeResponse(
        id=iota(),
        type=WheelPrizeEnum.token,
        amount=1_000,
        icon="NotImplemented",
        chance=10,
    ),
    WheelPrizeResponse(
        id=iota(),
        type=WheelPrizeEnum.token,
        amount=5_000,
        icon="NotImplemented",
        chance=10,
    ),
    WheelPrizeResponse(
        id=iota(),
        type=WheelPrizeEnum.ton,
        amount=50,
        icon="NotImplemented",
        chance=0,
    ),
]
