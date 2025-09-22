from app.api.dto.base import BaseRequest


class AdRequest(BaseRequest):
    provider: str
    rocket_id: int | None = None
    for_wheel: bool = False
    for_task: bool = False


class AdCheckRequest(BaseRequest):
    id: int
