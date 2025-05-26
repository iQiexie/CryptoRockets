import secrets
from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import APIKeyHeader, HTTPBasic, HTTPBasicCredentials
from starlette import status

from app.adapters.base import Adapters
from app.api.dependencies.stubs import dependency_adapters, dependency_services
from app.api.exceptions import ClientError
from app.services.base.services import Services
from app.services.dto.auth import WebappData

BasicAuth = HTTPBasic()
AuthTaskHeader = APIKeyHeader(name="token", scheme_name="AuthTask", auto_error=True)
AuthUserHeader = APIKeyHeader(name="token", scheme_name="AuthUserCryptorockets", auto_error=True)
AuthMaybeUserHeader = APIKeyHeader(name="token", scheme_name="AuthUserCryptorockets", auto_error=False)
AuthTelegramHeader = APIKeyHeader(name="X-Telegram-Bot-Api-Secret-Token", scheme_name="AuthTelegram", auto_error=True)


def get_country(request: Request) -> str | None:
    return request.headers.get("cf-ipcountry")


async def get_current_user(
    services: Services = Depends(dependency_services),
    webapp_data: str = Depends(AuthUserHeader),
) -> WebappData:
    return services.auth.auth_webapp(webapp_data=webapp_data, adapters=services.adapters)


def auth_basic(
    adapters: Annotated[Adapters, Depends(dependency_adapters)],
    credentials: Annotated[HTTPBasicCredentials, Depends(BasicAuth)],
) -> None:
    correct_username = secrets.compare_digest(credentials.username, adapters.config.auth.AUTH_OPENAPI_USERNAME)
    correct_password = secrets.compare_digest(credentials.password, adapters.config.auth.AUTH_OPENAPI_PASSWORD)

    if not (correct_username and correct_password):
        raise ClientError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message="Invalid credentials",
        )


def auth_task(
    adapters: Annotated[Adapters, Depends(dependency_adapters)],
    token: Annotated[str, Depends(AuthTaskHeader)],
) -> bool:
    correct_token = secrets.compare_digest(token, adapters.config.auth.AUTH_TOKEN_TASK)

    if not correct_token:
        raise ClientError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message="Invalid credentials",
        )

    return True


def auth_telegram(
    adapters: Annotated[Adapters, Depends(dependency_adapters)],
    token: str = Depends(AuthTelegramHeader),
) -> bool:
    if token != adapters.config.bot.TELEGRAM_BOT_WEBHOOK_SECRET:
        raise ClientError(status_code=status.HTTP_401_UNAUTHORIZED, message="Invalid credentials")

    return True
