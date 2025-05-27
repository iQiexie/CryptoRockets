from enum import Enum

from pydantic import Field

from app.api.dto.base import BaseResponse


class WheelPrizeEnum(str, Enum):
    premium_rocket = "premium_rocket"
    premium_rocket_full = "premium_rocket_full"
    fuel = "fuel"
    tokens = "tokens"


class WheelPrizeResponse(BaseResponse):
    type: WheelPrizeEnum
    amount: float
    icon: str
    chance: float = Field(exclude=True)


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
        type=WheelPrizeEnum.fuel,
        amount=20,
        icon="NotImplemented",
        chance=10,
    ),
    WheelPrizeResponse(
        type=WheelPrizeEnum.fuel,
        amount=40,
        icon="NotImplemented",
        chance=10,
    ),
    WheelPrizeResponse(
        type=WheelPrizeEnum.fuel,
        amount=60,
        icon="NotImplemented",
        chance=10,
    ),
    WheelPrizeResponse(
        type=WheelPrizeEnum.tokens,
        amount=1_000,
        icon="NotImplemented",
        chance=10,
    ),
    WheelPrizeResponse(
        type=WheelPrizeEnum.tokens,
        amount=2_000,
        icon="NotImplemented",
        chance=10,
    ),
    WheelPrizeResponse(
        type=WheelPrizeEnum.tokens,
        amount=5_000,
        icon="NotImplemented",
        chance=10,
    ),
]
