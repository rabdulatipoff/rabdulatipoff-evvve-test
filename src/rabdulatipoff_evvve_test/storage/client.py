import json
from typing import Iterable
from .schemas import CoinPricePoint
from .cache import Cache
from ..parser import ExchangeAPIParser
from ..config import default_quote_coin


class PricesClient:
    @staticmethod
    async def get_all(quote_coin: str = default_quote_coin) -> Iterable[CoinPricePoint]:
        return await ExchangeAPIParser.parse(quote_coin=quote_coin)

    @staticmethod
    async def get_by_coin_name(
        base_coin: str, quote_coin: str = default_quote_coin
    ) -> CoinPricePoint | None:
        pair_name = base_coin.upper() + quote_coin.upper()
        quote_pairs = json.loads(await Cache.get(quote_coin) or "[]")
        if not quote_pairs:
            # Parse the exchanges and update the coin index
            await ExchangeAPIParser.parse(quote_coin=quote_coin)

        if pair_name in quote_pairs:
            price = json.loads(await Cache.get(Cache.get_path(pair_name)) or "{}")
            if not price:
                return None

            return CoinPricePoint(**price)
        return None
