"""Resource manager module."""
import logging.config
import signal
from collections import defaultdict
from threading import Thread
from typing import Any, Tuple

from rcr.actor import CommandActor, LogActor, MessageActor, SessionActor
from rcr.config import LOGGING
from rcr.connection.connection import new_connection
from rcr.contact import Contact
from rcr.type import ConnectionEvent

logging.config.dictConfig(LOGGING)


class Manager:
    """Resource Manager class."""

    _actors_threads = []
    _connection_thread = None

    def __init__(self, is_server: bool = False):
        """Init class.

        Args:
            is_server (bool): is in server mode.
        """
        self.is_server = is_server
        self._contact = Contact()

        # Actor.
        self._log_actor = LogActor(self)
        self._session_actor = SessionActor(self)
        self._command_actor = CommandActor(self)
        self._message_actor = MessageActor(self)
        self._actor_thread = Thread(target=self.start_actors)
        self._actor_thread.start()

        # Connection.
        # TODO: Need a little cleanup.
        event_callback = defaultdict(
            # FIXME: this needs to be better implemented.
            lambda: lambda *args: None,
            {
                ConnectionEvent.ON_DISCONNECT: self.disconnect,
            },
        )
        if not is_server:
            event_callback[ConnectionEvent.ON_MESSAGE] = self.receive_message_client
            self._connection = new_connection(self.is_server, event_callback)
            self._connection_thread = Thread(target=self._connection.connect)
        else:
            event_callback[ConnectionEvent.ON_MESSAGE] = self.receive_message_server
            event_callback[ConnectionEvent.ON_JOIN] = self.add_new_client
            self._connection = new_connection(self.is_server, event_callback)
            self._connection_thread = Thread(target=self._connection.bind)
        self._connection_thread.start()

    def disconnect(self, sock: Any):
        """Disconnect event callback."""
        self._log_actor.inbox.put({"type": "info", "text": "Connection closed!"})

    def start_actors(self):
        """Start actors."""
        self._actors_threads.extend(
            [
                Thread(target=self._log_actor.start),
                Thread(target=self._session_actor.start),
                Thread(target=self._command_actor.start),
                Thread(target=self._message_actor.start),
            ]
        )
        for actor_thread in self._actors_threads:
            actor_thread.start()

    def add_new_client(self, conn: Any, addr: Tuple[str, int]):
        """Receives a new message from client.

        Args:
            conn (Any): connection object.
            addr (Tuple[str, int]): connection address.
        """
        self._session_actor.inbox.put({"addr": addr, "conn": conn})

    def receive_message_server(self, conn: Any, message: str):
        """Receives a new message from client.

        Args:
            conn (Any): connection object.
            message (str): payload.
        """
        self._command_actor.inbox.put({"text": message, "conn": conn})

    def receive_message_client(self, conn: Any, message: str):
        """Receives a new message from server.

        Args:
            conn (Any): connection object.
            message (str): payload.
        """
        print(message)
        # self._command_actor.inbox.put({"text": message, "conn": conn})

    def shutdown(self):
        """Shutdown all resources."""
        self._log_actor.shutdown()
        self._session_actor.shutdown()
        self._command_actor.shutdown()
        self._message_actor.shutdown()
        self._connection.shutdown()

    def start(self):
        """Start manager service."""
        print("Server is ready to serve requests.")
        self._connection_thread.join()
        for actor_thread in self._actors_threads:
            actor_thread.join()
        signal.pause()
