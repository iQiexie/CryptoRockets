
import structlog

logger = structlog.stdlib.get_logger()


class I18n:
    def __init__(self):
        self._translations: [str, str] = {}
        self._load_translations()

    def get_translations(self) -> dict:
        return self._translations

    def _load_translations(self) -> None:
        return

    @property
    def languages(self) -> list[str]:
        return list(self._translations.keys())

    def t(self, message: str, lang: str) -> str:
        translation = self._translations.get(lang, {}).get(message)
        if translation:
            return translation

        return self._translations.get("en", {}).get(message, message)
