"""Message actor implementation."""
from datetime import datetime
from typing import Dict, Union

from .base import Base


class Message(Base):

    """Message actor class implementation.

    This actor is responsible to send a message to a connected client.
    """

    def process(self, data: Dict[str, Union[str, int]]):
        """Message format logic.

        Args:
            data (Dict[str, Union[str, int]]): data.
                schema: {"text": "str", "client_id": int, "sender_id": int, "status": "ok|error"}.
                Note: sender_id is optional.
        """
        if data["client_id"]:
            client_ids = [data["client_id"]]
        else:
            client_ids = self.manager._contact.list()

        for client_id in client_ids:
            # Send a message to a client.
            client_connection = self.manager._contact.get(client_id)
            if data.get("sender_id"):
                self.manager._connection.send(
                    client_connection,
                    "{} {} {}\r\n".format(
                        datetime.now(), data["sender_id"], data["text"]
                    ),
                )
            else:
                self.manager._connection.send(
                    client_connection,
                    "{}\r\n".format(data["text"]),
                )

        # Notify sender about its delivered message.
        if data.get("sender_id"):
            sender_connection = self.manager._contact.get(data["sender_id"])
            self.manager._connection.send(
                sender_connection, "your message has been delivered\r\n"
            )
