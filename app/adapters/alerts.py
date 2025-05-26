import json
import re
import traceback
import urllib.parse

import aiohttp
import structlog
from starlette import status
from starlette.responses import Response

from app.config.config import Config
from app.config.constants import LOGGING_SENSITIVE_FIELDS, LOGGING_SENSITIVE_REPLACEMENT
from app.utils import struct_log

logger = structlog.stdlib.get_logger()


class AlertsAdapter:
    def __init__(self, config: Config):
        regex_str = r'("[^"]*?(?={keywords})[^"]*":\s*")[^"]*"'
        regex_with_keys = regex_str.format(keywords="|".join(LOGGING_SENSITIVE_FIELDS))
        self.regex_pattern = re.compile(regex_with_keys)
        self.substitution = rf'\1{LOGGING_SENSITIVE_REPLACEMENT}"'

        regex_str_url = r"({keywords})=([^=&?,\/\\]+)"
        regex_with_keys_url = regex_str_url.format(keywords="|".join(LOGGING_SENSITIVE_FIELDS))
        self.regex_pattern_url = re.compile(regex_with_keys_url)
        self.substitution_url = rf'\1={LOGGING_SENSITIVE_REPLACEMENT}"'

        self._alerts_enabled = config.alerts.ALERTS_ENABLED

        self._grafana_url = config.alerts.ALERTS_GRAFANA_URL.rstrip("/")
        self._grafana_data_source = config.alerts.ALERTS_GRAFANA_DATA_SOURCE
        self._container_name = config.alerts.ALERTS_CONTAINER_NAME

        self._bot_token = config.alerts.ALERTS_TELEGRAM_BOT_TOKEN
        self._chat_id = config.alerts.ALERTS_TELEGRAM_CHAT_ID

    async def send_alert(self, message: str, chat_id: int = None) -> None:
        logger.info(f"Sending alert: {message=}")
        async with aiohttp.ClientSession() as client:
            resp = await client.post(
                ssl=False,
                url=f"https://api.telegram.org/bot{self._bot_token}/sendMessage",
                json=dict(
                    chat_id=chat_id or self._chat_id,
                    text=message,
                    parse_mode="HTML",
                ),
            )

        if resp.status >= status.HTTP_400_BAD_REQUEST:
            logger.error(f"Cannot send alerts notification: {await resp.text()=}, {message=}")

    async def handle_alert(
        self,
        response: Response,
        total_time: float,
        exception: Exception | None = None,
    ) -> None:
        try:
            await self._handle_alert(
                response=response,
                total_time=total_time,
                exception=exception,
            )
        except Exception as ex:
            logger.error(
                event=f"Unable to send alert: {ex}",
                exception=traceback.format_exception(ex),
            )

    async def _handle_alert(
        self,
        response: Response,
        total_time: float,
        exception: Exception | None = None,
    ) -> None:
        if exception is None:
            return

        if not self._alerts_enabled:
            return

        message = self._get_alerts_message(
            response=response,
            total_time=total_time,
        )

        await self.send_alert(message=message)

    def _get_alerts_message(
        self,
        response: Response,
        total_time: float,
    ) -> str:
        context = structlog.contextvars.get_contextvars()

        method = context.get("method", "").ljust(11, " ")
        url = self._protect_url(data=context.get("url", ""))
        body = self._protect_data(data=context.get("body", ""))
        query = self._protect_data(data=context.get("query", ""))
        user_id = context.get("user_id", "")
        key = context.get("key", "")

        if response:
            try:
                response = response.body.decode("utf-8")
            except Exception as e:
                logger.error(event="Cannot decode body", exception=traceback.format_exception(e))
                response = response.body
        else:
            response = ""

        grafana_url = self._get_grafana_url(key=key)

        error = f"🛑 5️⃣0️⃣0️⃣ Ошибка {self._container_name} 🛑"

        result = ""
        result += f"<pre>{error}</pre>\n\n"
        result += (
            f"<pre>REQUEST\n\n"
            f"<b>➡️ {method}{url}</b>\n"
            f"<b>➡️ QUERY     </b> {query}\n"
            f"<b>➡️ BODY      </b> {body}\n"
            f"<b>➡️ USER_ID   </b> {user_id}\n"
            f"<b>➡️ KEY       </b> {key}"
            f"</pre>\n\n"
        )
        result += (
            f"<pre>RESPONSE\n\n"
            f"<b>⬅️ TIME      </b> {total_time:.4f}\n"
            f"<b>⬅️ BODY      </b> {response}</pre>\n\n"
        )

        result += f'🔗 <a href="{grafana_url}">Grafana</a>'
        return result

    def _get_grafana_url(self, key: str) -> str:
        left = {
            "datasource": self._grafana_data_source,
            "queries": [
                {
                    "refId": "A",
                    "datasource": {"type": "loki", "uid": self._grafana_data_source},
                    "editorMode": "code",
                    "expr": f'{{container="{self._container_name}"}} | json | __error__ = `` | key = "{key}"',
                    "queryType": "range",
                }
            ],
            "range": {"from": "now-1h", "to": "now"},
        }
        params = {"orgId": 1, "left": json.dumps(left)}
        params = urllib.parse.urlencode(params)
        return f"{self._grafana_url}/explore?{params}"

    def _protect_data(self, data: str) -> str:
        try:
            return re.sub(
                self.regex_pattern,
                repl=self.substitution,
                string=data,
            )
        except Exception as e:
            struct_log(event="Failed to protect string", exception=traceback.format_exception(e))
            return data

    def _protect_url(self, data: str) -> str:
        try:
            return re.sub(
                self.regex_pattern_url,
                repl=self.substitution_url,
                string=data,
            )
        except Exception as e:
            struct_log(event="Failed to protect string", exception=traceback.format_exception(e))
            return data
