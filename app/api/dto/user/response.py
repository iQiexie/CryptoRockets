from pydantic import ConfigDict, Field, computed_field

from app.api.dto.base import BaseResponse
from app.config.constants import BOT_NAME
from app.config.constants import REFERRAL_PREFIX
from app.config.constants import WEBAPP_NAME
from app.db.models import RocketSkinEnum, RocketTypeEnum


class RocketResponse(BaseResponse):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: int
    type: RocketTypeEnum
    fuel_capacity: int
    current_fuel: int
    enabled: bool


class UserResponse(BaseResponse):
    id: int
    telegram_id: int
    ton_balance: float
    usdt_balance: float
    token_balance: float
    wheel_balance: float

    rockets: list[RocketResponse]

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
