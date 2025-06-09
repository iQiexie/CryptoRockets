from app.api.dto.base import BaseRequest
from app.db.models import WheelPrizeEnum


class AdRequest(BaseRequest):
    provider: str
    rocket_id: int


class AdCheckRequest(BaseRequest):
    id: int
    token: str
