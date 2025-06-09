from typing import Annotated

from fastapi import APIRouter, Body, Depends
from starlette import status

from app.api.exceptions import ClientError
from app.db.models import CurrenciesEnum
from app.services.dto.shop import PaymentCallbackDTO
from app.services.shop import ShopService

router = APIRouter(tags=["Callbacks"])


@router.post(path="/callbacks/ton", status_code=status.HTTP_200_OK)
async def ton(
    service: Annotated[ShopService, Depends()],
    body: dict = Body(...),
) -> None:
    try:
        telegram_id, item_id = body["payload"].split(";")
        usd_amount = 0
    except ValueError:
        await service.adapters.alerts.send_alert(
            message=f"Invalid payload format in TON callback: {body=}",
        )
        raise ClientError(message="Invalid payload format in TON callback")

    return await service.handle_payment_callback(
        data=PaymentCallbackDTO(
            telegram_id=int(telegram_id),
            item_id=int(item_id),
            amount=body["amount"],
            usd_amount=usd_amount,
            currency=CurrenciesEnum.ton,
            external_id=body["hash"],
            callback_data=body,
        )
    )
