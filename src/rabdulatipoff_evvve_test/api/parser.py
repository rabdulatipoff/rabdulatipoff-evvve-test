"""Exchanges API parsing methods and related objects.

Classes:
    ExchangeAPIParser: The API parser implementation class.

Functions:
    retry_fetch: Fetch a HTTP resource by URL.

Exceptions:
    ResourceFetchError:
    ParseError:
"""

import json
import asyncio
from typing import Iterable
from decimal import Decimal
from aiohttp_retry import RetryClient, ExponentialRetry
from rabdulatipoff_evvve_test.storage.cache import Cache
from rabdulatipoff_evvve_test.storage.schemas import (
    CoinPair,
    CoinLastPrices,
    CoinPricePoint,
)
from rabdulatipoff_evvve_test import config


class ResourceFetchError(Exception):
    """A HTTP resource fetch error."""


class ParseError(Exception):
    """A coin prices parsing error."""


class ExchangeAPIParser:
    """The parser implementation class for supported exchange APIs."""

    @classmethod
    async def fetch_coin_pairs(
        cls, exchange: config.EndpointOptions
    ) -> tuple[CoinPair]:
        """Get coin pair data (fetch & update cache from API endpoints on a miss).

        Args:
            exchange: The exchange API endpoint options.

        Returns:
            tuple[CoinPair]: A collection of coin pairs for the exchange.
        """

        def to_coin_pairs(pairs: list[dict]):
            return tuple(
                CoinPair(
                    name=str(pair["symbol"]),
                    price=Decimal(pair[exchange.key]).normalize(),
                )
                for pair in pairs
            )

        data = await Cache.get(exchange.name)
        if not data:
            try:
                response = await retry_fetch(url=exchange.url)
            except Exception as e:
                raise ResourceFetchError(
                    f"Could not fetch price pairs for {exchange.name}"
                ) from e

            # Extract the pairs list from the response object, if necessary
            if exchange.name == "bybit":
                response = response["result"]

            data = f"[{', '.join(pair.json() for pair in to_coin_pairs(response))}]"
            await Cache.set(exchange.name, data)

        pairs = tuple(CoinPair(**pair) for pair in json.loads(data))
        return pairs

    @classmethod
    async def pairs_to_prices(
        cls,
        pairs: dict,
        quote_coin: str = config.DEFAULT_QUOTE_COIN,
        exchanges: Iterable[str] = ("binance", "bybit"),
        save: bool = True,
    ) -> tuple[CoinPricePoint]:
        """Convert dictionary of coin pairs into a sequence of coin prices for supported exchanges.

        Args:
            pairs (dict): The coin pair sequences dictionary (identical sequence keys & order).
            quote_coin (str): The quote coin for coin pairs.
            exchanges (Iterable[str]): The list of exchanges to extract the prices for.
            save (bool): Whether to write individual coins price data to the storage.

        Returns:
            tuple[CoinPricePoint]: A collection of coin prices from the provided coin pairs.
        """

        async def save_price(p: CoinPricePoint):
            await Cache.set(Cache.get_path((quote_coin, p.name)), p.json())

        # NOTE: all provided coin pairs must exist for every exchange
        target_pairs = zip(*(pairs[name] for name in exchanges))

        coin_prices = tuple(
            CoinPricePoint(
                # Remove the quote coin name from the pair name
                name=pairs_tuple[0].name.replace(quote_coin, ""),
                prices=CoinLastPrices(
                    **{
                        name: pairs_tuple[idx].price
                        for idx, name in enumerate(exchanges)
                    }
                ),
            )
            for pairs_tuple in target_pairs
        )

        if save:
            await asyncio.gather(
                *(asyncio.create_task(save_price(coin)) for coin in coin_prices)
            )

        return coin_prices

    @classmethod
    async def parse(
        cls, quote_coin: str = config.DEFAULT_QUOTE_COIN
    ) -> tuple[CoinPricePoint]:
        """Parse all supported exchanges for coin prices and return aggregated prices.

        Args:
            quote_coin (str): The quote coin for parsed coin pairs.

        Returns:
            tuple[CoinPricePoint]: A collection of objects with coin prices for supported exchanges.
        """
        exchange_pairs = {
            name: await cls.fetch_coin_pairs(config.EndpointOptions(name, url, key))
            for name, url, key in config.PARSE_ENDPOINTS
        }

        for name, pairs in exchange_pairs.items():
            if not pairs:
                raise ResourceFetchError(
                    f"Could not fetch coin pairs for exchange {name}"
                )

        # Get names for the coin pairs that exist on selected exchanges
        head, *tail = exchange_pairs.values()
        shared_pair_names = frozenset((el.name for el in head)).intersection(
            el.name for exchange in tail for el in exchange
        )

        quote_coin_pairs = {
            name: tuple(
                sorted(
                    filter(
                        lambda el: el.name in shared_pair_names
                        and el.name.endswith(quote_coin),
                        pairs,
                    ),
                    key=lambda el: el.name,
                )
            )
            for name, pairs in exchange_pairs.items()
        }

        prices = await cls.pairs_to_prices(
            pairs=quote_coin_pairs, quote_coin=quote_coin
        )
        if not prices:
            raise ParseError("Could not parse coin prices")
        # Update available pairs for the selected quote coin
        await Cache.set(quote_coin, json.dumps(tuple(el.name for el in prices)))

        return prices


async def retry_fetch(url):
    """Fetch a remote resource by URL using an async retry mechanism.

    Args:
        url (str): The URL of the resource to fetch.

    Returns:
        str: JSON response with the resource contents.
    """
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    client = RetryClient(loop=loop)
    async with client.get(url, retry_options=ExponentialRetry(attempts=5)) as response:
        try:
            return await response.json()
        finally:
            await client.close()
