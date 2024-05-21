import os
from typing import NamedTuple
from dotenv import load_dotenv


class EndpointOptions(NamedTuple):
    name: str
    url: str
    key: str


load_dotenv()

memcache_config: dict = {
    "address": os.getenv("MEMCACHED_ADDRESS", "127.0.0.1"),
    "port": int(os.getenv("MEMCACHED_PORT", 11211)),
    # Connection timeout (seconds)
    "connect_timeout": float(os.getenv("MEMCACHED_CONNECT_TIMEOUT", 10)),
    # Request timeout (seconds)
    "timeout": float(os.getenv("MEMCACHED_TIMEOUT", 5)),
}
# Cached data expiration period (seconds)
cache_expiration: int = 30

api_prefix: str = "/api"
parse_endpoints: list[EndpointOptions] = [
    EndpointOptions("binance", "https://api.binance.com/api/v3/ticker/price", "price"),
    EndpointOptions("bybit", "https://api.bybit.com/v2/public/tickers", "last_price"),
]

default_base_coin: str = "BTC"
default_quote_coin: str = "USDT"
