import functools
import json
from typing import Tuple

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config.config import PostgresConfig
from app.init.base_models import DecimalEncoder


def get_session_factory(config: PostgresConfig) -> Tuple[sessionmaker, AsyncEngine]:
    engine = create_async_engine(
        url=config.dsn,
        echo=config.POSTGRES_ECHO,
        pool_size=config.POSTGRES_POOL_SIZE,
        max_overflow=config.POSTGRES_MAX_OVERFLOW,
        isolation_level=config.POSTGRES_ISOLATION_LEVEL,
        json_serializer=functools.partial(json.dumps, cls=DecimalEncoder),
        pool_pre_ping=True,
        future=True,
    )

    session_factory = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)  # noqa
    return session_factory, engine
