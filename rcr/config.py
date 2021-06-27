"""Config file."""
import os

from rcr.type import Protocol

SERVER_HOST = os.environ.get("SERVER_HOST", "127.0.0.1")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "9171"))
CONNECTION_DRIVER = os.environ.get("CONNECTION_DRIVER", "socket")
CONNECTION_PROTOCOL = getattr(Protocol, os.environ.get("CONNECTION_PROTOCOL", "TCP"))
LOGGING = {
    "version": 1,
    "formatters": {"default": {"format": "%(asctime)s: %(message)s"}},
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "level": os.environ.get("LOG_LEVEL", "INFO"),
        }
    },
    "loggers": {
        "root": {
            "handlers": ["console"],
            "level": os.environ.get("LOG_LEVEL", "INFO"),
        }
    },
}
