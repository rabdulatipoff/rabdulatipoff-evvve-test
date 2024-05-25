"""Provides interfaces for price data query methods.

Classes:
    PricesClient: The interface class for querying price data.
"""

import json
from typing import Iterable
from rabdulatipoff_evvve_test.storage.schemas import CoinPricePoint
from rabdulatipoff_evvve_test.storage.cache import Cache
from rabdulatipoff_evvve_test.api.parser import ExchangeAPIParser
from rabdulatipoff_evvve_test import config


class PricesClient:
    """The interface class for price parsing/fetching methods."""

    @staticmethod
    async def get_all(
        quote_coin: str = config.DEFAULT_QUOTE_COIN,
    ) -> Iterable[CoinPricePoint]:
        """Get all available coin prices.

        Args:
            quote_coin (str): The quote coin name to look for.

        Returns:
            Iterable[CoinPricePoint]: A collection of parsed coin prices.
        """
        return await ExchangeAPIParser.parse(quote_coin=quote_coin)

    @staticmethod
    async def get_by_coin_name(
        base_coin: str, quote_coin: str = config.DEFAULT_QUOTE_COIN
    ) -> CoinPricePoint | None:
        """Get the coin prices for specified base and quote currencies.

        Args:
            base_coin (str): The requested coin name.
            quote_coin (str): The quote coin name.

        Returns:
            CoinPricePoint | None: A coin price object, if the coin was found by name.
        """
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
