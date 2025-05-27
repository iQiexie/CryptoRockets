from pydantic import ConfigDict

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
