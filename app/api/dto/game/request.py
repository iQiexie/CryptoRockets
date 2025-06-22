from app.api.dto.base import BaseRequest
from app.db.models import RocketSkinEnum


class UpdateRocketRequest(BaseRequest):
    skin: RocketSkinEnum


class MakeBetRequest(BaseRequest):
    amount: float
