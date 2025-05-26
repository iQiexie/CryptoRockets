import hashlib
import hmac
import json
from datetime import datetime, timedelta
from operator import itemgetter
from typing import Annotated, TypeVar
from urllib.parse import parse_qsl

import structlog
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from starlette import status

from app.adapters.base import Adapters
from app.api.dependencies.stubs import (
    dependency_adapters,
    dependency_session_factory,
    placeholder,
)
from app.api.exceptions import ClientError
from app.init.base_models import BaseModel
from app.services.base.base import BaseService
from app.services.dto.auth import WebappData

PydanticModel = TypeVar("PydanticModel", BaseModel, BaseModel)

logger = structlog.stdlib.get_logger()


class AuthService(BaseService):
    def __init__(
        self,
        adapters: Annotated[Adapters, Depends(dependency_adapters)],
        session_factory: Annotated[sessionmaker, Depends(dependency_session_factory)],
        session: Annotated[AsyncSession, Depends(placeholder)] = None,
    ):
        super().__init__(session_factory=session_factory, adapters=adapters, session=session)

        self.repo = self.repos.user
        self.adapters = adapters

    @staticmethod
    def auth_webapp(webapp_data: str, adapters: Adapters) -> WebappData:
        parsed_data = dict(parse_qsl(webapp_data))
        logger.error(f"{parsed_data=}")

        try:
            param_hash = parsed_data.pop("hash")
            max_auth_date = datetime.fromtimestamp(int(parsed_data["auth_date"])) + timedelta(days=7)
        except KeyError:
            raise ClientError(message="invalid webapp data", status_code=status.HTTP_401_UNAUTHORIZED)

        if datetime.utcnow() > max_auth_date:
            raise ClientError(
                status_code=status.HTTP_401_UNAUTHORIZED,
                message="auth_date is too old",
            )

        sorted_data = sorted(parsed_data.items(), key=itemgetter(0))
        data_check_string = "\n".join(f"{k}={v}" for k, v in sorted_data)

        secret_key = hmac.new(
            key=b"WebAppData",
            msg=adapters.config.bot.TELEGRAM_BOT_TOKEN.encode(),
            digestmod=hashlib.sha256,
        )

        actual_hash = hmac.new(
            key=secret_key.digest(),
            msg=data_check_string.encode(),
            digestmod=hashlib.sha256,
        ).hexdigest()

        invalid_hash = (param_hash != actual_hash) and adapters.config.auth.AUTH_CHECK_TELEGRAM_TOKEN

        if invalid_hash:
            raise ClientError(
                status_code=status.HTTP_412_PRECONDITION_FAILED,
                message="hash mismatch",
            )

        user_data = json.loads(parsed_data["user"])

        return WebappData(
            telegram_id=user_data["id"],
            language_code=user_data.get("language_code"),
            first_name=user_data.get("first_name"),
            last_name=user_data.get("last_name"),
            username=user_data.get("username"),
            is_premium=user_data.get("is_premium"),
            start_param=parsed_data.get("start_param"),
            photo_url=user_data.get("photo_url"),
        )
