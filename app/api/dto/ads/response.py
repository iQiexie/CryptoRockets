from app.api.dto.base import BaseResponse
from app.api.dto.user.response import RocketResponse
from app.api.dto.user.response import UserResponse


class AdsResponse(BaseResponse):
    id: int


class VerifyAdResponse(BaseResponse):
    user: UserResponse | None = None
    rocket: RocketResponse | None = None
