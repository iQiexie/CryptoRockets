from pydantic import Field
from pydantic import field_validator
from pydantic_core.core_schema import ValidationInfo

from app.api.dto.base import BaseResponse
from app.db.models import TaskRewardEnum, TaskTypeEnum
from app.db.models import TaskStatusEnum


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
    rocket_data: dict | None = None
    description: str | None = None
    completed: bool = Field(default=False, exclude=True)
