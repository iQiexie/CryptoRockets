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
    func,
    inspect,
)
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql.functions import current_timestamp


class TransactionTypeEnum(str, Enum):
    wheel_spin = "wheel_spin"
    rocket_launch = "rocket_launch"


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


class AdStatusEnum(str, Enum):
    watched = "watched"


class TaskTypeEnum(str, Enum):
    subscribe = "subscribe"
    watch_ad = "watch_ad"


class TaskRewardEnum(str, Enum):
    fuel = "fuel"


class RocketTypeEnum(str, Enum):
    default = "default"
    offline = "offline"
    premium = "premium"


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

    ton_balance: Mapped[float] = mapped_column(Numeric, server_default="0", default=0)
    usdt_balance: Mapped[float] = mapped_column(Numeric, server_default="0", default=0)
    token_balance: Mapped[float] = mapped_column(Numeric, server_default="0", default=0)
    fuel_balance: Mapped[float] = mapped_column(Numeric, server_default="0", default=0)
    wheel_balance: Mapped[float] = mapped_column(Numeric, server_default="0", default=0)

    referral_from: Mapped[str] = mapped_column(String, nullable=True)
    referral: Mapped[str] = mapped_column(String, unique=False)

    rockets: Mapped[list["Rocket"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", lazy="selectin"
    )


class Rocket(_TimestampMixin, Base):
    __tablename__ = "rockets"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.telegram_id", ondelete="CASCADE"))
    type: Mapped[RocketTypeEnum] = mapped_column(String)

    fuel_capacity: Mapped[int] = mapped_column(Integer)
    current_fuel: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    count: Mapped[int] = mapped_column(Integer, default=1, server_default="1")
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")

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


class Invoice(_TimestampMixin, Base):
    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.telegram_id"))
    external_id: Mapped[str] = mapped_column(String, unique=True, nullable=True)

    status: Mapped[TransactionStatusEnum] = mapped_column(String)

    currency: Mapped[CurrenciesEnum] = mapped_column(String)
    currency_amount: Mapped[float] = mapped_column(Numeric)
    currency_fee: Mapped[float] = mapped_column(Numeric, default=0, server_default="0")
    usd_amount: Mapped[float] = mapped_column(Numeric)

    callback_data: Mapped[dict] = mapped_column(JSONB, nullable=True)
    refunded: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")


class Task(_TimestampMixin, Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    reward: Mapped[TaskRewardEnum] = mapped_column(String)
    reward_amount: Mapped[float] = mapped_column(Numeric)
    task_type: Mapped[TaskTypeEnum] = mapped_column(String)
    url: Mapped[str] = mapped_column(String)


class TaskUser(_TimestampMixin, Base):
    __tablename__ = "tasks_users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.telegram_id"), index=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"), index=True)


class Advert(_TimestampMixin, Base):
    __tablename__ = "ads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(Integer)
    external_id: Mapped[str] = mapped_column(String, unique=True, nullable=True)
    status: Mapped[AdStatusEnum] = mapped_column(String)
    usd_amount: Mapped[float] = mapped_column(Numeric)
