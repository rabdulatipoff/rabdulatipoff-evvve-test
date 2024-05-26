"""The main application module.

Attrs:
    logger: Logger: The app logger instance.
    app (FastAPI): The API app instance."""

from fastapi import FastAPI
from rabdulatipoff_evvve_test.api.routes import prices_router

from rabdulatipoff_evvve_test.logger import logger


app = FastAPI()
app.include_router(prices_router)


@app.on_event("startup")
def startup_event():
    logger.info("Starting the prices API service...")


@app.on_event("shutdown")
def shutdown_event():
    logger.info("Stopping the prices API service...")
