import logging

from starlette.config import Config
from starlette.datastructures import Secret

config: Config = Config(".env")

# Logging configurations.
LOGGING_DEBUG: bool = config("LOGGING_DEBUG", cast=bool, default=False)
LOG_TO_FILE: bool = config("LOG_TO_FILE", cast=bool, default=True)
LOGGING_LEVEL: int = logging.DEBUG if LOGGING_DEBUG else logging.INFO

BINANCE_API_KEY: Secret = config("BINANCE_API_KEY", cast=Secret)
BINANCE_API_SECRET: Secret = config("BINANCE_API_SECRET", cast=Secret)
