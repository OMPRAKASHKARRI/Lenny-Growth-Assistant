import uuid
from collections.abc import AsyncGenerator
from sqlalchemy.engine import make_url

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy import text
from sqlalchemy.orm import DeclarativeBase

from .config import settings


database_url = make_url(settings.database_url)
connect_args = {}
if database_url.drivername == "postgresql+asyncpg":
    connect_args = {
        "statement_cache_size": 0,
        "prepared_statement_name_func": lambda: f"__asyncpg_{uuid.uuid4()}__",
    }

engine = create_async_engine(settings.database_url, future=True, echo=False, connect_args=connect_args)

SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session


async def init_db() -> None:
    from . import models

    async with engine.begin() as connection:
        if database_url.drivername == "postgresql+asyncpg":
            await connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await connection.run_sync(Base.metadata.create_all)
        if database_url.drivername == "postgresql+asyncpg":
            await connection.execute(text("ALTER TABLE transcript_chunks ADD COLUMN IF NOT EXISTS embedding vector(64)"))