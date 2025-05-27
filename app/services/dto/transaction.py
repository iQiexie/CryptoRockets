from app.db.models import Transaction, User
from app.init.base_models import BaseModel


class ChangeUserBalanceDTO(BaseModel):
    user: User
    transaction: Transaction
