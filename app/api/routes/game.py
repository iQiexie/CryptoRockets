from typing import Annotated

from fastapi import APIRouter, Depends
from starlette import status

from app.api.dependencies.auth import get_current_user
from app.api.dto.game.request import LaunchResponse
from app.api.dto.game.response import WHEEL_PRIZES, WheelPrizeResponse
from app.services.dto.auth import WebappData
from app.services.game import GameService

router = APIRouter(tags=["User"])


@router.post(
    path="/game/rocket/launch",
    status_code=status.HTTP_200_OK,
    response_model=LaunchResponse,
)
async def launch_rocket(
    current_user: Annotated[WebappData, Depends(get_current_user)],
    service: Annotated[GameService, Depends()],
) -> LaunchResponse:
    return await service.launch_rocket(current_user=current_user)


@router.post(
    path="/game/wheel/spin",
    status_code=status.HTTP_200_OK,
    response_model=LaunchResponse,
)
async def spin_wheel(
    current_user: Annotated[WebappData, Depends(get_current_user)],
    service: Annotated[GameService, Depends()],
) -> LaunchResponse:
    return await service.spin_wheel(current_user=current_user)


@router.get(
    path="/game/wheel/prizes",
    status_code=status.HTTP_200_OK,
    response_model=list[WheelPrizeResponse],
)
async def wheel_prizes() -> list[WheelPrizeResponse]:
    return WHEEL_PRIZES
