import datetime
from typing import Any, Dict

from sqlalchemy import (
    BigInteger,
    Boolean,
    Integer,
    String,
    func,
    inspect,
)
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql.functions import current_timestamp


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
