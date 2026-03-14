import pytest
from starlette.testclient import TestClient
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os
from reclamante.src.infrastructure.database.config import Base, get_session
from app import app as main_app
from typing import Iterator, AsyncGenerator
from httpx import AsyncClient

# Configuração do banco de dados de teste
DATABASE_URL_TEST = "sqlite+aiosqlite:///./test_reclamante_e2e.db"
engine_test = create_async_engine(DATABASE_URL_TEST, echo=True)
async_session_maker_test = sessionmaker(engine_test, class_=AsyncSession, expire_on_commit=False)

async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker_test() as session:
        yield session

@pytest.fixture(scope="module", autouse=True)
async def setup_database():
    # This is a synchronous fixture, so we can't use async with
    # For simplicity, we'll just create and remove the db file
    if os.path.exists("test_reclamante_e2e.db"):
        os.remove("test_reclamante_e2e.db")
    # The engine and tables will be created by the app lifespan
    yield
    if os.path.exists("test_reclamante_e2e.db"):
        os.remove("test_reclamante_e2e.db")

@pytest.fixture
def app() -> FastAPI:
    main_app.dependency_overrides[get_session] = override_get_session
    return main_app

@pytest.fixture
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as c:
        yield c

@pytest.mark.asyncio
async def test_fluxo_completo_criar_buscar_atualizar_deletar(client: AsyncClient):
    # 1. Criar
    response_create = await client.post("/api/v1/reclamantes/", json={"nome": "Fluxo Completo", "documento": "12345678900", "telefone": "11987654321"})
    assert response_create.status_code == 201
    data_create = response_create.json()
    reclamante_id = data_create["id"]

    # 2. Buscar
    response_get = await client.get(f"/api/v1/reclamantes/{reclamante_id}")
    assert response_get.status_code == 200
    assert response_get.json()["nome"] == "Fluxo Completo"

    # 3. Atualizar
    response_update = await client.put(f"/api/v1/reclamantes/{reclamante_id}", json={"nome": "Fluxo Atualizado", "documento": "12345678900", "telefone": "11987654321"})
    assert response_update.status_code == 200
    assert response_update.json()["nome"] == "Fluxo Atualizado"

    # 4. Deletar
    response_delete = await client.delete(f"/api/v1/reclamantes/{reclamante_id}")
    assert response_delete.status_code == 204

    # 5. Verificar se foi deletado
    response_get_after_delete = await client.get(f"/api/v1/reclamantes/{reclamante_id}")
    assert response_get_after_delete.status_code == 404

@pytest.mark.asyncio
async def test_fluxo_listar_com_paginacao(client: AsyncClient):
    # Adicionar alguns reclamantes para teste de paginação
    for i in range(15):
        await client.post("/api/v1/reclamantes/", json={"nome": f"Paginacao {i}", "documento": f"000{i}", "telefone": f"999{i}"})

    # Clear the table to ensure a clean state
    async with async_session_maker_test() as session:
        async with session.begin():
            await session.execute(Base.metadata.tables['reclamantes'].delete())

    # Adicionar alguns reclamantes para teste de paginação
    for i in range(15):
        await client.post("/api/v1/reclamantes/", json={"nome": f"Paginacao {i}", "documento": f"000{i}", "telefone": f"999{i}"})

    # Listar com paginação
    response = await client.get("/api/v1/reclamantes/?skip=5&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert len(data["reclamantes"]) == 5
    assert data["reclamantes"][0]["nome"] == "Paginacao 5"
    assert data["total"] >= 15
    assert data["skip"] == 5
    assert data["limit"] == 5
