from datetime import datetime

from pydantic import Field
from pydantic import RootModel

from app.api.dto.base import BaseResponse
from app.api.dto.user.response import PublicUserResponse
from app.api.dto.user.response import RocketResponse
from app.api.dto.user.response import UserResponse
from app.db.models import GiftUserStatusEnum
from app.db.models import WheelPrizeEnum
from app.utils import iota_generator

iota = iota_generator()


class CollectionResponse(BaseResponse):
    id: int
    name: str
    image: str


class GiftBetResponse(BaseResponse):
    probability: float
    is_boost: bool
    collection: CollectionResponse | None = None


class BetConfigResponse(BaseResponse, RootModel[dict[float, list[GiftBetResponse]]]):
    pass


class MakeBetResponse(BaseResponse):
    collection: CollectionResponse | None = None
    user: UserResponse


class GiftUserWithdrawResponse(BaseResponse):
    id: int
    created_at: datetime
    status: GiftUserStatusEnum


class GiftUserResponse(GiftUserWithdrawResponse):
    collection: CollectionResponse


class _GiftAttribute(BaseResponse):
    name: str
    rarity: float


class _GiftMetaResponse(BaseResponse):
    model: _GiftAttribute
    pattern: _GiftAttribute
    backdrop: _GiftAttribute


class LatestGiftResponse(BaseResponse):
    gift_id: str
    gift_id_ton: str
    image: str
    collection: CollectionResponse
    meta: _GiftMetaResponse


class WheelPrizeResponse(BaseResponse):
    id: int
    type: WheelPrizeEnum
    amount: float
    icon: str
    chance: float = Field(exclude=True)
    user: UserResponse | None = None
    rocket: RocketResponse | None = None


class LatestWheelPrizeResponse(BaseResponse):
    type: WheelPrizeEnum
    amount: float
    icon: str
    user: PublicUserResponse


class LaunchResponse(BaseResponse):
    usdt: float | None = None
    ton: float | None = None
    token: float | None = None
    user: UserResponse | None = None


WHEEL_PRIZES = [
    WheelPrizeResponse(
        id=iota(),
        type=WheelPrizeEnum.default_rocket,
        amount=1,
        icon="NotImplemented",
        chance=20,
    ),
    WheelPrizeResponse(
        id=iota(),
        type=WheelPrizeEnum.offline_rocket,
        amount=1,
        icon="NotImplemented",
        chance=19,
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
        chance=5,
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
        chance=4,
    ),
    WheelPrizeResponse(
        id=iota(),
        type=WheelPrizeEnum.ton,
        amount=1,
        icon="NotImplemented",
        chance=2,
    ),
    WheelPrizeResponse(
        id=iota(),
        type=WheelPrizeEnum.token,
        amount=500,
        icon="NotImplemented",
        chance=20,
    ),
    WheelPrizeResponse(
        id=iota(),
        type=WheelPrizeEnum.token,
        amount=1_500,
        icon="NotImplemented",
        chance=20,
    ),
    WheelPrizeResponse(
        id=iota(),
        type=WheelPrizeEnum.ton,
        amount=50,
        icon="NotImplemented",
        chance=0,
    ),
]
