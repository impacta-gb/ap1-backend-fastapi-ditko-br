"""
Configurações e fixtures para testes de integração
"""
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import insert
from item.src.infrastructure.database.config import Base
from item.src.infrastructure.database.models import ItemModel, LocalReferenceModel, ResponsavelReferenceModel


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
        # Insere referências de teste para Local e Responsável
        await session.execute(
            insert(LocalReferenceModel).values(
                id=1,
                tipo="Departamento",
                bairro="Centro",
                descricao="Local de teste"
            )
        )
        
        await session.execute(
            insert(ResponsavelReferenceModel).values(
                id=1,
                nome="Responsável Teste",
                cargo="Gerenciador",
                telefone="1234567890",
                ativo=1
            )
        )
        
        await session.commit()
        
        yield session
        await session.rollback()
