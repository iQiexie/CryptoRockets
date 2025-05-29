from pydantic import ConfigDict, Field, computed_field

from app.api.dto.base import BaseResponse
from app.db.models import RocketTypeEnum


class RocketResponse(BaseResponse):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    type: RocketTypeEnum
    fuel_capacity: int
    current_fuel: int
    enabled: bool


class UserResponse(BaseResponse):
    id: int
    ton_balance: float
    usdt_balance: float
    token_balance: float

    rockets: list[RocketResponse]


class PublicUserResponse(BaseResponse):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    tg_photo_url: str

    tg_username: str | None = Field(default=None, exclude=True)
    tg_first_name: str | None = Field(default=None, exclude=True)
    tg_last_name: str | None = Field(default=None, exclude=True)

    @computed_field
    def username(self) -> str:
        username = self.tg_username

        if not username:
            username = (self.tg_first_name or "") + (self.tg_last_name or "")

        return username
