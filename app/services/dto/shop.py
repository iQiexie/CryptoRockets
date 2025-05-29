from app.db.models import CurrenciesEnum
from app.init.base_models import BaseModel


class XTRPaymentCallbackDTO(BaseModel):
    telegram_id: int
    item_id: int
    amount: int
    usd_amount: float
    currency: CurrenciesEnum
    external_id: str
    callback_data: dict
