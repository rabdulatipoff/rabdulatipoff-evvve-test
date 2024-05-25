"""The API endpoint definitions.

Functions:
    get_all_coin_prices(None): Returns all available coin prices from supported exchanges.
    get_coin_prices_by_name(coin_name: str): Returns exchange prices list for a specified coin.
"""

from fastapi import APIRouter, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from rabdulatipoff_evvve_test.client import PricesClient
from rabdulatipoff_evvve_test import config

prices_router = APIRouter()
PRICES_PREFIX = config.API_PREFIX + "/prices"


@prices_router.get(PRICES_PREFIX, status_code=status.HTTP_200_OK)
async def get_all_coin_prices():
    """
    Get exchange prices for all listed coins.

    Returns:
        JSONResponse: A collection of available coin prices for supported exchanges.
    """
    try:
        content = jsonable_encoder(
            await PricesClient.get_all(quote_coin=config.DEFAULT_QUOTE_COIN)
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e

    if not content:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The price list is temporarily unavailable",
            headers={"Retry-After": "60"},
        )

    return JSONResponse(content=content)


@prices_router.get(PRICES_PREFIX + "{coin_name}", status_code=status.HTTP_200_OK)
async def get_coin_prices_by_name(coin_name: str = config.DEFAULT_BASE_COIN):
    """
    Get exchange prices for a specific currency by name.

    Args:
        coin_name (str): The name of the coin.

    Returns:
        JSONResponse: A collection of available coin prices for supported exchanges.
    """
    try:
        content = jsonable_encoder(
            await PricesClient.get_by_coin_name(base_coin=coin_name)
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e

    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Currency not found"
        )

    return JSONResponse(content=content)
