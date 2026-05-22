from app.core.config import settings

from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/health")
async def health():
    return {
        "app_name": settings.APP_NAME,
        "app_version": settings.APP_VERSION,
        "debug_mode": settings.DEBUG,
        "status": "ok",
    }