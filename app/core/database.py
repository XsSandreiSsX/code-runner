from app.core.config import BASE_DIR, settings

from contextlib import asynccontextmanager
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase



class Base(DeclarativeBase):
    pass

if settings.DEBUG:
    DATABASE_URL = f"sqlite+aiosqlite:///{BASE_DIR}/codrunner.db"
else:
    DATABASE_URL = (f"postgresql+asyncpg://"
                    f"{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@"
                    f"{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/"
                    f"{settings.POSTGRES_DB}")


engine = create_async_engine(DATABASE_URL,
                             echo=settings.DEBUG,
                             future=True)


async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
