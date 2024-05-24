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
from rabdulatipoff_evvve_test.config import parse_endpoints, default_quote_coin


class ExchangeAPIParser:
    @staticmethod
    async def retry_fetch(url):
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        client = RetryClient(loop=loop)
        async with client.get(
            url, retry_options=ExponentialRetry(attempts=5)
        ) as response:
            try:
                return await response.json()
            except:
                raise
            finally:
                await client.close()

    @classmethod
    async def fetch_coin_pairs(cls, name: str, url: str, key: str) -> tuple[CoinPair]:
        def to_coin_pairs(pairs: list[dict]):
            return tuple(
                CoinPair(
                    name=str(pair["symbol"]),
                    price=Decimal(pair[key]).normalize(),
                )
                for pair in pairs
            )

        data = await Cache.get(name)
        if not data:
            try:
                response = await cls.retry_fetch(url=url)
            except:
                raise Exception(f"Could not fetch price pairs for {name}")

            # Extract the pairs list from the response object, if necessary
            if name == "bybit":
                response = response["result"]

            data = f"[{', '.join(pair.json() for pair in to_coin_pairs(response))}]"
            await Cache.set(name, data)

        pairs = tuple(CoinPair(**pair) for pair in json.loads(data))
        return pairs

    @classmethod
    async def pairs_to_prices(
        cls,
        pairs_dict: dict,
        quote_coin: str = default_quote_coin,
        exchanges: Iterable[str] = ("binance", "bybit"),
        save: bool = True,
    ) -> tuple[CoinPricePoint]:
        async def save_price(p: CoinPricePoint):
            await Cache.set(Cache.get_path((quote_coin, p.name)), p.json())

        # NOTE: all provided coin pairs must exist for every exchange
        target_pairs = zip(*(pairs_dict[name] for name in exchanges))

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
    async def parse(cls, quote_coin: str = default_quote_coin) -> tuple[CoinPricePoint]:
        exchange_pairs = {
            name: await cls.fetch_coin_pairs(name, url, key)
            for name, url, key in parse_endpoints
        }

        for name, pairs in exchange_pairs.items():
            if not pairs:
                raise Exception(f"Could not fetch coin pairs for exchange {name}")

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
            pairs_dict=quote_coin_pairs, quote_coin=quote_coin
        )
        if not prices:
            raise Exception("Could not parse coin prices")
        # Update available pairs for the selected quote coin
        await Cache.set(quote_coin, json.dumps(tuple(el.name for el in prices)))

        return prices
