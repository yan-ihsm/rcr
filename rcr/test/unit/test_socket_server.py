"""Socket server unit tests."""
import socket
import threading
import time
import unittest
from collections import defaultdict
from unittest.mock import Mock

from rcr.connection.socket_server import SocketServer
from rcr.type import ConnectionEvent, Protocol

PORT = 9095


class TestSocketServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        events = defaultdict(lambda: lambda *args: 0)

        # Mock events.
        cls.event_on_bind = Mock()
        cls.event_on_disconnect = Mock()
        cls.event_on_join = Mock()
        cls.event_on_message = Mock()

        events.update(
            {
                ConnectionEvent.ON_BIND: cls.event_on_bind,
                ConnectionEvent.ON_DISCONNECT: cls.event_on_disconnect,
                ConnectionEvent.ON_JOIN: cls.event_on_join,
                ConnectionEvent.ON_MESSAGE: cls.event_on_message,
            }
        )
        cls.server = SocketServer("", PORT, Protocol.TCP, events)
        cls.server_thread = threading.Thread(target=cls.server.bind)
        cls.server_thread.start()

        time.sleep(1)  # just a short nap for the bind.

        # Simple client.
        cls.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cls.client.connect(("127.0.0.1", PORT))

        time.sleep(1)  # just a short nap for the connection.

    def test_1_on_bind(self):
        self.event_on_bind.assert_called_once_with(self.server._conn)

    def test_2_on_join(self):
        self.event_on_join.assert_called_once()

    def test_3_on_message(self):
        self.client.sendall(b"test")
        time.sleep(1)  # a short nap for the message.
        self.event_on_message.assert_called_once()

    def test_4_on_disconnect(self):
        self.client.close()
        self.server.shutdown = True
        self.server_thread.join()
        time.sleep(1)  # a short nap for the server to be stoped.
        self.event_on_disconnect.assert_called_once_with(self.server._conn)
