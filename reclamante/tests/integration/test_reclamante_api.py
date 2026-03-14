import pytest
from starlette.testclient import TestClient
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os
from reclamante.src.infrastructure.database.config import Base, get_session
from app import app as main_app
from typing import AsyncGenerator

# Configuração do banco de dados de teste
DATABASE_URL_TEST = "sqlite+aiosqlite:///./test_reclamante.db"
engine_test = create_async_engine(DATABASE_URL_TEST, echo=True)
async_session_maker_test = sessionmaker(engine_test, class_=AsyncSession, expire_on_commit=False)

async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker_test() as session:
        yield session

@pytest.fixture(scope="module", autouse=True)
async def setup_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    os.remove("test_reclamante.db")

@pytest.fixture
def app() -> FastAPI:
    main_app.dependency_overrides[get_session] = override_get_session
    return main_app

@pytest.fixture
async def client(app: FastAPI) -> AsyncGenerator[TestClient, None]:
    async with TestClient(app=app, base_url="http://test") as c:
        yield c

@pytest.mark.asyncio
async def test_create_reclamante(client: TestClient):
    response = await client.post("/api/v1/reclamantes/", json={"nome": "Teste", "documento": "111", "telefone": "999"})
    assert response.status_code == 201
    data = response.json()
    assert data["nome"] == "Teste"
    assert "id" in data

@pytest.mark.asyncio
async def test_get_all_reclamantes(client: TestClient):
    response = await client.get("/api/v1/reclamantes/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["reclamantes"], list)

@pytest.mark.asyncio
async def test_get_reclamante_by_id(client: TestClient):
    # Primeiro, crie um reclamante para ter um ID para buscar
    create_response = await client.post("/api/v1/reclamantes/", json={"nome": "Busca", "documento": "222", "telefone": "888"})
    reclamante_id = create_response.json()["id"]

    response = await client.get(f"/api/v1/reclamantes/{reclamante_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == reclamante_id
    assert data["nome"] == "Busca"

@pytest.mark.asyncio
async def test_update_reclamante(client: TestClient):
    create_response = await client.post("/api/v1/reclamantes/", json={"nome": "Antigo", "documento": "333", "telefone": "777"})
    reclamante_id = create_response.json()["id"]

    response = await client.put(f"/api/v1/reclamantes/{reclamante_id}", json={"nome": "Novo", "documento": "333", "telefone": "666"})
    assert response.status_code == 200
    data = response.json()
    assert data["nome"] == "Novo"
    assert data["telefone"] == "666"

@pytest.mark.asyncio
async def test_delete_reclamante(client: TestClient):
    create_response = await client.post("/api/v1/reclamantes/", json={"nome": "Apagar", "documento": "444", "telefone": "555"})
    reclamante_id = create_response.json()["id"]

    delete_response = await client.delete(f"/api/v1/reclamantes/{reclamante_id}")
    assert delete_response.status_code == 204

    get_response = await client.get(f"/api/v1/reclamantes/{reclamante_id}")
    assert get_response.status_code == 404
