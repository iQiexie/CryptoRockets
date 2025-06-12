from typing import Annotated

from fastapi import APIRouter, Depends, Path
from starlette import status

from app.api.dependencies.auth import get_current_user
from app.api.dto.user.response import UserResponse
from app.api.dto.user_task.response import TaskResponse
from app.db.models import Task, User
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


@router.get(
    path="/user/tasks/check/{task_id}",
    status_code=status.HTTP_200_OK,
    response_model=UserResponse,
)
async def check_subscription(
    current_user: Annotated[WebappData, Depends(get_current_user)],
    service: Annotated[UserTaskService, Depends()],
    task_id: int = Path(...),
) -> User:
    return await service.check_task(current_user=current_user, task_id=task_id)


@router.get(
    path="/user/tasks/mark_complete/{task_id}",
    status_code=status.HTTP_200_OK,
    response_model=UserResponse,
)
async def mark_complete(
    current_user: Annotated[WebappData, Depends(get_current_user)],
    service: Annotated[UserTaskService, Depends()],
    task_id: int = Path(...),
) -> User:
    return await service.mark_complete(current_user=current_user, task_id=task_id)
