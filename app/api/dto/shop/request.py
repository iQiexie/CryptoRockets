from datetime import datetime

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
    special: bool = False
    available_until: datetime | None = None


_items = (
    ShopItem(
        id=iota(),
        label="wheel_tickets",
        amount=1,
        item=WheelPrizeEnum.wheel,
        ton_price=0.1,
        xtr_price=25,
        token_price=1,
    ),
    ShopItem(
        id=iota(),
        label="wheel_tickets",
        item=WheelPrizeEnum.wheel,
        amount=3,
        ton_price=0.25,
        xtr_price=60,
        token_price=1,
    ),
    ShopItem(
        id=iota(),
        label="wheel_tickets",
        item=WheelPrizeEnum.wheel,
        amount=10,
        ton_price=0.5,
        xtr_price=150,
        token_price=1,
    ),
    ShopItem(
        id=iota(),
        label="wheel_tickets",
        item=WheelPrizeEnum.super_rocket,
        amount=1,
        ton_price=2,
        xtr_price=500,
        token_price=10000000,
        available_until=datetime(2025, 6, 30, 0, 0, 0),
    ),
    ShopItem(
        id=iota(),
        label="rolls",
        item=WheelPrizeEnum.rolls,
        amount=1,
        ton_price=0.5,
        xtr_price=10000000,
        token_price=10000000,
        
    ),
    ShopItem(
        id=iota(),
        label="gift_withdrawal",
        item=WheelPrizeEnum.gift_withdrawal,
        amount=1,
        ton_price=0.1,
        xtr_price=25,
        token_price=10000000,
    ),
    ShopItem(
        id=iota(),
        label="rolls",
        item=WheelPrizeEnum.rolls,
        amount=1,
        ton_price=1,
        xtr_price=10000000,
        token_price=10000000,
        
    ),
    ShopItem(
        id=iota(),
        label="rolls",
        item=WheelPrizeEnum.rolls,
        amount=1,
        ton_price=2,
        xtr_price=10000000,
        token_price=10000000,
        
    ),
    ShopItem(
        id=iota(),
        label="rolls",
        item=WheelPrizeEnum.rolls,
        amount=1,
        ton_price=3,
        xtr_price=10000000,
        token_price=10000000,
        
    ),
    ShopItem(
        id=iota(),
        label="rolls",
        item=WheelPrizeEnum.rolls,
        amount=1,
        ton_price=4,
        xtr_price=10000000,
        token_price=10000000,
        
    ),
    ShopItem(
        id=iota(),
        label="rolls",
        item=WheelPrizeEnum.rolls,
        amount=1,
        ton_price=5,
        xtr_price=10000000,
        token_price=10000000,
        
    ),
    ShopItem(
        id=iota(),
        label="rolls",
        item=WheelPrizeEnum.rolls,
        amount=1,
        ton_price=10,
        xtr_price=10000000,
        token_price=10000000,
        
    ),
    ShopItem(
        id=iota(),
        label="rolls",
        item=WheelPrizeEnum.rolls,
        amount=1,
        ton_price=20,
        xtr_price=10000000,
        token_price=10000000,
        
    ),
    ShopItem(
        id=iota(),
        label="rolls",
        item=WheelPrizeEnum.rolls,
        amount=1,
        ton_price=50,
        xtr_price=10000000,
        token_price=10000000,
        
    ),
)


SHOP_ITEMS = {i.id: i for i in _items}
