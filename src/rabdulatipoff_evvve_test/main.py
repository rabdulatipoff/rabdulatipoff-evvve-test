"""The main application module.

Attrs:
    app (FastAPI): The API app instance."""

from fastapi import FastAPI
from rabdulatipoff_evvve_test.api.routes import prices_router


app = FastAPI()
app.include_router(prices_router)
