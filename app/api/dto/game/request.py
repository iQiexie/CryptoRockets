from app.api.dto.base import BaseRequest
from app.db.models import RocketSkinEnum, RocketTypeEnum


class LaunchRocket(BaseRequest):
    type: RocketTypeEnum


class UpdateRocketRequest(BaseRequest):
    skin: RocketSkinEnum
