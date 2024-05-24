import json
from typing import Iterable
from rabdulatipoff_evvve_test.storage.schemas import CoinPricePoint
from rabdulatipoff_evvve_test.storage.cache import Cache
from rabdulatipoff_evvve_test.api.parser import ExchangeAPIParser
from rabdulatipoff_evvve_test.config import default_quote_coin


class PricesClient:
    @staticmethod
    async def get_all(quote_coin: str = default_quote_coin) -> Iterable[CoinPricePoint]:
        return await ExchangeAPIParser.parse(quote_coin=quote_coin)

    @staticmethod
    async def get_by_coin_name(
        base_coin: str, quote_coin: str = default_quote_coin
    ) -> CoinPricePoint | None:
        coin_name = base_coin.upper()
        available_coins = json.loads(await Cache.get(quote_coin) or "[]")
        if not available_coins:
            # Parse the exchanges and update the coin index
            await ExchangeAPIParser.parse(quote_coin=quote_coin)

        if coin_name in available_coins:
            price = json.loads(
                await Cache.get(Cache.get_path((quote_coin, coin_name))) or "{}"
            )
            if not price:
                return None

            return CoinPricePoint(**price)
