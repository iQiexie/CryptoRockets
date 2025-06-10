from typing import Annotated

from fastapi import APIRouter, Depends
from starlette import status

from app.db.models import RocketTypeEnum
from app.services.task import TaskService

router = APIRouter(tags=["Task"])


@router.get(path="/task/give_rocket", status_code=status.HTTP_200_OK)
async def give_rocket(
    rocket_type: RocketTypeEnum,
    telegram_id: int,
    full: bool,
    service: Annotated[TaskService, Depends()],
) -> None:
    return await service.give_rocket(rocket_type=rocket_type, full=full, telegram_id=telegram_id)


@router.get(path="/task/give_offline_rocket", status_code=status.HTTP_200_OK)
async def give_offline_rocket(service: Annotated[TaskService, Depends()]) -> None:
    return await service.give_offline_rocket()
