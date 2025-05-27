from typing import Annotated

from fastapi import APIRouter, Depends, Request
from starlette import status

from app.api.dependencies.auth import get_current_user
from app.api.dto.game.request import LaunchResponse
from app.api.dto.user.request import UpdateUserRequest
from app.api.dto.user.response import UserResponse
from app.db.models import User
from app.services.dto.auth import WebappData
from app.services.game import GameService
from app.services.user import UserService

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

