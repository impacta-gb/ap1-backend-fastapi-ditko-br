"""
Testes de integração da API REST de Local
Testa os endpoints HTTP, validações, status codes e serialização
"""
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from local.src.infrastructure.database.config import Base, get_session
from app import app


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


class TestCreateLocalAPI:
    """Testes para POST /api/v1/locais"""

    def test_criar_local_com_sucesso(self, client):
        """Testa criação de local via API com dados válidos"""
        # Arrange
        local_data = {
            "tipo": "Metrô",
            "descricao": "Estação Sé - Plataforma Central",
            "bairro": "Centro"
        }

        # Act
        response = client.post("/api/v1/locais/", json=local_data)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["tipo"] == "Metrô"
        assert data["descricao"] == "Estação Sé - Plataforma Central"
        assert data["bairro"] == "Centro"
        assert "id" in data

    def test_criar_local_com_dados_invalidos(self, client):
        """Testa criação de local com dados inválidos retorna 422"""
        # Arrange - faltando campo obrigatório
        local_data = {
            "tipo": "Metrô",
            # "descricao" está faltando (obrigatório)
            "bairro": "Centro"
        }

        # Act
        response = client.post("/api/v1/locais/", json=local_data)

        # Assert
        assert response.status_code == 422

    def test_criar_local_com_tipo_vazio(self, client):
        """Testa que não aceita tipo vazio"""
        # Arrange
        local_data = {
            "tipo": "",
            "descricao": "Descrição válida",
            "bairro": "Centro"
        }

        # Act
        response = client.post("/api/v1/locais/", json=local_data)

        # Assert
        assert response.status_code in [400, 422]

    def test_criar_local_com_descricao_vazia(self, client):
        """Testa que não aceita descrição vazia"""
        # Arrange
        local_data = {
            "tipo": "Metrô",
            "descricao": "",
            "bairro": "Centro"
        }

        # Act
        response = client.post("/api/v1/locais/", json=local_data)

        # Assert
        assert response.status_code in [400, 422]

    def test_criar_local_com_bairro_vazio(self, client):
        """Testa que não aceita bairro vazio"""
        # Arrange
        local_data = {
            "tipo": "Metrô",
            "descricao": "Descrição válida",
            "bairro": ""
        }

        # Act
        response = client.post("/api/v1/locais/", json=local_data)

        # Assert
        assert response.status_code in [400, 422]


class TestGetLocalByIdAPI:
    """Testes para GET /api/v1/locais/{local_id}"""

    def test_buscar_local_existente(self, client):
        """Testa busca de local que existe"""
        # Arrange - Cria um local primeiro
        create_data = {
            "tipo": "Parque",
            "descricao": "Parque Ibirapuera",
            "bairro": "Moema"
        }
        create_response = client.post("/api/v1/locais/", json=create_data)
        local_id = create_response.json()["id"]

        # Act
        response = client.get(f"/api/v1/locais/{local_id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == local_id
        assert data["tipo"] == "Parque"
        assert data["bairro"] == "Moema"

    def test_buscar_local_inexistente(self, client):
        """Testa busca de local que não existe"""
        # Act
        response = client.get("/api/v1/locais/9999")

        # Assert
        assert response.status_code == 404

    def test_buscar_local_com_id_string(self, client):
        """Testa busca de local com ID do tipo string"""
        # Act
        response = client.get("/api/v1/locais/abc")

        # Assert
        assert response.status_code == 422


class TestGetAllLocaisAPI:
    """Testes para GET /api/v1/locais"""

    def test_listar_todos_locais(self, client):
        """Testa listagem de locais"""
        # Act
        response = client.get("/api/v1/locais/")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "locals" in data
        assert "total" in data

    def test_listar_locais_com_paginacao(self, client):
        """Testa listagem com parâmetros de paginação"""
        # Act
        response = client.get("/api/v1/locais/?skip=0&limit=10")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["skip"] == 0
        assert data["limit"] == 10

    def test_listar_locais_com_skip_negativo(self, client):
        """Testa que skip negativo retorna erro"""
        # Act
        response = client.get("/api/v1/locais/?skip=-1")

        # Assert
        assert response.status_code in [400, 500]

    def test_listar_locais_com_limit_invalido(self, client):
        """Testa que limit inválido retorna erro"""
        # Act
        response = client.get("/api/v1/locais/?limit=0")

        # Assert
        assert response.status_code in [400, 500]


class TestUpdateLocalAPI:
    """Testes para PUT /api/v1/locais/{local_id}"""

    def test_atualizar_local_com_sucesso(self, client):
        """Testa atualização de local via API"""
        # Arrange - Cria local
        create_data = {
            "tipo": "Metrô",
            "descricao": "Estação Original",
            "bairro": "Centro"
        }
        create_response = client.post("/api/v1/locais/", json=create_data)
        local_id = create_response.json()["id"]

        # Act
        update_data = {
            "tipo": "Metrô Linha 3",
            "descricao": "Estação Atualizada",
            "bairro": "Centro"
        }
        response = client.put(f"/api/v1/locais/{local_id}", json=update_data)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["tipo"] == "Metrô Linha 3"
        assert data["descricao"] == "Estação Atualizada"

    def test_atualizar_local_inexistente(self, client):
        """Testa atualização de local que não existe"""
        # Arrange
        update_data = {
            "tipo": "Metrô",
            "descricao": "Descrição",
            "bairro": "Centro"
        }

        # Act
        response = client.put("/api/v1/locais/9999", json=update_data)

        # Assert
        assert response.status_code == 404


class TestDeleteLocalAPI:
    """Testes para DELETE /api/v1/locais/{local_id}"""

    def test_deletar_local_com_sucesso(self, client):
        """Testa exclusão de local via API"""
        # Arrange - Cria local
        create_data = {
            "tipo": "Ônibus",
            "descricao": "Terminal Para Deletar",
            "bairro": "Brás"
        }
        create_response = client.post("/api/v1/locais/", json=create_data)
        local_id = create_response.json()["id"]

        # Act
        response = client.delete(f"/api/v1/locais/{local_id}")

        # Assert
        assert response.status_code in [200, 204]

        # Verifica que foi deletado
        get_response = client.get(f"/api/v1/locais/{local_id}")
        assert get_response.status_code == 404

    def test_deletar_local_inexistente(self, client):
        """Testa exclusão de local que não existe"""
        # Act
        response = client.delete("/api/v1/locais/9999")

        # Assert
        assert response.status_code == 404


class TestGetLocalsByBairroAPI:
    """Testes para GET /api/v1/locais/bairro/{bairro}"""

    def test_buscar_por_bairro(self, client):
        """Testa busca de locais por bairro"""
        # Arrange - Cria locais
        locais_data = [
            {"tipo": "Metrô", "descricao": "Estação A", "bairro": "Centro"},
            {"tipo": "Ônibus", "descricao": "Terminal B", "bairro": "Centro"},
            {"tipo": "Parque", "descricao": "Parque C", "bairro": "Moema"},
        ]
        for local_data in locais_data:
            client.post("/api/v1/locais/", json=local_data)

        # Act
        response = client.get("/api/v1/locais/bairro/Centro")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2
        assert all(l["bairro"] == "Centro" for l in data)

    def test_buscar_por_bairro_sem_resultados(self, client):
        """Testa busca por bairro sem resultados retorna lista vazia"""
        # Act
        response = client.get("/api/v1/locais/bairro/BairroxInexistente999")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

