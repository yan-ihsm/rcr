"""Command actor implementation."""
import re
import urllib.request
from typing import Any, Dict, Union

from .base import Base

DIRECT_MESSAGE_PATTERN = re.compile("msg (?P<client_id>\\d+) (?P<message>.+)")
BROADCAST_MESSAGE_PATTERN = re.compile("broadcast (?P<message>.+)")
URL_MESSAGE_PATTERN = re.compile("url (?P<client_id>\\d+) (?P<url>.+)")
FIB_MESSAGE_PATTERN = re.compile("fib (?P<client_id>\\d+) (?P<n>\\d+)")


class Command(Base):
    """Command actor class implementation.

    This actor is responsible to parse raw text (client text) and
    dispatch it to related actors.
    """

    def _direct_message(self, text: str, sender_id: int) -> Dict[str, Union[str, int]]:
        """Direct message handler.

        Args:
            text (str): received direct text.
            sender_id (int): the client ID who sent the message.

        Returns:
            Dict[str, Union[str, int]]: genereted response message.

        """
        match = DIRECT_MESSAGE_PATTERN.match(text)
        if match:
            match_groups = match.groupdict()
            return {
                "client_id": int(match_groups["client_id"]),
                "text": match_groups["message"],
                "sender_id": sender_id,
            }
        return {
            "client_id": sender_id,
            "text": "invalid format to send a message!",
        }

    def _clients_list(self, sender_id: int) -> Dict[str, Union[str, int]]:
        """Client list message handler.

        Args:
            sender_id (int): the client ID who sent the message.

        Returns:
            Dict[str, Union[str, int]]: genereted response message.
        """
        return {
            "client_id": sender_id,
            "text": "\r\n".join(map(str, self.manager._contact.list())),
        }

    def _broadcast_message(
        self, text: str, sender_id: int
    ) -> Dict[str, Union[str, int]]:
        """Broadcast message handler.

        Args:
            text (str): received broadcast text.
            sender_id (int): the client ID who sent the message.

        Returns:
            Dict[str, Union[str, int]]: genereted response message.
        """
        match = BROADCAST_MESSAGE_PATTERN.match(text)
        if match:
            match_groups = match.groupdict()
            return {
                "client_id": "",
                "text": match_groups["message"],
                "sender_id": sender_id,
            }
        return {
            "client_id": sender_id,
            "text": "invalid format to broadcast a message!",
        }

    def _url_message(self, text: str, sender_id: int) -> Dict[str, Union[str, int]]:
        """URL message handler.

        Args:
            text (str): received URL text.
            sender_id (int): the client ID who sent the message.

        Returns:
            Dict[str, Union[str, int]]: genereted response message.
        """
        match = URL_MESSAGE_PATTERN.match(text)
        if match:
            match_groups = match.groupdict()
            try:
                request = urllib.request.Request(match_groups["url"], method="GET")
            except Exception as e:
                return {
                    "client_id": sender_id,
                    "text": "request has failed: {}".format(e),
                }
            with urllib.request.urlopen(request) as resp:
                return {
                    "client_id": int(match_groups["client_id"]),
                    "text": str(len(resp.read())),
                    "sender_id": sender_id,
                }
        return {
            "client_id": sender_id,
            "text": "invalid message format to send url size!",
        }

    @staticmethod
    def _fib_impl1(n: int) -> int:
        """Fibonacci calculation - another implementation.

        Args:
            n (int): nth number of Fibonacci's series.

        Returns:
            int: calculated nth number of the Fibonacci's series.
        """
        first = 0
        second = 1
        while n >= 2:
            second, first = first + second, second
            n -= 1
        return second

    @staticmethod
    def _fib(n: int, first: int = 0, second: int = 1) -> int:
        """Fibonacci calculation.

        Args:
            n (int): nth number of Fibonacci's series.
            first (int): first number.
            second (int): second number.

        Returns:
            int: calculated nth number of the Fibonacci's series.
        """
        if n < 2:
            return second
        return Command._fib(n - 1, second, first + second)

    def _fib_message(self, text: str, sender_id: int) -> Dict[str, Union[str, int]]:
        """Fibonacci message handler.

        Args:
            text (str): received fibonacci text.
            sender_id (int): the client ID who sent the message.

        Returns:
            Dict[str, Union[str, int]]: genereted response message.
        """
        match = FIB_MESSAGE_PATTERN.match(text)
        if match:
            match_groups = match.groupdict()
            return {
                "client_id": int(match_groups["client_id"]),
                "text": str(self._fib(int(match_groups["n"]))),
                "sender_id": sender_id,
            }
        return {
            "client_id": sender_id,
            "text": "invalid message format to calculate fibonacci!",
        }

    def process(self, data: Dict[str, Union[str, Any]]):
        """Message format logic.

        Args:
            data (Dict[str, str]): data.
                schema: {"text": "str", "conn": Any}.
        """
        sender_id = self.manager._contact.get_by_connection(data["conn"])

        if data["text"].startswith("msg"):
            response = self._direct_message(data["text"], sender_id)
        elif data["text"] == "w":
            response = self._clients_list(sender_id)
        elif data["text"].startswith("broadcast"):
            response = self._broadcast_message(data["text"], sender_id)
        elif data["text"].startswith("url"):
            response = self._url_message(data["text"], sender_id)
        elif data["text"].startswith("fib"):
            response = self._fib_message(data["text"], sender_id)
        else:
            response = {"client_id": sender_id, "text": "invalid message!"}

        self.manager._message_actor.inbox.put(response)
