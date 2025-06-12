import datetime
from enum import Enum
from typing import Any, Dict

from sqlalchemy import (
    BigInteger,
    Boolean,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    func,
    inspect,
)
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql.functions import current_timestamp

from app.utils import SafeList


class TransactionTypeEnum(str, Enum):
    wheel_spin = "wheel_spin"
    rocket_launch = "rocket_launch"
    purchase = "purchase"
    task_completion = "task_completion"


class TransactionStatusEnum(str, Enum):
    created = "created"
    success = "success"
    error = "error"


class CurrenciesEnum(str, Enum):
    ton = "ton"
    usdt = "usdt"
    token = "token"  # noqa: S105
    fuel = "fuel"
    wheel = "wheel"
    xtr = "xtr"


class AdStatusEnum(str, Enum):
    created = "created"
    watched = "watched"


class TaskTypeEnum(str, Enum):
    subscribe = "subscribe"
    watch_ad = "watch_ad"
    invite = "invite"
    bot = "bot"


class TaskRewardEnum(str, Enum):
    fuel = CurrenciesEnum.fuel.value
    token = CurrenciesEnum.token.value


class RocketTypeEnum(str, Enum):
    default = "default"
    offline = "offline"
    premium = "premium"
    super = "super"
    mega = "mega"
    ultra = "ultra"
    super_mega_ultra = "super_mega_ultra"


class RocketSkinEnum(str, Enum):
    default = "default"
    wood = "wood"


class WheelPrizeEnum(str, Enum):
    premium_rocket = "premium_rocket"
    default_rocket = "default_rocket"
    offline_rocket = "offline_rocket"

    super_rocket = "super_rocket"
    mega_rocket = "mega_rocket"
    ultra_rocket = "ultra_rocket"
    super_mega_ultra_rocket = "super_mega_ultra_rocket"

    fuel = "fuel"
    token = "token"  # noqa: S105
    usdt = "usdt"
    ton = "ton"
    wheel = "wheel"


class Base(DeclarativeBase):
    def object_as_dict(self) -> Dict[str, Any]:
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}  # noqa


class _TimestampMixin(Base):
    __abstract__ = True

    created_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP,
        default=datetime.datetime.utcnow,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP,
        onupdate=current_timestamp().op("AT TIME ZONE")("UTC"),
        default=datetime.datetime.utcnow,
        server_default=func.now(),
    )


class User(_TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    tg_username: Mapped[str] = mapped_column(String, nullable=True)
    tg_first_name: Mapped[str] = mapped_column(String, nullable=True)
    tg_last_name: Mapped[str] = mapped_column(String, nullable=True)
    tg_is_premium: Mapped[bool] = mapped_column(Boolean, nullable=True)
    tg_language_code: Mapped[str] = mapped_column(String, nullable=True)
    tg_photo_url: Mapped[str] = mapped_column(String, nullable=True)
    bot_banned: Mapped[bool] = mapped_column(Boolean, nullable=True)
    country: Mapped[str] = mapped_column(String, nullable=True)
    address: Mapped[str] = mapped_column(String, nullable=True)

    ton_balance: Mapped[float] = mapped_column(Numeric, server_default="0", default=0)
    usdt_balance: Mapped[float] = mapped_column(Numeric, server_default="0", default=0)
    token_balance: Mapped[float] = mapped_column(Numeric, server_default="0", default=0)
    fuel_balance: Mapped[float] = mapped_column(Numeric, server_default="0", default=0)
    wheel_balance: Mapped[float] = mapped_column(Numeric, server_default="0", default=0)
    last_broadcast_key: Mapped[str] = mapped_column(String, nullable=True)

    referral_from: Mapped[int] = mapped_column(
        ForeignKey("users.telegram_id", ondelete="CASCADE"), nullable=True, index=True
    )

    default_rocket_received: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP,
        default=datetime.datetime.utcnow,
        server_default=func.now(),
    )

    offline_rocket_received: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP,
        default=datetime.datetime.utcnow,
        server_default=func.now(),
    )

    premium_rocket_received: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP,
        default=datetime.datetime.utcnow,
        server_default=func.now(),
    )

    wheel_received: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP,
        default=datetime.datetime.utcnow,
        server_default=func.now(),
    )

    has_spins: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")

    rockets: Mapped[list["Rocket"]] = relationship(
        "Rocket",
        primaryjoin="and_(User.telegram_id == Rocket.user_id, Rocket.enabled == True)",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class Rocket(_TimestampMixin, Base):
    __tablename__ = "rockets"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.telegram_id", ondelete="CASCADE"))
    type: Mapped[RocketTypeEnum] = mapped_column(String)

    fuel_capacity: Mapped[int] = mapped_column(Integer)
    current_fuel: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    seen: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")

    user: Mapped[User] = relationship(back_populates="rockets")


class Transaction(_TimestampMixin, Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.telegram_id"))

    balance_before: Mapped[float] = mapped_column(Numeric, nullable=True)
    balance_after: Mapped[float] = mapped_column(Numeric, nullable=True)
    balance_amount: Mapped[float] = mapped_column(Numeric, nullable=True)
    balance_currency: Mapped[CurrenciesEnum] = mapped_column(String)

    type: Mapped[TransactionTypeEnum] = mapped_column(String)
    status: Mapped[TransactionStatusEnum] = mapped_column(String)
    refund_id: Mapped[int] = mapped_column(ForeignKey("transactions.id"), nullable=True)


class WheelPrize(_TimestampMixin, Base):
    __tablename__ = "wheel_prizes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.telegram_id"))

    type: Mapped[WheelPrizeEnum] = mapped_column(String)
    amount: Mapped[float] = mapped_column(Numeric, nullable=True)
    icon: Mapped[str] = mapped_column(String)

    user = relationship("User", foreign_keys=[user_id], viewonly=True)


class Invoice(_TimestampMixin, Base):
    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.telegram_id"))
    external_id: Mapped[str] = mapped_column(String, unique=True, nullable=True)

    status: Mapped[TransactionStatusEnum] = mapped_column(String)

    currency: Mapped[CurrenciesEnum] = mapped_column(String)
    currency_amount: Mapped[float] = mapped_column(Numeric)
    currency_fee: Mapped[float] = mapped_column(Numeric, nullable=True)
    usd_amount: Mapped[float] = mapped_column(Numeric)

    transaction_id: Mapped[int] = mapped_column(ForeignKey("transactions.id"), nullable=True)
    rocket_id: Mapped[int] = mapped_column(ForeignKey("rockets.id"), nullable=True)
    rocket_skin: Mapped[RocketSkinEnum] = mapped_column(String, nullable=True)

    callback_data: Mapped[dict] = mapped_column(JSONB, nullable=True)
    refunded: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")


class Task(_TimestampMixin, Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    reward: Mapped[TaskRewardEnum] = mapped_column(String)
    reward_amount: Mapped[float] = mapped_column(Numeric)
    task_type: Mapped[TaskTypeEnum] = mapped_column(String)
    url: Mapped[str] = mapped_column(String, nullable=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    amount: Mapped[float] = mapped_column(Numeric, nullable=True)
    icon: Mapped[str] = mapped_column(String)
    name: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String, nullable=True)

    @property
    def rocket_data(self) -> dict | None:
        if "rocket" not in self.reward:
            return

        reward = SafeList(self.reward.split("_"))
        return {"type": reward.get(0), "full": "full" in (reward.get(2, ""))}


class TaskUser(_TimestampMixin, Base):
    __tablename__ = "tasks_users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.telegram_id"), index=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"), index=True)

    __table_args__ = (UniqueConstraint("user_id", "task_id"),)


class Advert(_TimestampMixin, Base):
    __tablename__ = "ads"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(Integer)
    provider: Mapped[str] = mapped_column(String)
    status: Mapped[AdStatusEnum] = mapped_column(String)
    rocket_id: Mapped[int] = mapped_column(ForeignKey("rockets.id"), nullable=True)


# class BroadcastLog(_TimestampMixin, Base):
#     __tablename__ = "broadcast_logs"
#
#     id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
#     user_id: Mapped[int] = mapped_column(ForeignKey("users.telegram_id"))
#     broadcast_key: Mapped[str] = mapped_column(String)
