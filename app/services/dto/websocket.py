from enum import Enum

from app.init.base_models import BaseModel


class WsEventsEnum(str, Enum):
    user_notification = "user_notification"
    purchase = "purchase"
    roll_purchase = "roll_purchase"
    gift_withdrawal = "gift_withdrawal"


class WSMessage(BaseModel):
    event: WsEventsEnum
    telegram_id: int
    message: dict
