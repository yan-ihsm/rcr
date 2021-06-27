"""List of custom types."""
from enum import Enum
from socket import SOCK_DGRAM, SOCK_STREAM


class Protocol(Enum):
    """Protocols."""

    TCP = SOCK_STREAM
    UDP = SOCK_DGRAM


class ConnectionEvent(Enum):
    """Connection events."""

    ON_BIND = 1  # callback parameters: (socket object)
    ON_CONNECT = 2  # callback parameters: (socket object)
    ON_DISCONNECT = 3  # callback parameters: (socket object)
    ON_JOIN = 4  # callback parameters: (socket object, address tuple)
    ON_MESSAGE = 5  # callback parameters: (socket object, payload str)
