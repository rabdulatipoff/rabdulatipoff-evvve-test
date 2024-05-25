"""Models and storage schemas for the application.

Classes:
    CoinLastPrices: A collection of price attributes for supported exchanges.
    CoinPair: A currency pair price for an exchange.
    CoinPricePoint: A currency prices collection for supported exchanges.
"""

from decimal import Decimal
from pydantic import BaseModel, Field
from rabdulatipoff_evvve_test import config


class CoinLastPrices(BaseModel):
    """A collection of price attributes for supported exchanges."""

    binance: Decimal = Field(ge=0, decimal_places=8)
    bybit: Decimal = Field(ge=0, decimal_places=8)


class CoinPair(BaseModel):
    """A currency pair price for an exchange.

    Attrs:
        name (str): The currency pair name (base coin + quote coin).
        price (Decimal): The exchange price of the pair.
    """

    # Example: 'BTCUSDT'
    name: str = Field(default=config.DEFAULT_BASE_COIN + config.DEFAULT_QUOTE_COIN)
    price: Decimal = Field(ge=0, decimal_places=8)


class CoinPricePoint(BaseModel):
    """A currency prices collection for supported exchanges.

    Attrs:
        name (str): The name of the coin.
        prices (CoinLastPrices): The collection of exchange prices for the coin.
    """

    # Currency pair name
    name: str = Field(default=config.DEFAULT_BASE_COIN)
    # Exchange prices (base coin / quote coin rate for different exchanges)
    prices: CoinLastPrices
