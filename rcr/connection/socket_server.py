"""Socket server implementation."""
import selectors
import socket
from typing import Any, Tuple

from rcr.exception import BindError, CloseBindError, CloseConnectionError
from rcr.type import ConnectionEvent

from .base_server import BaseServer


class SocketServer(BaseServer):
    """Socket server implementation class."""

    def __init__(self, *args, **kwargs):
        self._selector = selectors.DefaultSelector()
        super().__init__(*args, **kwargs)

    def bind(self):
        """Bind a specific port."""
        self._conn = socket.socket(socket.AF_INET, self.protocol.value)
        try:
            self._conn.bind((self.host, self.port))
        except OSError as e:
            self.close()
            raise BindError(str(e))
        self._conn.setblocking(False)
        self._conn.listen(100)
        self._selector.register(self._conn, selectors.EVENT_READ, self.accept)

        # Event callback.
        self.event_callback[ConnectionEvent.ON_BIND](self._conn)

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

    def accept(self, sock):
        """Accept a socket connection.

        Args:
            sock (socket.socket): a socket connection.
        """
        conn, addr = sock.accept()
        conn.setblocking(False)
        self._selector.register(conn, selectors.EVENT_READ, self.receive)

        # Event callback.
        self.event_callback[ConnectionEvent.ON_JOIN](conn, addr)

    def close(self):
        """Close the bound connection."""
        if self._conn:
            try:
                self._conn.close()
            except Exception as e:  # TODO: no general exception!
                raise CloseBindError(str(e))

        # Event callback.
        self.event_callback[ConnectionEvent.ON_DISCONNECT](self._conn)

    def close_connection(self, conn: socket.socket):
        """Close and unregister a specific connection."""
        try:
            self._selector.unregister(conn)
            conn.close()
        except Exception as e:
            raise CloseConnectionError(str(e))

    def send(self, user_connection: Tuple[Tuple[str, int], Any], message: str):
        """Send a message to a user connection.

        Args:
            user_connection (Tuple[Tuple[str, int], Any]): user connection info.
            message (str): message payload.
        """
        user_connection[1].sendall(message.encode())

    def receive(self, sock: socket.socket):
        """Receive a message in a connection.

        Args:
            sock (socket.socket): a socket connection.
        """
        data = sock.recv(1024)
        if not data:
            return

        try:
            message = data.decode().strip()
        except UnicodeDecodeError:
            message = str(data)

        # Event callback.
        self.event_callback[ConnectionEvent.ON_MESSAGE](sock, message)
