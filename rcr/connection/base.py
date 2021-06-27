"""Abstract Connection class.

All connection classes must implement this class.
"""
from abc import ABCMeta, abstractmethod
from collections import defaultdict
from typing import Callable, DefaultDict, Optional

from rcr.type import ConnectionEvent, Protocol


class Base(metaclass=ABCMeta):
    """Base MQ class."""

    def __init__(
        self,
        host: str,
        port: int,
        protocol: Protocol,
        event_callback: Optional[DefaultDict[ConnectionEvent, Callable]] = None,
        **kwargs
    ):
        """Initialize the class.

        Args:
            host (str): host address.
            port (int): port number.
            protocol (Protocol): protocol type.
            event_callback (Optional[DefaultDict[ConnectionEvent, Callable]]): connection events
                callback. Defaults to None.
            **kwargs: any extra config to establish a connection.
        """
        self.host = host
        self.port = port
        self.protocol = protocol
        self.event_callback = self._update_event_callback(event_callback)

        # Extra attributes.
        for key, value in kwargs.items():
            setattr(self, key, value)

        self._conn = None

        # It's for telling to connections to stop streaming.
        self._shutdown = False

        # Pre-defined steps.
        self.validate_port()
        self.check_permission()
        self.check_availability()
        self.setup()

    def shutdown(self):
        """Triggers the shutdown flag."""
        self._shutdown = True

    def _update_event_callback(
        self, event_callback: Optional[DefaultDict[ConnectionEvent, Callable]]
    ) -> Optional[DefaultDict[ConnectionEvent, Callable]]:
        """Update event callback to support undefined events.

        Args:
            event_callback (Optional[DefaultDict[ConnectionEvent, Callable]]): event callback.

        Returns:
            event_callback (Optional[DefaultDict[ConnectionEvent, Callable]]): updated
                events callback.

        Raises:
            TypeError: if event_callbaack is not 'defaultdict' or the default factory is not
                callable.
        """
        if event_callback:
            if not isinstance(event_callback, defaultdict):
                raise TypeError("event_callback must be in a defaultdict type.")
            if not isinstance(event_callback.default_factory(), Callable):
                raise TypeError(
                    "event_callback default type must be in a callable type."
                )
            tmp_event_callback = event_callback.copy()

            # Add undefined events.
            for event in ConnectionEvent:
                if event.name not in tmp_event_callback:
                    tmp_event_callback[event.value] = lambda *args, **kwargs: None
            return tmp_event_callback

        # Default callable dictionary.
        return defaultdict(lambda: lambda *args, **kwargs: None)

    def setup(self):
        """Custom init method for derived classes.

        Note:
            This method can be overridden if needed.
        """
        pass

    def validate_port(self):
        """Validate port.

        Raises: ValueError when port is not in a valid range.
        """
        if self.port < 1 or self.port > 65535:
            raise ValueError("port is not in a valid range.")

    def check_permission(self):
        """Check permission on a specific port range.

        Note:
            This method can be overridden if needed.
        """
        pass

    @abstractmethod
    def check_availability(self):
        """Check resource availability."""
        pass
