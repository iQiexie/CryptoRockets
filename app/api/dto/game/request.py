from app.init.base_models import BaseModel


class LaunchResponse(BaseModel):
    new_balance_usdt: float | None = None
    new_balance_ton: float | None = None
