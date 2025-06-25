from app.init.base_models import BaseModel


class UpdateUserRequest(BaseModel):
    address: str | None = None
    rich_ads_tasks: int | None = None
