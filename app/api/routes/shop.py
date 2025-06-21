from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query
from fastapi import Path
from starlette import status

from app.api.dependencies.auth import get_current_user
from app.api.dto.shop.request import SHOP_ITEMS, ShopItem
from app.api.dto.shop.response import UrlResponse
from app.db.models import WheelPrizeEnum
from app.services.dto.auth import WebappData
from app.services.shop import ShopService

router = APIRouter(tags=["Shop"])


@router.get(
    path="/shop/invoice",
    status_code=status.HTTP_200_OK,
    response_model=UrlResponse,
)
async def get_invoice_url(
    current_user: Annotated[WebappData, Depends(get_current_user)],
    service: Annotated[ShopService, Depends()],
    shop_item_id: int = Query(...),
    gift_id: int | None = Query(default=None),
    amount: int = Query(default=1),
    payment_method: Literal["ton", "xtr"] = Query(default="xtr"),
) -> UrlResponse:
    return await service.get_invoice_url(
        current_user=current_user,
        shop_item_id=shop_item_id,
        payment_method=payment_method,
        amount=amount,
        gift_id=gift_id,
    )


@router.get(
    path="/shop/invoice/withdraw/{gift_id}",
    status_code=status.HTTP_200_OK,
    response_model=UrlResponse,
)
async def get_invoice_url_withdraw(
    current_user: Annotated[WebappData, Depends(get_current_user)],
    service: Annotated[ShopService, Depends()],
    gift_id: int = Path(default=...),
    payment_method: Literal["ton", "xtr"] = Query(default="xtr"),
) -> UrlResponse:
    shop_item_id = [key for key, value in SHOP_ITEMS.items() if value.item == WheelPrizeEnum.gift_withdrawal][0]

    return await service.get_invoice_url(
        current_user=current_user,
        shop_item_id=shop_item_id,
        payment_method=payment_method,
        amount=1,
        gift_id=gift_id,
    )


@router.get(
    path="/shop/invoice/rolls",
    status_code=status.HTTP_200_OK,
    response_model=UrlResponse,
)
async def get_invoice_url_rolls(
    current_user: Annotated[WebappData, Depends(get_current_user)],
    service: Annotated[ShopService, Depends()],
    rolls_amount: float = Query(default=...),
    rolls_cont: int = Query(default=...),
    payment_method: Literal["ton"] = Query(default="ton"),
) -> UrlResponse:
    shop_item_id = [
        key
        for key, value in SHOP_ITEMS.items()
        if value.ton_price == rolls_amount and value.item == WheelPrizeEnum.rolls
    ][0]

    return await service.get_invoice_url(
        current_user=current_user,
        shop_item_id=shop_item_id,
        payment_method=payment_method,
        amount=rolls_cont,
    )


@router.get(
    path="/shop/item",
    status_code=status.HTTP_200_OK,
    response_model=list[ShopItem],
)
async def get_shop_items(
    current_user: Annotated[WebappData, Depends(get_current_user)],
    service: Annotated[ShopService, Depends()],
) -> list[ShopItem]:
    resp = []
    for i in SHOP_ITEMS.values():
        i.label = service.adapters.i18n.t(i.label, current_user.language_code)
        resp.append(i)

    return resp
