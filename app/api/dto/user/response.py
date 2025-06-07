import math

from pydantic import ConfigDict, Field, computed_field
from pydantic import field_validator

from app.api.dto.base import BaseResponse
from app.config.constants import BOT_NAME
from app.config.constants import REFERRAL_PREFIX
from app.config.constants import WEBAPP_NAME
from app.db.models import Rocket
from app.db.models import RocketSkinEnum, RocketTypeEnum


class RocketResponse(BaseResponse):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: int
    frontend_id: str | None = Field(default=None)
    type: RocketTypeEnum
    fuel_capacity: int
    current_fuel: int
    enabled: bool
    skins: list[RocketSkinEnum]
    current_skin: RocketSkinEnum

    @field_validator("frontend_id", mode="before")
    @classmethod
    def validate_frontend_id(cls, v: str | None, values: dict) -> str:
        if v is None:
            return str(values.get("id"))
        return v


class UserResponse(BaseResponse):
    id: int
    telegram_id: int
    ton_balance: float
    usdt_balance: float
    token_balance: float
    wheel_balance: float

    rockets: list[RocketResponse]

    @field_validator("rockets", mode="before")
    @classmethod
    def validate_rockets(cls, v: list[Rocket]) -> list[RocketResponse]:
        resp = []

        for rocket in v:
            if rocket.current_fuel <= rocket.fuel_capacity:
                resp.append(RocketResponse.model_validate(rocket))
                continue

            rocket_count = math.ceil(rocket.current_fuel / rocket.fuel_capacity)
            for i in range(rocket_count):
                i += 1

                if rocket.fuel_capacity * i <= rocket.current_fuel:
                    current_fuel = rocket.fuel_capacity
                else:
                    current_fuel = rocket.current_fuel - rocket.fuel_capacity * (i - 1)

                temp_rocket = RocketResponse.model_validate(rocket)
                temp_rocket.current_fuel = current_fuel
                temp_rocket.frontend_id = f"{rocket.id}_{i}"
                resp.append(temp_rocket)

        return resp

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
