from fastapi import APIRouter, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from .storage.client import PricesClient
from .config import api_prefix, default_base_coin, default_quote_coin


prices_router = APIRouter()
prices_prefix = "/prices"


@prices_router.get(api_prefix + prices_prefix, status_code=status.HTTP_200_OK)
async def get_all_coin_prices():
    return JSONResponse(
        content=jsonable_encoder(
            await PricesClient.get_all(quote_coin=default_quote_coin)
        )
    )


@prices_router.get(api_prefix + prices_prefix + "/{coin_name}")
async def get_coin_prices_by_name(coin_name: str = default_base_coin):
    return JSONResponse(
        content=jsonable_encoder(
            await PricesClient.get_by_coin_name(base_coin=coin_name)
        )
    )
