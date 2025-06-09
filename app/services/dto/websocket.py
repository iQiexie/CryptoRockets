from enum import Enum

from app.init.base_models import BaseModel


class WsEventsEnum(str, Enum):
    user_notification = "user_notification"
    purchase = "purchase"


class WSMessage(BaseModel):
    event: WsEventsEnum
    telegram_id: int
    message: dict
