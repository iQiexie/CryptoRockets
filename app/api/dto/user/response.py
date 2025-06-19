from datetime import datetime, timedelta

from pydantic import ConfigDict, Field, computed_field
from pydantic import field_validator
from pydantic_core.core_schema import ValidationInfo

from app.api.dto.base import BaseResponse
from app.config.constants import (
    BOT_NAME,
    REFERRAL_PREFIX,
    WEBAPP_NAME,
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
    next_wheel_at: datetime | None = Field(default=None)
    next_wheel_ad_at: datetime | None = Field(default=None)
    next_default_rocket_at: datetime | None = Field(default=None, exclude=True)
    next_offline_rocket_at: datetime | None = Field(default=None, exclude=True)
    next_premium_rocket_at: datetime | None = Field(default=None, exclude=True)
    rolls: dict = Field(default=..., exclude=True)

    rockets: list[RocketResponse]

    @computed_field
    def available_rolls(self) -> dict:
        new_rolls = {}
        for key, value in self.rolls.items():
            if value:
                new_rolls[key] = value

        return new_rolls

    @computed_field
    def referral(self) -> str:
        return f"https://t.me/{BOT_NAME}/{WEBAPP_NAME}?startapp={REFERRAL_PREFIX}{self.telegram_id}"

    @field_validator("next_wheel_at", "next_wheel_ad_at", mode="before")
    @classmethod
    def validate_next(cls, v: datetime) -> datetime | None:
        if v <= datetime.utcnow():
            return None

        return v

    @computed_field
    def next_default_rocket_in(self) -> timedelta | None:
        if RocketTypeEnum.default in [rocket.type for rocket in self.rockets]:
            return None

        if self.next_default_rocket_at <= datetime.utcnow():
            return None

        return self.next_default_rocket_at

    @computed_field
    def next_offline_rocket_in(self) -> timedelta | None:
        if RocketTypeEnum.offline in [rocket.type for rocket in self.rockets]:
            return None

        if self.next_offline_rocket_at <= datetime.utcnow():
            return None

        return self.next_offline_rocket_at

    @computed_field
    def next_premium_rocket_in(self) -> timedelta | None:
        if RocketTypeEnum.premium in [rocket.type for rocket in self.rockets]:
            return None

        if self.next_premium_rocket_at <= datetime.utcnow():
            return None

        return self.next_premium_rocket_at


class PublicUserResponse(BaseResponse):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    tg_photo_url: str | None = Field(default=None)
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
