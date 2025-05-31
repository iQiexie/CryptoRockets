from typing import Annotated

from fastapi import APIRouter, Depends, Path
from starlette import status

from app.api.dependencies.auth import get_current_user
from app.api.dto.game.request import UpdateRocketRequest
from app.api.dto.game.response import (
    WHEEL_PRIZES,
    LatestWheelPrizeResponse,
    LaunchResponse,
    WheelPrizeResponse,
)
from app.api.dto.user.response import RocketResponse
from app.db.models import Rocket, WheelPrize
from app.services.dto.auth import WebappData
from app.services.game import GameService

router = APIRouter()


@router.post(
    path="/rocket/launch/{rocket_id}",
    status_code=status.HTTP_200_OK,
    response_model=LaunchResponse,
    tags=["Rockets"],
)
async def launch_rocket(
    current_user: Annotated[WebappData, Depends(get_current_user)],
    service: Annotated[GameService, Depends()],
    rocket_id: int = Path(...),
) -> LaunchResponse:
    return await service.launch_rocket(current_user=current_user, rocket_id=rocket_id)


@router.patch(
    path="/rocket/{rocket_id}",
    status_code=status.HTTP_200_OK,
    response_model=RocketResponse,
    tags=["Rockets"],
)
async def update_rocket(
    current_user: Annotated[WebappData, Depends(get_current_user)],
    service: Annotated[GameService, Depends()],
    data: UpdateRocketRequest,
    rocket_id: int = Path(...),
) -> Rocket:
    return await service.update_rocket(current_user=current_user, rocket_id=rocket_id, data=data)


@router.post(
    path="/wheel/spin",
    status_code=status.HTTP_200_OK,
    response_model=WheelPrizeResponse,
    tags=["Wheel"],
)
async def spin_wheel(
    current_user: Annotated[WebappData, Depends(get_current_user)],
    service: Annotated[GameService, Depends()],
) -> WheelPrizeResponse:
    return await service.spin_wheel(current_user=current_user)


@router.get(
    path="/wheel/winners",
    status_code=status.HTTP_200_OK,
    response_model=list[LatestWheelPrizeResponse],
    tags=["Wheel"],
)
async def get_winners(
    service: Annotated[GameService, Depends()],
) -> list[WheelPrize]:
    return await service.get_latest_wheel_winners()


@router.get(
    path="/wheel/prizes",
    status_code=status.HTTP_200_OK,
    response_model=list[WheelPrizeResponse],
    tags=["Wheel"],
)
async def wheel_prizes() -> list[WheelPrizeResponse]:
    return WHEEL_PRIZES
