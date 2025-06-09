from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query
from starlette import status

from app.api.dependencies.auth import get_current_user
from app.api.dto.shop.request import SHOP_ITEMS, ShopItem
from app.api.dto.shop.response import UrlResponse
from app.services.dto.auth import WebappData
from app.services.dto.shop import PaymentCallbackDTO
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
    payment_method: Literal["ton", "xtr", "token"] = Query(default="xtr"),
) -> UrlResponse:
    return await service.get_invoice_url(
        current_user=current_user,
        shop_item_id=shop_item_id,
        payment_method=payment_method,
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

