from typing import Annotated

from fastapi import APIRouter, Depends, Path
from starlette import status

from app.api.dependencies.auth import get_current_user
from app.api.dto.game.request import MakeBetRequest
from app.api.dto.game.response import BetConfigResponse
from app.api.dto.game.response import GiftUserResponse
from app.api.dto.game.response import MakeBetResponse
from app.api.dto.game.response import (
    WHEEL_PRIZES,
    LatestWheelPrizeResponse,
    LaunchResponse,
    WheelPrizeResponse,
)
from app.api.dto.user.response import UserResponse
from app.db.models import BetConfig
from app.db.models import GiftUser
from app.db.models import WheelPrize
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


@router.get(
    path="/gift/bet/config",
    status_code=status.HTTP_200_OK,
    response_model=BetConfigResponse,
    tags=["Gifts"],
)
async def bets_config(service: Annotated[GameService, Depends()]) -> dict[list[BetConfig]]:
    resp = await service.get_bets_config()
    return resp


@router.post(
    path="/gift/bet/make",
    status_code=status.HTTP_200_OK,
    response_model=MakeBetResponse,
    tags=["Gifts"],
)
async def make_bet(
    data: MakeBetRequest,
    service: Annotated[GameService, Depends()],
    current_user: Annotated[WebappData, Depends(get_current_user)],
) -> MakeBetResponse:
    resp = await service.make_bet(data=data, current_user=current_user)
    return resp


@router.get(
    path="/gifts",
    status_code=status.HTTP_200_OK,
    response_model=list[GiftUserResponse],
    tags=["Gifts"],
)
async def get_gifts(
    service: Annotated[GameService, Depends()],
    current_user: Annotated[WebappData, Depends(get_current_user)],
) -> list[GiftUser]:
    resp = await service.get_gifts(current_user=current_user)
    return resp


@router.get(
    path="/gifts/latest",
    status_code=status.HTTP_200_OK,
    response_model=list[GiftUserResponse],
    tags=["Gifts"],
)
async def get_gifts(service: Annotated[GameService, Depends()]) -> list[GiftUser]:
    resp = await service.get_latest_gifts()
    return resp
