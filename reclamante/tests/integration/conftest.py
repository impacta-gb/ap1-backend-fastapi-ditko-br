import asyncio
from typing import AsyncGenerator

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app import app
from devolucao.src.infrastructure.database.base_model import Base as DevolucaoBase
from item.src.infrastructure.database.base_model import Base as ItemBase
from local.src.infrastructure.database.base_model import Base as LocalBase
from reclamante.src.infrastructure.database.base_model import Base as ReclamanteBase
from responsavel.src.infrastructure.database.base_model import \
    Base as ResponsavelBase

DATABASE_URL_TEST = "sqlite+aiosqlite:///./test_reclamante_e2e.db"
engine_test = create_async_engine(DATABASE_URL_TEST, echo=True)
async_session_maker_test = sessionmaker(
    engine_test, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture(scope="function", autouse=True)
async def init_db():
    async with engine_test.begin() as conn:
        await conn.run_sync(LocalBase.metadata.create_all)
        await conn.run_sync(ResponsavelBase.metadata.create_all)
        await conn.run_sync(ItemBase.metadata.create_all)
        await conn.run_sync(DevolucaoBase.metadata.create_all)
        await conn.run_sync(ReclamanteBase.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(ReclamanteBase.metadata.drop_all)
        await conn.run_sync(DevolucaoBase.metadata.drop_all)
        await conn.run_sync(ItemBase.metadata.drop_all)
        await conn.run_sync(ResponsavelBase.metadata.drop_all)
        await conn.run_sync(LocalBase.metadata.drop_all)


@pytest.fixture(scope="function")
async def get_session_test() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker_test() as session:
        yield session


@pytest.fixture(scope="function")
def app_test() -> FastAPI:
    return app


@pytest.fixture
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as c:
        yield c
