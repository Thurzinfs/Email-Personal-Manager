from app.infrastructure.models.user_models import User

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import DeclarativeBase

from advanced_alchemy.extensions.fastapi import (
    AdvancedAlchemy,
    SQLAlchemyAsyncConfig,
)


config = SQLAlchemyAsyncConfig(
    connection_string='sqlite+aiosqlite:///my_db.sqlite3',
    create_all=True,
)

alchemy = AdvancedAlchemy(config=config)


class Base(DeclarativeBase):
    pass


async def get_session():
    async with config.get_session() as session:
        yield session


async def init_models():
    engine = config.get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    engine = config.get_engine()
    await engine.dispose()
