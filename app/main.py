import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

import app.models
from app.core.config import settings
from app.core.database import init_db
from app.core.error_handlers import http_exception_handler
from app.core.http_exceptions import HttpException
from app.routers import submission, test_suite
from app.services.result_awaiter import ResultAwaiter

from shared.logger import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application startup and shutdown lifecycle.

    Initializes the database on startup, starts the background result awaiter
    task, and cancels it when the FastAPI application shuts down.
    """
    setup_logging()
    await init_db()
    checker = asyncio.create_task(ResultAwaiter.listen())

    yield
    checker.cancel()


app = FastAPI(lifespan=lifespan)

app.add_exception_handler(HttpException, http_exception_handler)

app.include_router(test_suite.router, prefix="/testsuite", tags=["testsuite"])

app.include_router(submission.router, prefix="/submission", tags=["submissions"])


@app.get("/health")
async def health():
    return {
        "app_name": settings.APP_NAME,
        "app_version": settings.APP_VERSION,
        "debug_mode": settings.DEBUG,
        "status": "ok",
    }

