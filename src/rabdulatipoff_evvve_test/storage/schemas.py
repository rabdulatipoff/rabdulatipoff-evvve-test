from decimal import Decimal
from pydantic import BaseModel, Field
from rabdulatipoff_evvve_test.config import default_base_coin, default_quote_coin


class CoinPair(BaseModel):
    # Currency pair name (base coin + quote coin)
    # Example: 'BTCUSDT'
    name: str = Field(default=default_base_coin + default_quote_coin)
    price: Decimal = Field(ge=0, decimal_places=8)


class CoinLastPrices(BaseModel):
    binance: Decimal = Field(ge=0, decimal_places=8)
    bybit: Decimal = Field(ge=0, decimal_places=8)


class CoinPricePoint(BaseModel):
    # Currency pair name
    name: str = Field(default=default_base_coin)
    # Exchange prices (base coin / quote coin rate for different exchanges)
    prices: CoinLastPrices
