from fastapi import FastAPI
from .config import api_prefix
from .routes import prices_router


app = FastAPI()
app.include_router(prices_router)
