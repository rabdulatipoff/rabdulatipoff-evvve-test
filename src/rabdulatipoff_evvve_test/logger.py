"""The logging facilities for the application modules."""

import logging
import logging.config

from pydantic import BaseModel


class LogConfig(BaseModel):
    """Logging configuration for the application instance."""

    LOGGER_NAME: str = "app"
    LOG_FORMAT: str = "%(levelprefix)s | %(asctime)s | %(message)s"
    LOG_LEVEL: str = "DEBUG"

    # Logging config
    version: int = 1
    disable_existing_loggers: bool = False
    formatters: dict = {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": LOG_FORMAT,
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    }
    handlers: dict = {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
    }
    loggers: dict = {
        LOGGER_NAME: {"handlers": ["default"], "level": LOG_LEVEL},
    }


def get_logger():
    config = LogConfig()
    logging.config.dictConfig(config.dict())
    logger = logging.getLogger(config.LOGGER_NAME)

    return logger


logger = get_logger()
