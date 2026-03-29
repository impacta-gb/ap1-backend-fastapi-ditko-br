"""
Testes de integração da API REST de Reclamante
Testa os endpoints HTTP, validações, status codes e serialização
"""
import sys
from pathlib import Path

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from unittest.mock import AsyncMock, patch

# Adicionar o diretório reclamante ao PYTHONPATH para importar main.py
reclamante_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(reclamante_dir))

from reclamante.src.infrastructure.database.config import Base, get_session

with patch("src.infrastructure.messaging.bootstrap.MessagingBootstrap") as MockMessagingBootstrap:
    bootstrap_instance = MockMessagingBootstrap.return_value
    bootstrap_instance.start_producers = AsyncMock(return_value=None)
    bootstrap_instance.start_consumers = AsyncMock(return_value=None)
    bootstrap_instance.stop_producers = AsyncMock(return_value=None)
    bootstrap_instance.stop_consumers = AsyncMock(return_value=None)
    from main import app


def payload_data(response):
    """Extrai o payload de sucesso, aceitando contrato antigo e novo."""
    body = response.json()
    if isinstance(body, dict) and "data" in body:
        return body["data"]
    return body


@pytest_asyncio.fixture
async def test_db():
    """Cria um banco de dados SQLite em memória para testes"""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    yield async_session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
def client(test_db):
    """Cria um cliente de teste para a API"""
    async def override_get_session():
        async with test_db() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client
    app.dependency_overrides.pop(get_session, None)


class TestCreateReclamanteAPI:
    """Testes para POST /api/v1/reclamantes"""

    def test_criar_reclamante_com_sucesso(self, client):
        """Testa criação de reclamante via API com dados válidos"""
        # Arrange
        reclamante_data = {
            "nome": "Teste",
            "documento": "111",
            "telefone": "999",
        }

        # Act
        response = client.post("/api/v1/reclamantes/", json=reclamante_data)

        # Assert
        assert response.status_code == 201
        data = payload_data(response)
        assert data["nome"] == "Teste"
        assert "id" in data

    def test_criar_reclamante_com_dados_invalidos(self, client):
        """Testa criação com payload inválido"""
        # Arrange
        reclamante_data = {
            "nome": "",
            "documento": "111",
            "telefone": "999",
        }

        # Act
        response = client.post("/api/v1/reclamantes/", json=reclamante_data)

        # Assert
        assert response.status_code in [400, 422]

    def test_criar_reclamante_com_campo_faltando(self, client):
        """Testa criação faltando campo obrigatório"""
        # Arrange
        reclamante_data = {
            "nome": "Teste",
            "telefone": "999",
        }

        # Act
        response = client.post("/api/v1/reclamantes/", json=reclamante_data)

        # Assert
        assert response.status_code == 422

    def test_criar_reclamante_com_telefone_vazio(self, client):
        """Testa criação com telefone vazio"""
        # Arrange
        reclamante_data = {
            "nome": "Teste",
            "documento": "111",
            "telefone": "",
        }

        # Act
        response = client.post("/api/v1/reclamantes/", json=reclamante_data)

        # Assert
        assert response.status_code in [400, 422]

    def test_criar_reclamante_com_documento_vazio(self, client):
        """Testa criação com documento vazio (validação de domínio)"""
        # Arrange
        reclamante_data = {
            "nome": "Teste",
            "documento": "",
            "telefone": "999",
        }

        # Act
        response = client.post("/api/v1/reclamantes/", json=reclamante_data)

        # Assert
        assert response.status_code in [400, 422]


class TestGetAllReclamantesAPI:
    """Testes para GET /api/v1/reclamantes"""

    def test_listar_todos_reclamantes(self, client):
        """Testa listagem de reclamantes"""
        # Act
        response = client.get("/api/v1/reclamantes/")

        # Assert
        assert response.status_code == 200
        data = payload_data(response)
        assert "reclamantes" in data
        assert "total" in data

    def test_listar_reclamantes_com_paginacao(self, client):
        """Testa listagem com paginação"""
        # Act
        response = client.get("/api/v1/reclamantes/?skip=0&limit=10")

        # Assert
        assert response.status_code == 200
        data = payload_data(response)
        assert data["skip"] == 0
        assert data["limit"] == 10

    def test_listar_reclamantes_com_skip_negativo(self, client):
        """Testa listagem com skip negativo"""
        # Act
        response = client.get("/api/v1/reclamantes/?skip=-1")

        # Assert
        assert response.status_code in [400, 422, 500]

    def test_listar_reclamantes_com_limit_invalido(self, client):
        """Testa listagem com limit inválido"""
        # Act
        response = client.get("/api/v1/reclamantes/?limit=0")

        # Assert
        assert response.status_code in [400, 422, 500]


class TestGetReclamanteByIdAPI:
    """Testes para GET /api/v1/reclamantes/{id}"""

    def test_buscar_reclamante_existente(self, client):
        """Testa busca de reclamante existente"""
        # Arrange
        create_response = client.post(
            "/api/v1/reclamantes/",
            json={"nome": "Busca", "documento": "222", "telefone": "888"},
        )
        reclamante_id = payload_data(create_response)["id"]

        # Act
        response = client.get(f"/api/v1/reclamantes/{reclamante_id}")

        # Assert
        assert response.status_code == 200
        data = payload_data(response)
        assert data["id"] == reclamante_id
        assert data["nome"] == "Busca"

    def test_buscar_reclamante_inexistente(self, client):
        """Testa busca de reclamante que não existe"""
        # Act
        response = client.get("/api/v1/reclamantes/9999")

        # Assert
        assert response.status_code == 404

    def test_buscar_reclamante_com_id_string(self, client):
        """Testa busca com id inválido do tipo string"""
        # Act
        response = client.get("/api/v1/reclamantes/abc")

        # Assert
        assert response.status_code == 422

    def test_buscar_reclamante_com_id_negativo(self, client):
        """Testa busca com id negativo"""
        # Act
        response = client.get("/api/v1/reclamantes/-1")

        # Assert
        assert response.status_code in [400, 404, 422, 500]


class TestUpdateReclamanteAPI:
    """Testes para PUT /api/v1/reclamantes/{id}"""

    def test_atualizar_reclamante_com_sucesso(self, client):
        """Testa atualização de reclamante"""
        # Arrange
        create_response = client.post(
            "/api/v1/reclamantes/",
            json={"nome": "Antigo", "documento": "333", "telefone": "777"},
        )
        reclamante_id = payload_data(create_response)["id"]

        # Act
        response = client.put(
            f"/api/v1/reclamantes/{reclamante_id}",
            json={"nome": "Novo", "documento": "333", "telefone": "666"},
        )

        # Assert
        assert response.status_code == 200
        data = payload_data(response)
        assert data["nome"] == "Novo"
        assert data["telefone"] == "666"

    def test_atualizar_reclamante_inexistente(self, client):
        """Testa update em reclamante inexistente"""
        # Arrange
        payload = {"nome": "Novo", "documento": "333", "telefone": "666"}

        # Act
        response = client.put("/api/v1/reclamantes/9999", json=payload)

        # Assert
        assert response.status_code == 404

    def test_atualizar_reclamante_com_payload_incompleto(self, client):
        """Testa update com payload incompleto"""
        # Act
        response = client.put("/api/v1/reclamantes/1", json={"nome": "Novo"})

        # Assert
        assert response.status_code == 422

    def test_atualizar_reclamante_com_nome_vazio(self, client):
        """Testa update com nome vazio"""
        # Arrange
        create_response = client.post(
            "/api/v1/reclamantes/",
            json={"nome": "Original", "documento": "909", "telefone": "101"},
        )
        reclamante_id = payload_data(create_response)["id"]

        # Act
        response = client.put(
            f"/api/v1/reclamantes/{reclamante_id}",
            json={"nome": "", "documento": "909", "telefone": "101"},
        )

        # Assert
        assert response.status_code in [400, 422]


class TestDeleteReclamanteAPI:
    """Testes para DELETE /api/v1/reclamantes/{id}"""

    def test_deletar_reclamante_com_sucesso(self, client):
        """Testa exclusão de reclamante"""
        # Arrange
        create_response = client.post(
            "/api/v1/reclamantes/",
            json={"nome": "Apagar", "documento": "444", "telefone": "555"},
        )
        reclamante_id = payload_data(create_response)["id"]

        # Act
        delete_response = client.delete(f"/api/v1/reclamantes/{reclamante_id}")

        # Assert
        assert delete_response.status_code in [200, 204]

        # Act
        get_response = client.get(f"/api/v1/reclamantes/{reclamante_id}")

        # Assert
        assert get_response.status_code == 404

    def test_deletar_reclamante_inexistente(self, client):
        """Testa exclusão de reclamante inexistente"""
        # Act
        response = client.delete("/api/v1/reclamantes/9999")

        # Assert
        assert response.status_code == 404

    def test_deletar_reclamante_com_id_string(self, client):
        """Testa exclusão com id inválido do tipo string"""
        # Act
        response = client.delete("/api/v1/reclamantes/abc")

        # Assert
        assert response.status_code == 422


class TestPatchReclamanteAPI:
    """Testes para PATCH /api/v1/reclamantes/{id}"""

    def test_patch_reclamante_com_sucesso(self, client):
        create_response = client.post(
            "/api/v1/reclamantes/",
            json={"nome": "Patch", "documento": "321", "telefone": "777"},
        )
        reclamante_id = payload_data(create_response)["id"]

        response = client.patch(
            f"/api/v1/reclamantes/{reclamante_id}",
            json={"telefone": "555"},
        )

        assert response.status_code == 200
        data = payload_data(response)
        assert data["telefone"] == "555"

    def test_patch_reclamante_vazio_retorna_400(self, client):
        create_response = client.post(
            "/api/v1/reclamantes/",
            json={"nome": "Patch", "documento": "321", "telefone": "777"},
        )
        reclamante_id = payload_data(create_response)["id"]

        response = client.patch(f"/api/v1/reclamantes/{reclamante_id}", json={})

        assert response.status_code == 400

    def test_patch_reclamante_inexistente(self, client):
        response = client.patch("/api/v1/reclamantes/9999", json={"nome": "Novo"})
        assert response.status_code == 404
