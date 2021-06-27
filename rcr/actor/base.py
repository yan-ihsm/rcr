"""Base actor module."""
import logging
import time
from abc import ABCMeta, abstractmethod
from queue import Empty, Queue
from threading import Thread
from typing import Dict, Union


class Base(metaclass=ABCMeta):
    """Base actor class."""

    def __init__(self, manager):
        """Python Built-in method.

        Args:
            manager (Manager): manager instance.
        """
        self.manager = manager

        self._shutdown = False
        self.inbox = Queue()
        self._start_thread = None

        self._log = logging.getLogger("actor")

    def start(self):
        """Start running the actor."""
        self._start_thread = Thread(target=self.receiver)
        self._start_thread.start()

    def shutdown(self):
        """Triggers the shutdown flag."""
        self._shutdown = True

    @abstractmethod
    def process(self, msg: Dict[str, Union[str, int]]):
        """Message format logic.

        Args:
            msg (Dict[str, Union[str, int]]): message.

        Note:
            It can put a message to other actors.
        """

    def receiver(self):
        """Receive message and pass it to process."""
        while not self._shutdown:
            try:
                item = self.inbox.get_nowait()
            except Empty:
                time.sleep(0.1)
                continue

            # Ignore empty messages.
            if not item:
                continue

            # Actor should be stopped.
            if item == "shutdown":
                break

            # Process a received message.
            try:
                self.process(item)
            except Exception as e:
                self._log.error(
                    f"Process has failed on {self.__class__.__name__} actor: {e}"
                )
                raise
