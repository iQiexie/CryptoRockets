from pydantic import Field

from app.db.models import CurrenciesEnum
from app.init.base_models import BaseModel


class PaymentCallbackDTO(BaseModel):
    telegram_id: int
    item_id: int
    amount: float
    usd_amount: float
    currency: CurrenciesEnum
    external_id: str
    callback_data: dict
    fee: float | None = Field(default=None)
