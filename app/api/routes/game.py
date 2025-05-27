from typing import Annotated

from fastapi import APIRouter, Depends
from starlette import status

from app.api.dependencies.auth import get_current_user
from app.api.dto.game.request import LaunchResponse
from app.services.dto.auth import WebappData
from app.services.game import GameService

router = APIRouter(tags=["User"])


@router.post(
    path="/game/launch_rocket",
    status_code=status.HTTP_200_OK,
    response_model=LaunchResponse,
)
async def launch_rocket(
    current_user: Annotated[WebappData, Depends(get_current_user)],
    service: Annotated[GameService, Depends()],
) -> LaunchResponse:
    return await service.launch_rocket(current_user=current_user)
