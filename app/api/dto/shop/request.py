from app.api.dto.base import BaseResponse
from app.db.models import CurrenciesEnum
from app.db.models import RocketSkinEnum
from app.db.models import RocketTypeEnum


class ShopItem(BaseResponse):
    id: int
    description: str
    label: str
    price: int | None = None
    rocket_skin: RocketSkinEnum | None = None
    rocket_type: RocketTypeEnum | None = None
    currency: CurrenciesEnum | None = None
    amount: int | None = None


SHOP_ITEMS = {
    1: ShopItem(
        id=1,
        price=50,
        description="some_key",
        label="some_translation_key",
        currency=CurrenciesEnum.token,
        amount=1000,
    ),
    2: ShopItem(
        id=2,
        price=50,
        description="some_key",
        label="some_translation_key",
        rocket_skin=RocketSkinEnum.wood,
        rocket_type=RocketTypeEnum.default,
    ),
}
