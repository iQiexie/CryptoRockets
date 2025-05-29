import structlog

from app.config.config import Config
from app.external.base.aiohttp_client import AioHttpClient

logger = structlog.stdlib.get_logger()


class TelegramClient:
    def __init__(self, config: Config):
        self.config = config
        self.http_client = AioHttpClient(
            auth_header={},
            base_url=f"https://api.telegram.org/bot{config.bot.TELEGRAM_BOT_TOKEN}",
        )

    async def send_method(self, method: str, params: dict) -> dict:
        return await self.http_client.request(method="GET", url=f"/{method}", params=params, return_json=True)
