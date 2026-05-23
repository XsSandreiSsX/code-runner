from app.core.config import settings
from app.core.database import init_db

import app.models

from app.routers import test_suite

from contextlib import asynccontextmanager
from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(test_suite.router,
                   prefix="/test",
                   tags=["test"])


@app.get("/health")
async def health():
    return {
        "app_name": settings.APP_NAME,
        "app_version": settings.APP_VERSION,
        "debug_mode": settings.DEBUG,
        "status": "ok",
    }