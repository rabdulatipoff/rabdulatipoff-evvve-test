from fastapi import APIRouter, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from rabdulatipoff_evvve_test.client import PricesClient
from rabdulatipoff_evvve_test.config import (
    api_prefix,
    default_base_coin,
    default_quote_coin,
)


prices_router = APIRouter()
prices_prefix = "/prices"


@prices_router.get(api_prefix + prices_prefix, status_code=status.HTTP_200_OK)
async def get_all_coin_prices():
    """
    Get exchange prices for all listed coins.

    Returns:
        JSONResponse: A list of prices for the specified coin, as reported by supported exchanges.
    """
    try:
        content = jsonable_encoder(
            await PricesClient.get_all(quote_coin=default_quote_coin)
        )
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    if not content:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The price list is temporarily unavailable",
            headers={"Retry-After": "60"},
        )

    return JSONResponse(content=content)


@prices_router.get(
    api_prefix + prices_prefix + "/{coin_name}", status_code=status.HTTP_200_OK
)
async def get_coin_prices_by_name(coin_name: str = default_base_coin):
    """
    Get exchange prices for a specific currency by name.

    Args:
        coin_name (str): The name of the coin.

    Returns:
        JSONResponse: A list of prices for the specified coin, as reported by supported exchanges.
    """
    try:
        content = jsonable_encoder(
            await PricesClient.get_by_coin_name(base_coin=coin_name)
        )
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Currency not found"
        )

    return JSONResponse(content=content)
