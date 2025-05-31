import logging

from pydantic import Field
from pydantic import computed_field
from app.config.constants import REFERRAL_PREFIX
from app.init.base_models import BaseModel


class WebappData(BaseModel):
    telegram_id: int
    language_code: str | None = Field(default="ru")
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    is_premium: bool | None = None
    photo_url: str | None = None
    start_param: str | None = None
    country: str | None = None

    @computed_field
    def broadcast_param(self) -> str | None:
        if 'broadcast' not in (self.start_param or ""):
            return None

        return self.start_param

    @computed_field
    def referral(self) -> int | None:
        if REFERRAL_PREFIX not in (self.start_param or ""):
            return None

        try:
            return int(self.start_param.replace('pilot_', ""))
        except Exception as e:
            logging.error(f"Failed to parse referral from start_param: {self.start_param}, error: {e}")
            return None
