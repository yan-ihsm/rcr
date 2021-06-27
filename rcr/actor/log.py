"""Log actor implementation."""
from typing import Dict, Union

from .base import Base


class Log(Base):
    """Log actor class implementation.

    This actor is responsible to log whatever it receives
    based on defined log type.
    """

    def process(self, msg: Dict[str, Union[str, int]]):
        """Message format logic.

        Args:
            msg (Dict[str, Union[str, int]]): message.
                schema: {"type": "str", "text": "str"}.
                type: debug, info, or error.

        Raises:
            TypeError: when log type is invalid.
        """
        log_type = msg["type"]
        if not isinstance(log_type, str):
            raise TypeError(f"invalid log type. str expected but got {type(log_type)}")

        log_method = {
            "error": self._log.error,
            "debug": self._log.debug,
            "info": self._log.info,
        }[log_type]
        log_method(msg["text"])
