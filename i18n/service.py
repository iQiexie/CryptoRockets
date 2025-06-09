import os

import structlog
from pydantic_core import from_json

logger = structlog.stdlib.get_logger()


class I18n:
    def __init__(self):
        self._translations: [str, str] = {}
        self._load_translations()

    def get_translations(self) -> dict:
        return self._translations

    def _load_translations(self) -> None:
        translations_dir = "i18n/translations"

        for filename in os.listdir(translations_dir):
            if not filename.endswith(".json"):
                continue

            file_path = os.path.join(translations_dir, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                language_code = filename.split(".")[0]

                try:
                    self._translations[language_code] = from_json(f.read())
                except Exception as e:
                    logger.error(f"Failed to load language {language_code}: {e}")

    @property
    def languages(self) -> list[str]:
        return list(self._translations.keys())

    def t(self, message: str, lang: str) -> str:
        translation = self._translations.get(lang, {}).get(message)
        if translation:
            return translation

        return self._translations.get("en", {}).get(message, message)
