from app.core.config import settings
from app.core.database import init_db
from app.core.http_exceptions import HttpException
from app.core.error_handlers import http_exception_handler

import app.models

from app.routers import test_suite

from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(lifespan=lifespan)

app.add_exception_handler(HttpException, http_exception_handler)

app.include_router(test_suite.router,
                   prefix="/testsuite",
                   tags=["tests"])


@app.get("/health")
async def health():
    return {
        "app_name": settings.APP_NAME,
        "app_version": settings.APP_VERSION,
        "debug_mode": settings.DEBUG,
        "status": "ok",
    }