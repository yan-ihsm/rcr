"""Session actor implementation."""
from typing import Any, Dict

from rcr.actor.base import Base


class Session(Base):
    """Session actor class implementation.

    This actor is responsible to manage sessions by keeping contact book updated.
    """

    def process(self, msg: Dict[str, Any]):
        """Message format logic.

        Args:
            msg (Dict[str, Union[str, Any]]): message.
                schema: {"addr": "str", "conn": Any}.
        """
        # Add the client in the contact book.
        client_id = self.manager._contact.add((msg["addr"], msg["conn"]))

        # Log on the server.
        self.manager._log_actor.inbox.put(
            {"type": "info", "text": "user has been added to the contact list."}
        )

        # Reply to the user about its client ID.
        self.manager._message_actor.inbox.put(
            {"text": "Your client ID: {}\r\n".format(client_id), "client_id": client_id}
        )
