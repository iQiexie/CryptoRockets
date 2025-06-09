from app.api.dto.base import BaseResponse
from app.db.models import CurrenciesEnum, RocketSkinEnum, RocketTypeEnum
from app.utils import iota_generator

iota = iota_generator()


class ShopItem(BaseResponse):
    id: int
    description: str
    label: str
    ton_price: float
    xtr_price: float
    token_price: float
    rocket_skin: RocketSkinEnum | None = None
    rocket_type: RocketTypeEnum | None = None
    currency: CurrenciesEnum | None = None
    amount: int | None = None


SHOP_ITEMS = {
    iota(): ShopItem(
        id=iota(),
        description="some_key",
        label="wheel_tickets",
        currency=CurrenciesEnum.wheel,
        amount=1,
        ton_price=1,
        xtr_price=1,
        token_price=1,
    ),
    iota(): ShopItem(
        id=iota(),
        description="some_key",
        label="wheel_tickets",
        currency=CurrenciesEnum.wheel,
        amount=5,
        ton_price=1,
        xtr_price=1,
        token_price=1,
    ),
    iota(): ShopItem(
        id=iota(),
        description="some_key",
        label="wheel_tickets",
        currency=CurrenciesEnum.wheel,
        amount=10,
        ton_price=1,
        xtr_price=1,
        token_price=1,
    ),
    iota(): ShopItem(
        id=iota(),
        description="some_key",
        label="wheel_tickets",
        currency=CurrenciesEnum.wheel,
        amount=25,
        ton_price=1,
        xtr_price=1,
        token_price=1,
    ),
    iota(): ShopItem(
        id=iota(),
        description="some_key",
        label="wheel_tickets",
        currency=CurrenciesEnum.wheel,
        amount=50,
        ton_price=1,
        xtr_price=1,
        token_price=1,
    ),
}
