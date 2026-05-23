from app.core.database import async_session_maker

from sqlalchemy.ext.asyncio import AsyncSession

from typing import AsyncGenerator


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session

            await session.commit()

        except Exception:
            await session.rollback()
            raise

