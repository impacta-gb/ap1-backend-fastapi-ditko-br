"""
Configurações e fixtures para testes de integração de Devolucao
"""
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import insert
from devolucao.src.infrastructure.database.config import Base
from devolucao.src.infrastructure.database.models import DevolucaoModel, ItemReferenceModel, ReclamanteReferenceModel


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
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Limpa as tabelas após os testes
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def test_session(test_engine):
    """Cria sessão de teste com dados de referência capturados"""
    async_session_maker = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session_maker() as session:
        # Insere referências de teste para Item e Reclamante
        # Items
        for i in range(1, 21):
            await session.execute(
                insert(ItemReferenceModel).values(
                    id=i,
                    local_id=1,
                    responsavel_id=1,
                    status="disponivel"
                )
            )
        
        # Reclamantes
        for i in range(1, 21):
            await session.execute(
                insert(ReclamanteReferenceModel).values(
                    id=i,
                    nome=f"Reclamante {i}",
                    documento=f"123456789{i:02d}",
                    telefone=f"1234567{i:03d}"
                )
            )
        
        await session.commit()
        
        yield session
        await session.rollback()
