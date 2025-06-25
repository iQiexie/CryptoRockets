from datetime import datetime, timedelta

from pydantic import ConfigDict, Field, computed_field
from pydantic import field_validator
from pydantic_core.core_schema import ValidationInfo

from app.api.dto.base import BaseResponse
from app.config.config import get_config
from app.config.constants import (
    BOT_NAME,
    REFERRAL_PREFIX,
    WEBAPP_NAME,
)
from app.db.models import RocketTypeEnum


config = get_config()


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
    payment_address: str = config.scanner.SCANNER_WALLET
    next_wheel_at: datetime | None = Field(default=None)
    next_wheel_ad_at: datetime | None = Field(default=None)
    next_default_rocket_at: datetime | None = Field(default=None, exclude=True)
    next_offline_rocket_at: datetime | None = Field(default=None, exclude=True)
    next_premium_rocket_at: datetime | None = Field(default=None, exclude=True)
    rolls: dict = Field(default=..., exclude=True)
    boost_balance: int = Field(default=..., exclude=True)
    rich_ads_tasks: int

    rockets: list[RocketResponse]

    @computed_field
    def available_rolls(self) -> dict:
        rolls = [float(i) for i in [
            0.5, 1, 2, 3, 4, 5, 10, 20, 50, 120, 250, 500, 700, 1000, 1200
        ]]

        old_rolls = {float(key): int(value) for key, value in self.rolls.items()}
        new_rolls = {}

        for roll in rolls:
            new_rolls[roll] = old_rolls.get(roll, 0)

        return new_rolls

    @computed_field
    def has_boost(self) -> bool:
        return self.boost_balance > 0

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
