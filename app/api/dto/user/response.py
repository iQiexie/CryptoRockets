from datetime import datetime, timedelta

from pydantic import ConfigDict, Field, computed_field

from app.api.dto.base import BaseResponse
from app.config.constants import (
    BOT_NAME,
    REFERRAL_PREFIX,
    ROCKET_TIMEOUT_DEFAULT,
    ROCKET_TIMEOUT_OFFLINE,
    ROCKET_TIMEOUT_PREMIUM,
    WEBAPP_NAME,
    WHEEL_TIMEOUT,
)
from app.db.models import RocketTypeEnum


class RocketResponse(BaseResponse):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: int
    type: RocketTypeEnum
    fuel_capacity: int
    current_fuel: int
    enabled: bool
    seen: bool


class UserResponse(BaseResponse):
    id: int
    telegram_id: int
    ton_balance: float
    usdt_balance: float
    token_balance: float
    wheel_balance: float
    payment_address: str = "UQA824RWvHtNCPlMp-mRA1u3geuf98zyt4VZjXdGAZCAwDHC"
    wheel_received: datetime = Field(default=..., exclude=True)
    default_rocket_received: datetime = Field(default=..., exclude=True)
    offline_rocket_received: datetime = Field(default=..., exclude=True)
    premium_rocket_received: datetime = Field(default=..., exclude=True)

    rockets: list[RocketResponse]

    @computed_field()
    def next_wheel_at(self) -> datetime:
        return self.wheel_received + timedelta(minutes=WHEEL_TIMEOUT)

    @computed_field()
    def next_default_rocket_at(self) -> datetime | None:
        if RocketTypeEnum.default in [rocket.type for rocket in self.rockets]:
            return None

        return self.default_rocket_received + timedelta(minutes=ROCKET_TIMEOUT_DEFAULT)

    @computed_field()
    def next_offline_rocket_at(self) -> datetime | None:
        if RocketTypeEnum.offline in [rocket.type for rocket in self.rockets]:
            return None

        return self.offline_rocket_received + timedelta(minutes=ROCKET_TIMEOUT_OFFLINE)

    @computed_field()
    def next_premium_rocket_at(self) -> datetime | None:
        if RocketTypeEnum.premium in [rocket.type for rocket in self.rockets]:
            return None

        return self.premium_rocket_received + timedelta(minutes=ROCKET_TIMEOUT_PREMIUM)

    @computed_field
    def referral(self) -> str:
        return f"https://t.me/{BOT_NAME}/{WEBAPP_NAME}?startapp={REFERRAL_PREFIX}{self.telegram_id}"


class PublicUserResponse(BaseResponse):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    tg_photo_url: str
    tg_is_premium: bool | None = Field(default=False)

    tg_username: str | None = Field(default=None, exclude=True)
    tg_first_name: str | None = Field(default=None, exclude=True)
    tg_last_name: str | None = Field(default=None, exclude=True)

    @computed_field
    def username(self) -> str:
        username = self.tg_username

        if not username:
            username = (self.tg_first_name or "") + (self.tg_last_name or "")

        return username
