from typing import Annotated

from fastapi import APIRouter, Depends
from starlette import status

from app.api.dependencies.auth import get_current_user
from app.api.dto.user_task.response import TaskResponse
from app.db.models import Task
from app.services.dto.auth import WebappData
from app.services.user_task import UserTaskService

router = APIRouter(tags=["User Tasks"])


@router.get(
    path="/user/tasks",
    status_code=status.HTTP_200_OK,
    response_model=list[TaskResponse],
)
async def get_all_eligible_tasks(
    current_user: Annotated[WebappData, Depends(get_current_user)],
    service: Annotated[UserTaskService, Depends()],
) -> list[Task]:
    return await service.get_tasks(current_user=current_user)
