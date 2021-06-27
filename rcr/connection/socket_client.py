"""Socket client implementation."""
import selectors
import socket

from rcr.exception import CloseConnectionError, ConnectionError
from rcr.type import ConnectionEvent

from .base_client import BaseClient


class SocketClient(BaseClient):
    """Socket client implementation class."""

    def __init__(self, *args, **kwargs):
        self._selector = selectors.DefaultSelector()
        super().__init__(*args, **kwargs)

    def connect(self):
        """Connect to a port to send requests."""
        self._conn = socket.socket(socket.AF_INET, self.protocol.value)
        try:
            self._conn.connect((self.host, self.port))
        except OSError as e:
            self.close()
            raise ConnectionError(str(e))
        self._conn.setblocking(False)
        self._selector.register(self._conn, selectors.EVENT_READ, self.receive)

        # Event callback.
        self.event_callback[ConnectionEvent.ON_CONNECT](self._conn)

        self._mainloop()

    def _mainloop(self):
        """Start listening to events and trigger related methods.

        Note:
            It blocks the process, so, it should be executed in a seperate thread.
        """
        while not self._shutdown:
            events = self._selector.select(timeout=0.01)
            for key, _ in events:
                key.data(key.fileobj)
        self.close()

    def close(self):
        """Close the connection."""
        if self._conn:
            try:
                self._selector.unregister(self._conn)
                self._conn.close()
            except Exception as e:  # TODO: no general exception!
                raise CloseConnectionError(str(e))
        self._selector.close()

        # Event callback.
        self.event_callback[ConnectionEvent.ON_DISCONNECT](self._conn)

    def send(self, message: str):
        """Send a message."""
        self._conn.sendall(message.encode())

    def receive(self, sock: socket.socket):
        """Receive messages."""
        data = sock.recv(1024)
        if not data:
            return

        try:
            message = data.decode().strip()
        except UnicodeDecodeError:
            message = str(data)

        # Event callback.
        self.event_callback[ConnectionEvent.ON_MESSAGE](sock, message)
