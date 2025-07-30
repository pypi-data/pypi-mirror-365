### This is hydragram Released and maintained by @hasnainkk on TG!
"""
Created by @Endtrz 

- Supports message, callback_query, inline_query, and more.
- Integrates custom filters (dev_cmd, owner_cmd, gc_admin, etc.)
- Automatically registers with client if available.
- Enables clean decorator-based command routing.
"""


__version__ = "0.0.11"
__license__ = "GNU Lesser General Public License v3.0 (LGPL-3.0)"
__copyright__ = "Copyright (C) 2025-Endtrz<https://github.com/Endtrz>"

from concurrent.futures.thread import ThreadPoolExecutor


class StopTransmission(Exception):
    pass


class StopPropagation(StopAsyncIteration):
    pass


class ContinuePropagation(StopAsyncIteration):
    pass


from . import raw, types, filters, handlers, enums
from .client import Client
from .sync import idle, compose

crypto_executor = ThreadPoolExecutor(1, thread_name_prefix="CryptoWorker")
