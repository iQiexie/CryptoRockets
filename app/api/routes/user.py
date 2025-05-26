from typing import Annotated

from fastapi import APIRouter, Depends, Request
from starlette import status

from app.api.dependencies.auth import get_current_user
from app.api.dto.user.request import UpdateUserRequest
from app.api.dto.user.response import UserResponse
from app.db.models import User
from app.services.dto.auth import WebappData
from app.services.user import UserService

router = APIRouter(tags=["User"])


@router.get(
    path="/user/me",
    status_code=status.HTTP_200_OK,
    response_model=UserResponse,
)
async def get_me(
    request: Request,
    current_user: Annotated[WebappData, Depends(get_current_user)],
    service: Annotated[UserService, Depends()],
) -> User:
    current_user.country = request.headers.get("cf-ipcountry")
    return await service.get_or_create_user(data=current_user)


@router.patch(
    path="/user/me",
    status_code=status.HTTP_200_OK,
    response_model=UserResponse,
)
async def update_me(
    data: UpdateUserRequest,
    service: Annotated[UserService, Depends()],
    current_user: Annotated[WebappData, Depends(get_current_user)],
) -> User:
    return await service.update_user(current_user=current_user, data=data)
