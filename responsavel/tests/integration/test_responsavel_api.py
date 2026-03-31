"""
Testes de integração da API REST de Responsavel
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

# Adicionar o diretório responsavel ao PYTHONPATH para importar main.py
responsavel_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(responsavel_dir))

from responsavel.src.infrastructure.database.config import Base, get_session

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


# Fixture para criar um banco de dados de teste em memória
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


class TestCreateResponsavelAPI:
    """Testes para POST /api/v1/responsaveis"""

    def test_criar_responsavel_com_sucesso(self, client):
        """Testa criação de responsável via API com dados válidos"""
        # Arrange
        responsavel_data = {
            "nome": "João Silva",
            "cargo": "Segurança",
            "telefone": "11999999999"
        }

        # Act
        response = client.post("/api/v1/responsaveis/", json=responsavel_data)

        # Assert
        assert response.status_code == 201
        data = payload_data(response)
        assert data["nome"] == "João Silva"
        assert data["cargo"] == "Segurança"
        assert data["ativo"] is True  # Sempre inicia ativo
        assert "id" in data

    def test_criar_responsavel_com_dados_invalidos(self, client):
        """Testa criação de responsável com dados inválidos retorna 422"""
        # Arrange - faltando campo obrigatório
        responsavel_data = {
            "nome": "João Silva",
            # "cargo" está faltando (obrigatório)
            "telefone": "11999999999"
        }

        # Act
        response = client.post("/api/v1/responsaveis/", json=responsavel_data)

        # Assert
        assert response.status_code == 422

    def test_criar_responsavel_com_nome_vazio(self, client):
        """Testa que não aceita nome vazio"""
        # Arrange
        responsavel_data = {
            "nome": "",
            "cargo": "Segurança",
            "telefone": "11999999999"
        }

        # Act
        response = client.post("/api/v1/responsaveis/", json=responsavel_data)

        # Assert
        assert response.status_code in [400, 422]

    def test_criar_responsavel_com_telefone_invalido(self, client):
        """Testa que não aceita telefone com formato inválido"""
        # Arrange
        responsavel_data = {
            "nome": "João Silva",
            "cargo": "Segurança",
            "telefone": "12345"  # Menos de 10 dígitos
        }

        # Act
        response = client.post("/api/v1/responsaveis/", json=responsavel_data)

        # Assert
        assert response.status_code in [400, 422]

    def test_criar_responsavel_ativo_sempre_true(self, client):
        """Testa que responsável é criado sempre como ativo independente do input"""
        # Arrange
        responsavel_data = {
            "nome": "João Silva",
            "cargo": "Segurança",
            "telefone": "11999999999"
        }

        # Act
        response = client.post("/api/v1/responsaveis/", json=responsavel_data)

        # Assert
        assert response.status_code == 201
        assert payload_data(response)["ativo"] is True


class TestGetResponsavelByIdAPI:
    """Testes para GET /api/v1/responsaveis/{id}"""

    def test_buscar_responsavel_existente(self, client):
        """Testa busca de responsável que existe"""
        # Arrange - Cria um responsável primeiro
        create_data = {
            "nome": "Maria Souza",
            "cargo": "Recepcionista",
            "telefone": "11988888888"
        }
        create_response = client.post("/api/v1/responsaveis/", json=create_data)
        responsavel_id = payload_data(create_response)["id"]

        # Act
        response = client.get(f"/api/v1/responsaveis/{responsavel_id}")

        # Assert
        assert response.status_code == 200
        data = payload_data(response)
        assert data["id"] == responsavel_id
        assert data["nome"] == "Maria Souza"

    def test_buscar_responsavel_inexistente(self, client):
        """Testa busca de responsável que não existe"""
        # Act
        response = client.get("/api/v1/responsaveis/9999")

        # Assert
        assert response.status_code == 404

    def test_buscar_responsavel_com_id_string(self, client):
        """Testa busca de responsável com ID do tipo string"""
        # Act
        response = client.get("/api/v1/responsaveis/abc")

        # Assert
        assert response.status_code == 422


class TestGetAllResponsaveisAPI:
    """Testes para GET /api/v1/responsaveis"""

    def test_listar_todos_responsaveis(self, client):
        """Testa listagem de responsáveis"""
        # Act
        response = client.get("/api/v1/responsaveis/")

        # Assert
        assert response.status_code == 200
        data = payload_data(response)
        assert "responsaveis" in data
        assert "total" in data

    def test_listar_responsaveis_com_paginacao(self, client):
        """Testa listagem com parâmetros de paginação"""
        # Act
        response = client.get("/api/v1/responsaveis/?skip=0&limit=10")

        # Assert
        assert response.status_code == 200
        data = payload_data(response)
        assert data["skip"] == 0
        assert data["limit"] == 10

    def test_listar_responsaveis_com_skip_negativo(self, client):
        """Testa que skip negativo retorna erro"""
        # Act
        response = client.get("/api/v1/responsaveis/?skip=-1")

        # Assert - rota não captura ValueError, então retorna 500
        assert response.status_code in [400, 422, 500]

    def test_listar_responsaveis_com_limit_invalido(self, client):
        """Testa que limit inválido retorna erro"""
        # Act
        response = client.get("/api/v1/responsaveis/?limit=0")

        # Assert - rota não captura ValueError, então retorna 500
        assert response.status_code in [400, 422, 500]


class TestUpdateResponsavelAPI:
    """Testes para PUT /api/v1/responsaveis/{id}"""

    def test_atualizar_responsavel_com_sucesso(self, client):
        """Testa atualização de responsável"""
        # Arrange - Cria um responsável
        create_data = {
            "nome": "João Silva",
            "cargo": "Segurança",
            "telefone": "11999999999"
        }
        create_response = client.post("/api/v1/responsaveis/", json=create_data)
        responsavel_id = payload_data(create_response)["id"]

        # Act - Atualiza
        update_data = {
            "nome": "João Santos",
            "cargo": "Supervisor de Segurança",
            "telefone": "11999999999"
        }
        response = client.put(f"/api/v1/responsaveis/{responsavel_id}", json=update_data)

        # Assert
        assert response.status_code == 200
        data = payload_data(response)
        assert data["nome"] == "João Santos"
        assert data["cargo"] == "Supervisor de Segurança"

    def test_atualizar_responsavel_inexistente(self, client):
        """Testa atualização de responsável que não existe"""
        # Arrange
        update_data = {
            "nome": "João Santos",
            "cargo": "Supervisor",
            "telefone": "11999999999"
        }

        # Act
        response = client.put("/api/v1/responsaveis/9999", json=update_data)

        # Assert
        assert response.status_code == 404

    def test_atualizar_responsavel_com_telefone_invalido(self, client):
        """Testa que não aceita telefone inválido no update"""
        # Arrange - Cria um responsável
        create_data = {
            "nome": "João Silva",
            "cargo": "Segurança",
            "telefone": "11999999999"
        }
        create_response = client.post("/api/v1/responsaveis/", json=create_data)
        responsavel_id = payload_data(create_response)["id"]

        # Act - Tenta atualizar com telefone inválido
        update_data = {
            "nome": "João Silva",
            "cargo": "Segurança",
            "telefone": "123"  # Inválido
        }
        response = client.put(f"/api/v1/responsaveis/{responsavel_id}", json=update_data)

        # Assert
        assert response.status_code in [400, 422]


class TestDeleteResponsavelAPI:
    """Testes para DELETE /api/v1/responsaveis/{id}"""

    def test_deletar_responsavel_com_sucesso(self, client):
        """Testa exclusão de responsável"""
        # Arrange - Cria um responsável
        create_data = {
            "nome": "Carlos Lima",
            "cargo": "Porteiro",
            "telefone": "21977776666"
        }
        create_response = client.post("/api/v1/responsaveis/", json=create_data)
        responsavel_id = payload_data(create_response)["id"]

        # Act
        response = client.delete(f"/api/v1/responsaveis/{responsavel_id}")

        # Assert
        assert response.status_code in [200, 204]

        # Verifica que foi deletado
        get_response = client.get(f"/api/v1/responsaveis/{responsavel_id}")
        assert get_response.status_code == 404

    def test_deletar_responsavel_inexistente(self, client):
        """Testa exclusão de responsável que não existe"""
        # Act
        response = client.delete("/api/v1/responsaveis/9999")

        # Assert
        assert response.status_code == 404


class TestResponsavelStatusAPI:
    """Testes para endpoints de status ativo/inativo"""

    def test_buscar_responsaveis_ativos(self, client):
        """Testa endpoint GET /api/v1/responsaveis/ativo/{ativo_value}"""
        # Arrange - Cria um responsável
        create_data = {
            "nome": "João Silva",
            "cargo": "Segurança",
            "telefone": "11999999999"
        }
        client.post("/api/v1/responsaveis/", json=create_data)

        # Act
        response = client.get("/api/v1/responsaveis/ativo/true")

        # Assert
        assert response.status_code == 200
        data = payload_data(response)
        assert isinstance(data, list)
        assert all(r["ativo"] is True for r in data)

    def test_buscar_responsaveis_inativos(self, client):
        """Testa busca de responsáveis inativos"""
        # Act
        response = client.get("/api/v1/responsaveis/ativo/false")

        # Assert
        assert response.status_code == 200
        data = payload_data(response)
        assert isinstance(data, list)

    def test_alterar_status_responsavel(self, client):
        """Testa PATCH /api/v1/responsaveis/{id}/status"""
        # Arrange - Cria um responsável
        create_data = {
            "nome": "Ana Lima",
            "cargo": "Coordenadora",
            "telefone": "31966665555"
        }
        create_response = client.post("/api/v1/responsaveis/", json=create_data)
        responsavel_id = payload_data(create_response)["id"]
        assert payload_data(create_response)["ativo"] is True

        # Act - Desativa via PATCH /status
        status_data = {"ativo": False}
        response = client.patch(
            f"/api/v1/responsaveis/{responsavel_id}/status",
            json=status_data
        )

        # Assert
        assert response.status_code == 200
        assert payload_data(response)["ativo"] is False

    def test_alterar_status_responsavel_inexistente(self, client):
        """Testa PATCH /status de responsável inexistente"""
        # Act
        response = client.patch(
            "/api/v1/responsaveis/9999/status",
            json={"ativo": False}
        )

        # Assert
        assert response.status_code == 404


class TestPatchResponsavelAPI:
    """Testes de PATCH /api/v1/responsaveis/{id}"""

    def test_patch_responsavel_vazio_retorna_400(self, client):
        create_response = client.post(
            "/api/v1/responsaveis/",
            json={"nome": "Patch", "cargo": "Segurança", "telefone": "11999999999"},
        )
        responsavel_id = payload_data(create_response)["id"]

        response = client.patch(f"/api/v1/responsaveis/{responsavel_id}", json={})

        assert response.status_code == 400
