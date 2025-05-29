from typing import Annotated

from aiogram.types import SuccessfulPayment
from fastapi import APIRouter, Depends
from redis.commands.search.query import Query
from starlette import status

from app.api.dependencies.auth import get_current_user
from app.api.dto.shop.request import SHOP_ITEMS, ShopItem
from app.api.dto.shop.response import UrlResponse
from app.services.dto.auth import WebappData
from app.services.dto.shop import XTRPaymentCallbackDTO
from app.services.shop import ShopService

router = APIRouter(tags=["Shop"])


@router.post(
    path="/shop/invoice",
    status_code=status.HTTP_200_OK,
    response_model=UrlResponse,
)
async def get_invoice_url(
    current_user: Annotated[WebappData, Depends(get_current_user)],
    service: Annotated[ShopService, Depends()],
    shop_item_id: int = Query(...),
) -> UrlResponse:
    return await service.get_invoice_url(shop_item_id=shop_item_id, current_user=current_user)


@router.get(
    path="/shop/item",
    status_code=status.HTTP_200_OK,
    response_model=list[ShopItem],
)
async def get_shop_items() -> list[ShopItem]:
    return SHOP_ITEMS.values()


@router.post(path="/shop/item", status_code=status.HTTP_200_OK)
async def grant_shop_item(
    service: Annotated[ShopService, Depends()],
    data: XTRPaymentCallbackDTO,
) -> None:
    return await service.handle_payment_callback(data=data)
