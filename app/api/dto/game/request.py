from app.api.dto.base import BaseRequest
from app.db.models import RocketSkinEnum
from app.db.models import RocketTypeEnum


class LaunchRocket(BaseRequest):
    type: RocketTypeEnum


class UpdateRocketRequest(BaseRequest):
    skin: RocketSkinEnum
