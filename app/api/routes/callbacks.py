import traceback
from typing import Annotated

from fastapi import APIRouter, Body, Depends
from starlette import status

from app.api.dto.shop.request import SHOP_ITEMS
from app.api.exceptions import ClientError
from app.config.constants import TON_PRICE
from app.db.models import CurrenciesEnum
from app.db.models import WheelPrizeEnum
from app.services.dto.shop import PaymentCallbackDTO
from app.services.shop import ShopService
from app.services.shop import logger
from app.utils import SafeList

router = APIRouter(tags=["Callbacks"])


@router.post(path="/callbacks/ton", status_code=status.HTTP_200_OK)
async def ton(
    service: Annotated[ShopService, Depends()],
    body: dict = Body(...),
) -> None:
    data = SafeList(body["payload"].split(";"))
    try:
        telegram_id = data[0]
        item_id = data[1]
        item_amount = data.get(2, 1)
    except (ValueError, IndexError) as e:
        await service.adapters.alerts.send_alert(
            message=f"Invalid payload format in TON callback: {body=}",
        )
        logger.error(f"Invalid payload in callback", exception=traceback.format_exception(e))
        raise ClientError(message="Invalid payload format in TON callback")

    item = SHOP_ITEMS[int(item_id)]
    if item.item == WheelPrizeEnum.gift_withdrawal:
        new_data = {"gift_id": item_amount}
    else:
        new_data = {"item_amount": item_amount}

    return await service.handle_payment_callback(
        data=PaymentCallbackDTO(
            telegram_id=int(telegram_id),
            item_id=int(item_id),
            amount=body["amount"],
            usd_amount=body["amount"] * TON_PRICE,
            currency=CurrenciesEnum.ton,
            external_id=body["hash"],
            callback_data=body,
            **new_data,
        )
    )
