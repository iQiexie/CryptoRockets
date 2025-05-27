from app.init.base_models import BaseModel


class LaunchResponse(BaseModel):
    new_balance_usdt: float
    new_balance_ton: float
