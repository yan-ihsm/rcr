"""Clients contact book manager."""
from __future__ import annotations

import time
from itertools import count
from threading import Lock, Thread
from typing import Any, Dict, List, Optional, Set, Tuple


class Contact:
    """Client contact book manager.

    It adds an auto-increment number for each user.
    """

    __instance: Optional[Contact] = None
    __counter = count(start=1)
    __released_counters: Set[int] = set()
    __lock = Lock()
    __thread = None

    @classmethod
    def get_instance(cls) -> Contact:
        if cls.__instance is None:
            cls.__instance = Contact()
        return cls.__instance

    def __init__(self):
        self._contact_book: Dict[int, Tuple[Tuple[str, int], Any]] = {}

        # Cleanup thread needs to be implemented.
        Contact.__thread = Thread(target=self._check_client_availability)
        # Contact.__thread.start()

    def add(self, connection_info: Tuple[Tuple[str, int], Any]) -> int:
        """Add a new client.

        Args:
            connection_info (Tuple[Tuple[str,int],Any]): client connection info.

        Returns:
            int: a new client ID.

        Todo:
            This method needs to be implemented in a better way to handle exceptions.
        """
        with Contact.__lock:
            if Contact.__released_counters:
                contact_id = Contact.__released_counters.pop()
            else:
                contact_id = next(Contact.__counter)
            if contact_id not in self._contact_book:
                self._contact_book[contact_id] = connection_info
            elif self._contact_book[contact_id] == connection_info:
                return contact_id
            else:
                raise SystemError("Can't add a new client in the contact book.")
            return contact_id

    def remove(self, contact_id: int) -> bool:
        """Remove a client.

        Args:
            contact_id (int): client's contact ID.

        Returns:
            bool: removing contact record was successful or not.
        """
        with Contact.__lock:
            if contact_id in self._contact_book:
                del self._contact_book[contact_id]
                Contact.__released_counters.add(contact_id)
                return True
        return False

    def list(self) -> List[int]:
        """Return list of recorded clients.

        Returns:
            List[int]: list of recorded clients.
        """
        return list(self._contact_book.keys())

    def get(self, contact_id: int) -> Optional[Tuple[Tuple[str, int], Any]]:
        """Get a client's connection info.

        Args:
            contact_id (int): client's contact ID.

        Returns:
            Optional[Tuple[Tuple[str, int], Any]]: a client's connection info.
        """
        return self._contact_book.get(contact_id)

    def get_by_connection(self, connection: Any):
        """Get client ID by connection object."""
        for client_id, connection_info in self._contact_book.items():
            if connection_info[1] == connection:
                return client_id
        raise ValueError("client with connection object %s not found.", connection)

    def _check_client_availability(self):
        """Check contact book and removed disconnected clients."""
        while True:  # FIXME: need to support gracefully shutdown.
            for client_id, connection_info in self._contact_book.items():
                print(connection_info[1])  # TODO: needs to be implemented.
            time.sleep(0.5)
