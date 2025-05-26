from typing import Annotated, Any

import structlog
from aiogram import Bot
from aiogram.methods import TelegramMethod
from fastapi import APIRouter, Body, Depends
from fastapi.responses import ORJSONResponse
from starlette import status

from app.adapters.base import Adapters
from app.api.dependencies.auth import auth_telegram
from app.api.dependencies.stubs import dependency_adapters, dependency_services
from app.services.base.services import Services
from app.telegram.dispatcher import root_dispatcher
from app.telegram.patches import prepare_value
from app.utils import struct_log

logger = structlog.stdlib.get_logger()
router = APIRouter(tags=["Telegram callback"])


def process_response(response: TelegramMethod, bot: Bot) -> dict[str, Any]:
    if not response:
        return {}

    if hasattr(response, "name") and response.name == "UNHANDLED":
        return {}

    result = {"method": response.__api_method__}
    for key, value in response.model_dump(warnings=False, exclude_none=True).items():
        prepared_value = prepare_value(value=value, bot=bot, files={})

        if prepared_value:
            result[key] = prepared_value

    return result


@router.post(path="/telegram", response_class=ORJSONResponse)
async def webhook(
    _: Annotated[bool, Depends(auth_telegram)],
    adapters: Annotated[Adapters, Depends(dependency_adapters)],
    body: Any = Body(),
    services: Services = Depends(dependency_services),
) -> ORJSONResponse:
    _response = await root_dispatcher.feed_raw_update(
        update=body,
        bot=adapters.bot,
        adapters=adapters,
        services=services,
    )

    try:
        response = process_response(response=_response, bot=adapters.bot)
    except Exception as e:
        logger.error(f"Error processing response: {e}", exception=e)
        response = {}

    struct_log(event="Response", data=response)

    return ORJSONResponse(
        content=response,
        status_code=status.HTTP_200_OK,
        media_type="application/json",
    )
