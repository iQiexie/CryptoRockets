from app.adapters.alerts import AlertsAdapter
from app.adapters.redis import RedisAdapter
from app.config.config import Config
from app.external.base.aiohttp_client import AioHttpClient
from app.telegram.patches import Bot
from i18n.service import I18n


class Adapters:
    def __init__(self, config: Config):
        self.config = config
        self.i18n = I18n()
        self.alerts = AlertsAdapter(config=config)
        self.http_client = AioHttpClient(auth_header={}, base_url="")

        self.redis = RedisAdapter(config=config.redis)
        self.bot = Bot(config=config.bot, i18n=self.i18n, token=config.bot.TELEGRAM_BOT_TOKEN)
