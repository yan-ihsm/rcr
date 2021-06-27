"""Abstract client class.

All client connection classes must implement this class.
"""
import socket
from abc import abstractmethod
from typing import Callable, NoReturn

from .base import Base


class BaseClient(Base):
    """Base MQ client class."""

    def check_availability(self):
        """Check resource availability.

        Raises: ConnectionError when resources are already used.
        """
        sock_obj = socket.socket(socket.AF_INET, self.protocol.value)
        if sock_obj.connect_ex((self.host, self.port)) != 0:
            raise ConnectionError(
                "%s:%s is not available." % (self.host or "*", self.port)
            )
        sock_obj.close()

    @abstractmethod
    def connect(self):
        """Connect to a port to send requests.

        Raises:
            ConnectError if it can't connect to a server.
        """

    @abstractmethod
    def close(self):
        """Close the connection.

        Raises:
            CloseConnectionError if closing a connection has failed.
        """

    @abstractmethod
    def send(self, message: str) -> bool:
        """Send a message.

        Args:
            message (str): message payload to be send.

        Returns:
            bool: sending process was successful or not.
        """

    @abstractmethod
    def receive(self, callback: Callable) -> NoReturn:
        """Receive messages.

        Args:
            callback (Callback): the method to be called in case of any new messages.
        """
