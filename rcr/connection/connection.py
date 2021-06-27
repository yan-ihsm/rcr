"""Connection wrapper library."""
import importlib
from typing import Callable, DefaultDict, Optional

from rcr import config
from rcr.type import ConnectionEvent


def new_connection(
    is_server: bool = False,
    event_callback: Optional[DefaultDict[ConnectionEvent, Callable]] = None,
):
    """Create new connection driver.

    Args:
        is_server (bool): the connection should be in a server mode or not. Defaults to None.
        event_callback (Optional[DefaultDict[ConnectionEvent, Callable]]): connection events
            callback. Defaults to None.

    Returns:
        Base: a new connection driver instance.
    """
    if not is_server:
        module = "rcr.connection.{}_client".format(config.CONNECTION_DRIVER)
        cls_name = "{}Client".format(config.CONNECTION_DRIVER.title())
    else:
        module = "rcr.connection.{}_server".format(config.CONNECTION_DRIVER)
        cls_name = "{}Server".format(config.CONNECTION_DRIVER.title())

    imp = importlib.import_module(module, cls_name)
    cls = getattr(imp, cls_name)

    return cls(
        config.SERVER_HOST,
        config.SERVER_PORT,
        config.CONNECTION_PROTOCOL,
        event_callback,
    )
