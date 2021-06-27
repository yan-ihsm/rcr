"""Abstract server class.

All server connection classes must implement this class.
"""
import os
import socket
from abc import abstractmethod
from collections import Callable
from typing import Any, NoReturn, Tuple

from .base import Base


class BaseServer(Base):
    """Base Connection server class."""

    def check_availability(self):
        """Check resource availability.

        Raises: ConnectionError when resources are already used.
        """
        sock_obj = socket.socket(socket.AF_INET, self.protocol.value)
        if sock_obj.connect_ex((self.host, self.port)) == 0:
            raise ConnectionError(
                "%s:%s is already used." % (self.host or "*", self.port)
            )
        sock_obj.close()

    def check_permission(self):
        """Check permission on a specific port range.

        Raises: SystemError when user has no superuser access for a range of ports.
        """
        if self.port < 1024 and os.getuid() != 0:
            raise PermissionError("permission denied to bind in this range of ports.")

    @abstractmethod
    def bind(self):
        """Bind a port to get requests.

        Raises:
            BindError if it can't bind a port.
        """

    @abstractmethod
    def close(self):
        """Close the connection.

        Raises:
            CloseBindError if closing a bind connection has failed.
        """

    @abstractmethod
    def close_connection(self, conn: Any):
        """Close and unregister a specific connection.

        Args:
            conn (Any): a connection object.

        Raises:
            CloseConnectionError: when can't close a connection.
        """

    @abstractmethod
    def send(self, user_connection: Tuple[Tuple[str, int], Any], message: str):
        """Send a message.

        Args:
            user_connection (Tuple[Tuple[str, int], Any]): user connection info.
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
