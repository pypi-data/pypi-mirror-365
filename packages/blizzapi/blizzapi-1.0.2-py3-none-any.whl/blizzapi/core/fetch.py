from collections.abc import Callable
from functools import wraps
from typing import TYPE_CHECKING

from blizzapi.core.oauth2_client import OAuth2Client

if TYPE_CHECKING:
    from blizzapi.core.base_client import BaseClient


class Fetch:
    def __init__(self, namespace_type: str):
        self.namespace_type = namespace_type

    def fetch(self, command_uri: str):  # noqa: ANN201
        def wrapped(func: Callable):  # noqa: ANN202
            @wraps(func)
            def wrapped(*args: tuple, **kwargs: dict) -> dict:
                if not isinstance(args[0], OAuth2Client):
                    msg = "First argument must be an instance of OAuth2Client"
                    raise TypeError(msg)
                client: BaseClient = args[0]
                uri = client.build_uri(command_uri, self.namespace_type, func, args, kwargs)

                return client.get(uri)

            return wrapped

        return wrapped


dynamic = Fetch("dynamic").fetch
profile = Fetch("profile").fetch
static = Fetch("static").fetch
