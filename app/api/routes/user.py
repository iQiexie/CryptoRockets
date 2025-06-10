from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.util import b64decode
from starlette import status
from starlette.websockets import WebSocket

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.stubs import dependency_websocket_service
from app.api.dto.base import PaginatedRequest, PaginatedResponse
from app.api.dto.user.request import UpdateUserRequest
from app.api.dto.user.response import PublicUserResponse, UserResponse
from app.db.models import User
from app.services.dto.auth import WebappData
from app.services.user import UserService
from app.services.websocket import WebsocketService

router = APIRouter(tags=["User"])
logger = structlog.stdlib.get_logger()


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


@router.get(
    path="/user/referrals",
    status_code=status.HTTP_200_OK,
    response_model=PaginatedResponse[PublicUserResponse],
)
async def get_referrals(
    current_user: Annotated[WebappData, Depends(get_current_user)],
    service: Annotated[UserService, Depends()],
    pagination: PaginatedRequest = Depends(),
) -> PaginatedResponse[PublicUserResponse]:
    return await service.get_referrals(current_user=current_user, pagination=pagination)


@router.post(path="/user/seen", status_code=status.HTTP_200_OK)
async def set_seen(
    current_user: Annotated[WebappData, Depends(get_current_user)],
    service: Annotated[UserService, Depends()],
) -> None:
    return await service.set_seen(current_user=current_user)


@router.websocket(path="/user/ws")
async def connect_websocket(
    user_service: Annotated[UserService, Depends()],
    websocket_service: Annotated[WebsocketService, Depends(dependency_websocket_service)],
    websocket: WebSocket,
    token: str = Query(...),
) -> None:
    await websocket.accept()

    try:
        current_user = await get_current_user(
            services=user_service.services, webapp_data=b64decode(token).decode("utf-8")
        )

        await websocket_service.subscribe(
            websocket=websocket,
            telegram_id=current_user.telegram_id,
        )
    except Exception as e:
        try:
            await websocket.send_text(data=f"Got an error: {e}")
        except Exception as e_inner:
            logger.error(f"Failed tp send websocket: {e_inner}")

        raise e
