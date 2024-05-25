"""Configuration definitions and options for the application.
"""

import os
from typing import NamedTuple
from dotenv import load_dotenv


class EndpointOptions(NamedTuple):
    """The exchange API endpoint options.

    Attrs:
        name (str): The name of the exchange.
        url (str): The API endpoint URL.
        key (str): The JSON key for the `last_price` response value.
    """

    name: str
    url: str
    key: str


load_dotenv()

MEMCACHE_CONFIG: dict = {
    "address": os.getenv("MEMCACHED_ADDRESS", "127.0.0.1"),
    "port": int(os.getenv("MEMCACHED_PORT", str(11211))),
    # Connection timeout (seconds)
    "connect_timeout": float(os.getenv("MEMCACHED_CONNECT_TIMEOUT", str(10))),
    # Request timeout (seconds)
    "timeout": float(os.getenv("MEMCACHED_TIMEOUT", str(5))),
}
# Cached data expiration period (seconds)
CACHE_EXPIRATION: int = 30

API_PREFIX: str = "/api"
PARSE_ENDPOINTS: list[EndpointOptions] = [
    EndpointOptions("binance", "https://api.binance.com/api/v3/ticker/price", "price"),
    EndpointOptions("bybit", "https://api.bybit.com/v2/public/tickers", "last_price"),
]

DEFAULT_BASE_COIN: str = "BTC"
DEFAULT_QUOTE_COIN: str = "USDT"
