import emcache
from typing import Iterable
from contextlib import asynccontextmanager
from rabdulatipoff_evvve_test.config import memcache_config, cache_expiration


class Cache:
    key_delimiter = "."

    @staticmethod
    @asynccontextmanager
    async def memcache_client(
        addr: str = memcache_config["address"],
        port: int = memcache_config["port"],
        connect_timeout: float = memcache_config["connect_timeout"],
        timeout: float = memcache_config["timeout"],
        *args,
        **kwargs,
    ):
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
    def get_path(cls, keys: str | Iterable[str], prefix: str = "prices"):
        path = [prefix]
        if type(keys) is str:
            path.append(keys)
        else:
            path.extend(keys)

        return cls.key_delimiter.join(path)

    @classmethod
    async def get(cls, key: str, json: bool = True, *args, **kwargs) -> str | None:
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
        exptime=cache_expiration,
        *args,
        **kwargs,
    ) -> None:
        async with cls.memcache_client() as cache:
            try:
                await cache.set(
                    key=key.encode("utf-8"),
                    value=value.encode("utf-8"),
                    exptime=exptime,
                    *args,
                    **kwargs,
                )
            except emcache.StorageCommandError:
                raise Exception(f"Could not set value for key '{key}'")
