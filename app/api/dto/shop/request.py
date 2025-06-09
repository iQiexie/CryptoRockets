from app.api.dto.base import BaseResponse
from app.db.models import WheelPrizeEnum
from app.utils import iota_generator

iota = iota_generator()


class ShopItem(BaseResponse):
    id: int
    label: str
    item: WheelPrizeEnum
    amount: int
    ton_price: float
    xtr_price: float
    token_price: float


_items = (
    ShopItem(
        id=iota(),
        label="wheel_tickets",
        amount=1,
        item=WheelPrizeEnum.wheel,
        ton_price=0.1,
        xtr_price=1,
        token_price=1,
    ),
    ShopItem(
        id=iota(),
        label="wheel_tickets",
        item=WheelPrizeEnum.wheel,
        amount=3,
        ton_price=0.01,
        xtr_price=1,
        token_price=1,
    ),
    ShopItem(
        id=iota(),
        label="wheel_tickets",
        item=WheelPrizeEnum.wheel,
        amount=10,
        ton_price=1,
        xtr_price=1,
        token_price=1,
    ),
    ShopItem(
        id=iota(),
        label="wheel_tickets",
        item=WheelPrizeEnum.super_rocket,
        amount=1,
        ton_price=10,
        xtr_price=10,
        token_price=10,
    ),
    ShopItem(
        id=iota(),
        label="wheel_tickets",
        item=WheelPrizeEnum.mega_rocket,
        amount=1,
        ton_price=10,
        xtr_price=10,
        token_price=10,
    ),
    ShopItem(
        id=iota(),
        label="wheel_tickets",
        item=WheelPrizeEnum.ultra_rocket,
        amount=1,
        ton_price=10,
        xtr_price=10,
        token_price=10,
    ),
)


SHOP_ITEMS = {i.id: i for i in _items}
