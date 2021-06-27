"""Socket client unit tests."""
import selectors
import socket
import threading
import time
import unittest
from collections import defaultdict
from unittest.mock import Mock

from rcr.connection.socket_client import SocketClient
from rcr.type import ConnectionEvent, Protocol

PORT = 9081


selector = selectors.DefaultSelector()
shutdown = False


# Echo server.
def start_echo_server():
    with socket.socket(socket.AF_INET, Protocol.TCP.value) as sock:
        sock.setblocking(False)
        sock.bind(("", PORT))
        sock.listen(1)
        selector.register(sock, selectors.EVENT_READ, accept)

        while not shutdown:
            events = selector.select(timeout=0.01)
            for key, _ in events:
                key.data(key.fileobj)
        selector.unregister(sock)
    selector.close()


def accept(sock):
    conn, _ = sock.accept()
    conn.setblocking(False)
    selector.register(conn, selectors.EVENT_READ, receive_and_reply)


def receive_and_reply(sock):
    data = sock.recv(1024)
    if data:
        sock.sendall(data)
    selector.unregister(sock)
    sock.close()


class TestSocketClient(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server_thread = threading.Thread(target=start_echo_server)
        cls.server_thread.start()
        time.sleep(1)  # just a short nap for the bind.

        events = defaultdict(lambda: lambda *args: 0)

        # Mock events.
        cls.event_on_connect = Mock()
        cls.event_on_disconnect = Mock()
        cls.event_on_message = Mock()

        events.update(
            {
                ConnectionEvent.ON_CONNECT: cls.event_on_connect,
                ConnectionEvent.ON_DISCONNECT: cls.event_on_disconnect,
                ConnectionEvent.ON_MESSAGE: cls.event_on_message,
            }
        )
        cls.client = SocketClient("127.0.0.1", PORT, Protocol.TCP, events)
        cls.client_thread = threading.Thread(target=cls.client.connect)
        cls.client_thread.start()

        time.sleep(1)  # just a short nap for the connection.

    @classmethod
    def tearDownClass(cls):
        global shutdown
        shutdown = True
        cls.server_thread.join()

    def test_1_on_connect(self):
        self.event_on_connect.assert_called_once_with(self.client._conn)

    def test_3_on_message(self):
        self.client.send("test123")
        time.sleep(1)  # a short nap for the message.
        self.event_on_message.assert_called_once_with(self.client._conn, "test123")

    def test_4_on_disconnect(self):
        self.client.shutdown = True
        self.client_thread.join()
        time.sleep(1)  # a short nap for the client to be stoped.
        self.event_on_disconnect.assert_called_once_with(self.client._conn)
