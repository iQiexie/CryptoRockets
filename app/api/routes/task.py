from typing import Annotated

from fastapi import APIRouter, Depends
from starlette import status

from app.services.task import TaskService

router = APIRouter(tags=["Task"])


@router.get(path="/task/example", status_code=status.HTTP_200_OK)
async def test(service: Annotated[TaskService, Depends()]) -> None:
    await service.example()
