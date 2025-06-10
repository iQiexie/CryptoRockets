JWT_ALGORYTHM = "HS256"
POSTGRES_TIMEOUT = 60
DEFAULT_HTTP_TIMEOUT = 20

LOGGING_SENSITIVE_FIELDS = (
    "password",
    "token",
    "Authorization",
    "Authentication",
    "authorization",
    "authentication",
    "x-api-key",
    "x-cmc_pro_api_key",
)

LOGGING_SENSITIVE_REPLACEMENT = "******"

LOGGING_DISABLED_ENDPOINTS = ("/metrics",)
DEFAULT_LANGUAGE = "en"


ROCKET_CAPACITY_DEFAULT = 3
ROCKET_CAPACITY_OFFLINE = 6
ROCKET_CAPACITY_PREMIUM = 4

REFERRAL_PREFIX = "pilot_"
BOT_NAME = "CryptoRocketsBot"
WEBAPP_NAME = "launch"


MAX_BALANCE = 60
WHEEL_TIMEOUT = 60 * 3
