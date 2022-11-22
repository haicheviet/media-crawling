import os

level_log = "INFO" if os.getenv("APP_ENV") != "test" else "DEBUG"
BASE_LOGGER = {
    "version": 1,
    # Separate uvicorn log and custom log
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
        "fast_api": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
    },
    "loggers": {"app.main": {"handlers": ["fast_api"], "level": "INFO"}},
}
