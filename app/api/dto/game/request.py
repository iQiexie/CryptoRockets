from app.api.dto.base import BaseRequest
from app.db.models import RocketTypeEnum


class LaunchRocket(BaseRequest):
    type: RocketTypeEnum
