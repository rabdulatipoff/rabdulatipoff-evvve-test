"""Cache storage methods and exceptions.

Classes:
    Cache: The cache client class.

Exceptions:
    SetValueError:
"""

from typing import Iterable
from contextlib import asynccontextmanager

import emcache
from rabdulatipoff_evvve_test.config import MEMCACHE_CONFIG, CACHE_EXPIRATION


class SetValueError(Exception):
    """A cache key-value pair set/update error."""


class Cache:
    """The memcached client implementation class.

    Attrs:
        key_delimiter (str): The delimiter string for key flattening.
    """

    key_delimiter: str = "."

    @staticmethod
    @asynccontextmanager
    async def memcache_client(
        *args,
        addr: str = MEMCACHE_CONFIG["address"],
        port: int = MEMCACHE_CONFIG["port"],
        connect_timeout: float = MEMCACHE_CONFIG["connect_timeout"],
        timeout: float = MEMCACHE_CONFIG["timeout"],
        **kwargs,
    ):
        """The context manager for memcached async client.

        Args:
            addr (str): The memcached server address.
            port (int): The memcached server address.
            connect_timeout (float): The timeout for server connection requests.
            timeout (float): The timeout for cache querying operations.
        """

        client = await emcache.create_client(
            [
                emcache.MemcachedHostAddress(addr, port),
            ],
            connection_timeout=connect_timeout,
            timeout=timeout,
            autobatching=True,
            *args,
            **kwargs,
        )

        try:
            yield client
        finally:
            pass

    @classmethod
    def get_path(cls, keys: str | Iterable[str], prefix: str = "prices") -> str:
        """Construct a flattened path from keys.

        Args:
            keys (str | Iterable[str]): The key/sequence of ordered keys.
            prefix (str): The key path prefix.

        Returns:
            str: A key string in a flattened path format."""
        path = [prefix]
        if isinstance(keys, str):
            path.append(keys)
        else:
            path.extend(keys)

        return cls.key_delimiter.join(path)

    @classmethod
    async def get(cls, key: str, *args, **kwargs) -> str | None:
        """Get the value for a given `key`.

        Args:
            key (str): The cache key.

        Returns:
            str | None: The JSON data for the key, if defined.
        """

        async with cls.memcache_client() as cache:
            data = await cache.get(key.encode("utf-8"), *args, **kwargs)
            if data:
                return str(data.value, encoding="utf-8")
            return None

    @classmethod
    async def set(
        cls,
        key: str,
        value: str,
        *args,
        exptime=CACHE_EXPIRATION,
        **kwargs,
    ) -> None:
        """Set/update the `value` for a given `key`.

        Args:
            key (str): The cache key.
            value (str): The JSON data for storage.
        """

        async with cls.memcache_client() as cache:
            try:
                await cache.set(
                    key=key.encode("utf-8"),
                    value=value.encode("utf-8"),
                    exptime=exptime,
                    *args,
                    **kwargs,
                )
            except emcache.StorageCommandError as e:
                raise SetValueError(f"Could not set value for key '{key}'") from e
