"""
Testes de integração da API REST de Devolucao
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

# Adicionar o diretório devolucao ao PYTHONPATH para importar main.py
devolucao_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(devolucao_dir))

from devolucao.src.infrastructure.database.config import Base, get_session
from devolucao.src.infrastructure.database.models import ItemReferenceModel, ReclamanteReferenceModel

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
    async def seed_references():
        async with test_db() as session:
            items = [
                ItemReferenceModel(
                    id=i,
                    local_id=1,
                    responsavel_id=1,
                    status="disponivel",
                )
                for i in range(1, 21)
            ]
            reclamantes = [
                ReclamanteReferenceModel(
                    id=i,
                    nome=f"Reclamante {i}",
                    documento=f"DOC{i}",
                    telefone=f"1199999{i:04d}",
                )
                for i in range(1, 21)
            ]
            session.add_all(items + reclamantes)
            await session.commit()

    async def override_get_session():
        async with test_db() as session:
            yield session

    import asyncio
    asyncio.run(seed_references())

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client
    app.dependency_overrides.pop(get_session, None)


class TestCreateDevolucaoAPI:
    """Testes para POST /api/v1/devolucoes"""

    def test_criar_devolucao_com_sucesso(self, client):
        """Testa criação de devolução via API com dados válidos"""
        # Arrange
        devolucao_data = {
            "reclamante_id": 1,
            "item_id": 2,
            "observacao": "Item devolvido na portaria",
            "data_devolucao": "2024-01-15T10:00:00"
        }

        # Act
        response = client.post("/api/v1/devolucoes/", json=devolucao_data)

        # Assert
        assert response.status_code == 201
        data = payload_data(response)
        assert data["reclamante_id"] == 1
        assert data["item_id"] == 2
        assert data["observacao"] == "Item devolvido na portaria"
        assert "id" in data

    def test_criar_devolucao_com_dados_invalidos(self, client):
        """Testa criação de devolução com dados inválidos retorna 422"""
        # Arrange — faltando campo obrigatório
        devolucao_data = {
            "reclamante_id": 1,
            # "item_id" está faltando (obrigatório)
            "observacao": "Observação válida"
        }

        # Act
        response = client.post("/api/v1/devolucoes/", json=devolucao_data)

        # Assert
        assert response.status_code == 422

    def test_criar_devolucao_com_reclamante_id_invalido(self, client):
        """Testa que reclamante_id inválido retorna erro"""
        # Arrange
        devolucao_data = {
            "reclamante_id": 0,
            "item_id": 1,
            "observacao": "Observação",
            "data_devolucao": "2024-01-15T10:00:00"
        }

        # Act
        response = client.post("/api/v1/devolucoes/", json=devolucao_data)

        # Assert
        assert response.status_code in [400, 422]

    def test_criar_devolucao_com_item_id_invalido(self, client):
        """Testa que item_id inválido retorna erro"""
        # Arrange
        devolucao_data = {
            "reclamante_id": 1,
            "item_id": -1,
            "observacao": "Observação",
            "data_devolucao": "2024-01-15T10:00:00"
        }

        # Act
        response = client.post("/api/v1/devolucoes/", json=devolucao_data)

        # Assert
        assert response.status_code in [400, 422]

    def test_criar_devolucao_com_data_futura(self, client):
        """Testa que data futura retorna erro"""
        # Arrange
        devolucao_data = {
            "reclamante_id": 1,
            "item_id": 1,
            "observacao": "Observação",
            "data_devolucao": "2099-12-31T23:59:59"
        }

        # Act
        response = client.post("/api/v1/devolucoes/", json=devolucao_data)

        # Assert
        assert response.status_code in [400, 500]


class TestGetDevolucaoByIdAPI:
    """Testes para GET /api/v1/devolucoes/{devolucao_id}"""

    def test_buscar_devolucao_existente(self, client):
        """Testa busca de devolução que existe"""
        # Arrange — cria uma devolução primeiro
        create_data = {
            "reclamante_id": 1,
            "item_id": 2,
            "observacao": "Item devolvido",
            "data_devolucao": "2024-03-10T14:00:00"
        }
        create_response = client.post("/api/v1/devolucoes/", json=create_data)
        devolucao_id = payload_data(create_response)["id"]

        # Act
        response = client.get(f"/api/v1/devolucoes/{devolucao_id}")

        # Assert
        assert response.status_code == 200
        data = payload_data(response)
        assert data["id"] == devolucao_id
        assert data["observacao"] == "Item devolvido"

    def test_buscar_devolucao_inexistente(self, client):
        """Testa busca de devolução que não existe"""
        # Act
        response = client.get("/api/v1/devolucoes/9999")

        # Assert
        assert response.status_code == 404

    def test_buscar_devolucao_com_id_string(self, client):
        """Testa busca de devolução com ID do tipo string"""
        # Act
        response = client.get("/api/v1/devolucoes/abc")

        # Assert
        assert response.status_code == 422


class TestGetAllDevolucoesAPI:
    """Testes para GET /api/v1/devolucoes"""

    def test_listar_todas_devolucoes(self, client):
        """Testa listagem de devoluções"""
        # Act
        response = client.get("/api/v1/devolucoes/")

        # Assert
        assert response.status_code == 200
        data = payload_data(response)
        assert "devolucoes" in data
        assert "total" in data

    def test_listar_devolucoes_com_paginacao(self, client):
        """Testa listagem com parâmetros de paginação"""
        # Act
        response = client.get("/api/v1/devolucoes/?skip=0&limit=10")

        # Assert
        assert response.status_code == 200
        data = payload_data(response)
        assert data["skip"] == 0
        assert data["limit"] == 10

    def test_listar_devolucoes_com_skip_negativo(self, client):
        """Testa que skip negativo retorna erro"""
        # Act
        response = client.get("/api/v1/devolucoes/?skip=-1")

        # Assert
        assert response.status_code in [400, 500]

    def test_listar_devolucoes_com_limit_invalido(self, client):
        """Testa que limit inválido retorna erro"""
        # Act
        response = client.get("/api/v1/devolucoes/?limit=0")

        # Assert
        assert response.status_code in [400, 500]


class TestUpdateDevolucaoAPI:
    """Testes para PUT /api/v1/devolucoes/{devolucao_id}"""

    def test_atualizar_devolucao_com_sucesso(self, client):
        """Testa atualização de devolução via API"""
        # Arrange — cria devolução
        create_data = {
            "reclamante_id": 1,
            "item_id": 1,
            "observacao": "Observação original",
            "data_devolucao": "2024-04-10T09:00:00"
        }
        create_response = client.post("/api/v1/devolucoes/", json=create_data)
        devolucao_id = payload_data(create_response)["id"]

        # Act
        update_data = {
            "reclamante_id": 1,
            "item_id": 1,
            "observacao": "Observação atualizada",
            "data_devolucao": "2024-04-10T09:00:00"
        }
        response = client.put(f"/api/v1/devolucoes/{devolucao_id}", json=update_data)

        # Assert
        assert response.status_code == 200
        data = payload_data(response)
        assert data["observacao"] == "Observação atualizada"

    def test_atualizar_devolucao_inexistente(self, client):
        """Testa atualização de devolução que não existe"""
        # Arrange
        update_data = {
            "reclamante_id": 1,
            "item_id": 1,
            "observacao": "Observação",
            "data_devolucao": "2024-04-10T09:00:00"
        }

        # Act
        response = client.put("/api/v1/devolucoes/9999", json=update_data)

        # Assert
        assert response.status_code == 404


class TestPatchDevolucaoAPI:
    """Testes para PATCH /api/v1/devolucoes/{devolucao_id}"""

    def test_patch_devolucao_com_sucesso(self, client):
        """Testa atualização parcial de devolução via API"""
        # Arrange — cria devolução
        create_data = {
            "reclamante_id": 2,
            "item_id": 3,
            "observacao": "Observação para patch",
            "data_devolucao": "2024-05-20T11:00:00"
        }
        create_response = client.post("/api/v1/devolucoes/", json=create_data)
        devolucao_id = payload_data(create_response)["id"]

        # Act — patch apenas da observação
        patch_data = {"observacao": "Observação patcheada"}
        response = client.patch(f"/api/v1/devolucoes/{devolucao_id}", json=patch_data)

        # Assert
        assert response.status_code == 200
        data = payload_data(response)
        assert data["observacao"] == "Observação patcheada"

    def test_patch_devolucao_inexistente(self, client):
        """Testa patch de devolução que não existe"""
        # Arrange
        patch_data = {"observacao": "Nova observação"}

        # Act
        response = client.patch("/api/v1/devolucoes/9999", json=patch_data)

        # Assert
        assert response.status_code == 404

    def test_patch_devolucao_vazio_retorna_400(self, client):
        """Testa patch vazio"""
        create_response = client.post(
            "/api/v1/devolucoes/",
            json={
                "reclamante_id": 1,
                "item_id": 3,
                "observacao": "Observação inicial",
                "data_devolucao": "2024-05-20T11:00:00",
            },
        )
        devolucao_id = payload_data(create_response)["id"]

        response = client.patch(f"/api/v1/devolucoes/{devolucao_id}", json={})

        assert response.status_code == 400


class TestDeleteDevolucaoAPI:
    """Testes para DELETE /api/v1/devolucoes/{devolucao_id}"""

    def test_deletar_devolucao_com_sucesso(self, client):
        """Testa exclusão de devolução via API"""
        # Arrange — cria devolução
        create_data = {
            "reclamante_id": 1,
            "item_id": 5,
            "observacao": "Devolução para deletar",
            "data_devolucao": "2024-06-01T08:00:00"
        }
        create_response = client.post("/api/v1/devolucoes/", json=create_data)
        devolucao_id = payload_data(create_response)["id"]

        # Act
        response = client.delete(f"/api/v1/devolucoes/{devolucao_id}")

        # Assert
        assert response.status_code in [200, 204]

        # Verifica que foi deletado
        get_response = client.get(f"/api/v1/devolucoes/{devolucao_id}")
        assert get_response.status_code == 404

    def test_deletar_devolucao_inexistente(self, client):
        """Testa exclusão de devolução que não existe"""
        # Act
        response = client.delete("/api/v1/devolucoes/9999")

        # Assert
        assert response.status_code == 404


class TestGetDevolucoesByDataAPI:
    """Testes para GET /api/v1/devolucoes/data/{data}"""

    def test_buscar_por_data_com_resultados(self, client):
        """Testa busca de devoluções por data com resultados"""
        # Arrange — cria devoluções na mesma data
        for i in range(2):
            client.post("/api/v1/devolucoes/", json={
                "reclamante_id": i + 1,
                "item_id": i + 1,
                "observacao": f"Devolução {i}",
                "data_devolucao": "2024-07-04T10:00:00"
            })

        # Act
        response = client.get("/api/v1/devolucoes/data/2024-07-04T10:00:00")

        # Assert
        assert response.status_code == 200
        data = payload_data(response)
        assert isinstance(data, list)
        assert len(data) >= 2

    def test_buscar_por_data_sem_resultados(self, client):
        """Testa busca por data que não tem devoluções"""
        # Act
        response = client.get("/api/v1/devolucoes/data/1900-01-01T00:00:00")

        # Assert
        assert response.status_code == 200
        data = payload_data(response)
        assert isinstance(data, list)
        assert len(data) == 0
