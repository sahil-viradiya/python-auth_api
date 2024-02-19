from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://postgres:admin@localhost:5432/auth"

engine = create_async_engine(SQLALCHEMY_DATABASE_URL)
sessionLoacal = async_sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


async def init_model(engine) -> AsyncSession:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def getDb():
    db = sessionLoacal()
    try:
        yield db
    finally:
        await db.close()
