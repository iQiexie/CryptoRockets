from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from starlette import status

from app.api.dependencies.auth import get_current_user
from app.api.dto.game.request import LaunchRocket
from app.api.dto.game.response import LaunchResponse
from app.api.dto.game.response import WHEEL_PRIZES
from app.api.dto.game.response import WheelPrizeResponse
from app.services.dto.auth import WebappData
from app.services.game import GameService

router = APIRouter(tags=["Game"])


@router.post(
    path="/game/rocket/launch",
    status_code=status.HTTP_200_OK,
    response_model=LaunchResponse,
)
async def launch_rocket(
    current_user: Annotated[WebappData, Depends(get_current_user)],
    service: Annotated[GameService, Depends()],
    data: LaunchRocket,
) -> LaunchResponse:
    return await service.launch_rocket(current_user=current_user, rocket_type=data.type)


@router.post(
    path="/game/wheel/spin",
    status_code=status.HTTP_200_OK,
    response_model=WheelPrizeResponse,
)
async def spin_wheel(
    current_user: Annotated[WebappData, Depends(get_current_user)],
    service: Annotated[GameService, Depends()],
) -> WheelPrizeResponse:
    return await service.spin_wheel(current_user=current_user)


@router.get(
    path="/game/wheel/prizes",
    status_code=status.HTTP_200_OK,
    response_model=list[WheelPrizeResponse],
)
async def wheel_prizes() -> list[WheelPrizeResponse]:
    return WHEEL_PRIZES
