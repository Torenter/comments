from sqlalchemy.ext.asyncio.session import AsyncSession

from database.database import async_session


async def get_session() -> AsyncSession:
    async with async_session() as session:
        async with session.begin():
            try:
                yield session
            finally:
                await session.close()
