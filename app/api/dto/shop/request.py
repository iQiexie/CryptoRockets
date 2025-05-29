from app.api.dto.base import BaseResponse
from app.db.models import CurrenciesEnum


class ShopItem(BaseResponse):
    id: int
    description: str
    label: str
    price: int | None = None
    rocket_id: int | None = None
    currency: CurrenciesEnum | None = None
    amount: int | None = None


SHOP_ITEMS = {
    1: ShopItem(id=1, price=50, description="some_key", label="some_translation_key", amount=1000),
}
