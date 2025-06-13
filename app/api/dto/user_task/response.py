from pydantic import Field

from app.api.dto.base import BaseResponse
from app.db.models import TaskRewardEnum, TaskStatusEnum, TaskTypeEnum


class TaskResponse(BaseResponse):
    id: int
    reward: TaskRewardEnum
    reward_amount: float
    task_type: TaskTypeEnum
    status: TaskStatusEnum
    url: str | None = None
    amount: int | None = None
    icon: str
    name: str
    description: str | None = None
    completed: bool = Field(default=False, exclude=True)
    rocket_type: str | None = None
