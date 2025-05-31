from app.api.dto.base import BaseResponse
from app.db.models import TaskRewardEnum, TaskTypeEnum


class TaskResponse(BaseResponse):
    id: int
    reward: TaskRewardEnum
    reward_amount: float
    task_type: TaskTypeEnum
    url: str | None = None
    completed: bool
    amount: int | None = None
