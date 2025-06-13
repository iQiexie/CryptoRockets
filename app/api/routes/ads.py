from typing import Annotated

import structlog
from fastapi import APIRouter, Depends
from starlette import status

from app.api.dependencies.auth import get_current_user
from app.api.dto.ads.request import AdCheckRequest, AdRequest
from app.api.dto.ads.response import AdsResponse
from app.api.dto.ads.response import VerifyAdResponse
from app.api.dto.user.response import RocketResponse
from app.api.dto.user.response import UserResponse
from app.db.models import Advert, Rocket
from app.db.models import User
from app.services.ads import AdsService
from app.services.dto.auth import WebappData

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
    response_model=VerifyAdResponse,
)
async def verify(
    current_user: Annotated[WebappData, Depends(get_current_user)],
    service: Annotated[AdsService, Depends()],
    data: AdCheckRequest,
) -> VerifyAdResponse:
    return await service.verify_offer(current_user=current_user, data=data)
