from app.api.dto.base import BaseResponse
from app.db.models import TaskRewardEnum, TaskTypeEnum


class TaskResponse(BaseResponse):
    reward: TaskRewardEnum
    reward_amount: float
    task_type: TaskTypeEnum
    url: str
    completed: bool
