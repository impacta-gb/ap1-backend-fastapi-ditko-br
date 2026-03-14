"""
Configurações e fixtures para testes de integração
"""
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

# Import Base from all models to ensure all tables are created
from item.src.infrastructure.database.config import Base as item_base
from local.src.infrastructure.database.config import Base as local_base
from responsavel.src.infrastructure.database.config import Base as responsavel_base
from devolucao.src.infrastructure.database.config import Base as devolucao_base
from reclamante.src.infrastructure.database.config import Base as reclamante_base


# URL do banco de dados de teste (usa SQLite em memória)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def test_engine():
    """Cria engine de teste"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True
    )
    
    # Cria as tabelas
    async with engine.begin() as conn:
        await conn.run_sync(local_base.metadata.create_all)
        await conn.run_sync(responsavel_base.metadata.create_all)
        await conn.run_sync(item_base.metadata.create_all)
        await conn.run_sync(devolucao_base.metadata.create_all)
        await conn.run_sync(reclamante_base.metadata.create_all)
    
    yield engine
    
    # Limpa as tabelas após os testes
    async with engine.begin() as conn:
        await conn.run_sync(item_base.metadata.drop_all)
        await conn.run_sync(responsavel_base.metadata.drop_all)
        await conn.run_sync(local_base.metadata.drop_all)
        await conn.run_sync(devolucao_base.metadata.drop_all)
        await conn.run_sync(reclamante_base.metadata.drop_all)
    
    await engine.dispose()


@pytest_asyncio.fixture
async def test_session(test_engine):
    """Cria sessão de teste"""
    async_session_maker = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with async_session_maker() as session:
        yield session
        await session.rollback()
