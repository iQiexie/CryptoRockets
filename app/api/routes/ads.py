from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, Request
from fastapi import Path
from fastapi import Query
from sqlalchemy.util import b64decode
from starlette import status
from starlette.websockets import WebSocket

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.stubs import dependency_websocket_service
from app.api.dto.ads.request import AdCheckRequest
from app.api.dto.ads.request import AdRequest
from app.api.dto.ads.response import AdsResponse
from app.api.dto.base import PaginatedRequest, PaginatedResponse
from app.api.dto.user.request import UpdateUserRequest
from app.api.dto.user.response import PublicUserResponse, UserResponse
from app.db.models import Advert
from app.db.models import User
from app.services.ads import AdsService
from app.services.dto.auth import WebappData
from app.services.user import UserService
from app.services.websocket import WebsocketService

router = APIRouter(tags=["Offers"])
logger = structlog.stdlib.get_logger()


@router.post(
    path="/offer",
    status_code=status.HTTP_200_OK,
    response_model=AdsResponse,
)
async def ads(
    current_user: Annotated[WebappData, Depends(get_current_user)],
    service: Annotated[AdsService, Depends()],
    data: AdRequest,
) -> Advert:
    return await service.create_ad(current_user=current_user, data=data)


@router.post(
    path="/offer/verify",
    status_code=status.HTTP_200_OK,
    response_model=AdsResponse,
)
async def ads(
    current_user: Annotated[WebappData, Depends(get_current_user)],
    service: Annotated[AdsService, Depends()],
    data: AdCheckRequest
) -> Advert:
    return await service.verify_offer(current_user=current_user, data=data)
