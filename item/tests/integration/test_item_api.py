"""
Testes de integração da API REST de Item
Testa os endpoints HTTP, validações, status codes e serialização
"""
import pytest
import pytest_asyncio
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from item.src.infrastructure.database.config import Base, get_session
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


class TestCreateItemAPI:
    """Testes para POST /api/v1/items"""
    
    def test_criar_item_com_sucesso(self, client):
        """Testa criação de item via API com dados válidos"""
        # Arrange
        item_data = {
            "nome": "Notebook Dell",
            "categoria": "Eletrônicos",
            "data_encontro": (datetime.now() - timedelta(days=1)).isoformat(),
            "descricao": "Notebook Dell Inspiron 15 preto",
            "local_id": 1,
            "responsavel_id": 1
        }
        
        # Act
        response = client.post("/api/v1/items/", json=item_data)
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["nome"] == "Notebook Dell"
        assert data["categoria"] == "Eletrônicos"
        assert data["status"] == "disponivel"
        assert "id" in data
        assert "created_at" in data
    
    def test_criar_item_com_dados_invalidos(self, client):
        """Testa criação de item com dados inválidos retorna 422"""
        # Arrange - faltando campo obrigatório
        item_data = {
            "nome": "Item teste",
            "categoria": "Teste",
            # "data_encontro" está faltando (obrigatório)
            "descricao": "Descrição teste",
            "local_id": 1,
            "responsavel_id": 1
        }
        
        # Act
        response = client.post("/api/v1/items/", json=item_data)
        
        # Assert
        assert response.status_code == 422
    
    def test_criar_item_com_nome_vazio(self, client):
        """Testa que não aceita nome vazio"""
        # Arrange
        item_data = {
            "nome": "",
            "categoria": "Teste",
            "data_encontro": datetime.now().isoformat(),
            "descricao": "Descrição teste",
            "local_id": 1,
            "responsavel_id": 1
        }
        
        # Act
        response = client.post("/api/v1/items/", json=item_data)
        
        # Assert
        assert response.status_code == 400 or response.status_code == 422
    
    def test_criar_item_com_data_futura(self, client):
        """Testa que não aceita data de encontro futura"""
        # Arrange
        item_data = {
            "nome": "Item teste",
            "categoria": "Teste",
            "data_encontro": (datetime.now() + timedelta(days=1)).isoformat(),
            "descricao": "Descrição teste",
            "local_id": 1,
            "responsavel_id": 1
        }
        
        # Act
        response = client.post("/api/v1/items/", json=item_data)
        
        # Assert
        assert response.status_code == 400
        assert "futuro" in response.json()["detail"].lower()
    
    def test_criar_item_com_local_id_invalido(self, client):
        """Testa que não aceita local_id <= 0"""
        # Arrange
        item_data = {
            "nome": "Item teste",
            "categoria": "Teste",
            "data_encontro": datetime.now().isoformat(),
            "descricao": "Descrição teste",
            "local_id": 0,
            "responsavel_id": 1
        }
        
        # Act
        response = client.post("/api/v1/items/", json=item_data)
        
        # Assert
        assert response.status_code in [400, 422]


class TestGetItemByIdAPI:
    """Testes para GET /api/v1/items/{id}"""
    
    def test_buscar_item_existente(self, client):
        """Testa busca de item que existe"""
        # Arrange - Primeiro cria um item
        item_data = {
            "nome": "Item para buscar",
            "categoria": "Teste",
            "data_encontro": datetime.now().isoformat(),
            "descricao": "Descrição teste",
            "local_id": 1,
            "responsavel_id": 1
        }
        create_response = client.post("/api/v1/items/", json=item_data)
        item_id = create_response.json()["id"]
        
        # Act
        response = client.get(f"/api/v1/items/{item_id}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == item_id
        assert data["nome"] == "Item para buscar"
    
    def test_buscar_item_inexistente(self, client):
        """Testa busca de item que não existe retorna 404"""
        # Act
        response = client.get("/api/v1/items/99999")
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower() or "não encontrado" in response.json()["detail"].lower()
    
    def test_buscar_item_com_id_invalido(self, client):
        """Testa busca com ID inválido retorna 400"""
        # Act
        response = client.get("/api/v1/items/0")
        
        # Assert
        assert response.status_code == 400
        assert "maior que zero" in response.json()["detail"].lower()
    
    def test_buscar_item_com_id_string(self, client):
        """Testa que ID não numérico retorna 422"""
        # Act
        response = client.get("/api/v1/items/abc")
        
        # Assert
        assert response.status_code == 422


class TestListItemsAPI:
    """Testes para GET /api/v1/items"""
    
    def test_listar_todos_itens(self, client):
        """Testa listagem de itens"""
        # Arrange - Cria alguns itens
        for i in range(3):
            item_data = {
                "nome": f"Item {i}",
                "categoria": "Teste",
                "data_encontro": datetime.now().isoformat(),
                "descricao": f"Descrição {i}",
                "local_id": 1,
                "responsavel_id": 1
            }
            client.post("/api/v1/items/", json=item_data)
        
        # Act
        response = client.get("/api/v1/items/")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "items" in data or isinstance(data, list)
        if isinstance(data, dict):
            assert len(data["items"]) >= 3
        else:
            assert len(data) >= 3
    
    def test_listar_itens_com_paginacao(self, client):
        """Testa listagem com parâmetros de paginação"""
        # Arrange - Cria alguns itens
        for i in range(5):
            item_data = {
                "nome": f"Item Paginação {i}",
                "categoria": "Teste",
                "data_encontro": datetime.now().isoformat(),
                "descricao": f"Descrição {i}",
                "local_id": 1,
                "responsavel_id": 1
            }
            client.post("/api/v1/items/", json=item_data)
        
        # Act
        response = client.get("/api/v1/items/?skip=0&limit=3")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        if isinstance(data, dict):
            assert len(data["items"]) <= 3
        else:
            assert len(data) <= 3
    
    def test_listar_itens_com_skip_negativo(self, client):
        """Testa que skip negativo retorna erro"""
        # Act
        response = client.get("/api/v1/items/?skip=-1")
        
        # Assert
        assert response.status_code == 400
    
    def test_listar_itens_com_limit_invalido(self, client):
        """Testa que limit > 1000 retorna erro"""
        # Act
        response = client.get("/api/v1/items/?limit=1001")
        
        # Assert
        assert response.status_code == 400


class TestUpdateItemAPI:
    """Testes para PUT /api/v1/items/{id}"""
    
    def test_atualizar_item_com_sucesso(self, client):
        """Testa atualização de item via API"""
        # Arrange - Cria um item
        item_data = {
            "nome": "Item Original",
            "categoria": "Teste",
            "data_encontro": datetime.now().isoformat(),
            "descricao": "Descrição original",
            "local_id": 1,
            "responsavel_id": 1
        }
        create_response = client.post("/api/v1/items/", json=item_data)
        item_id = create_response.json()["id"]
        
        # Act - Atualiza o item
        update_data = {
            "nome": "Item Atualizado",
            "categoria": "Teste Atualizado",
            "data_encontro": datetime.now().isoformat(),
            "descricao": "Descrição atualizada",
            "local_id": 1,
            "responsavel_id": 1
        }
        response = client.put(f"/api/v1/items/{item_id}", json=update_data)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["nome"] == "Item Atualizado"
        assert data["descricao"] == "Descrição atualizada"
    
    def test_atualizar_item_inexistente(self, client):
        """Testa atualização de item que não existe retorna 404"""
        # Arrange
        update_data = {
            "nome": "Item teste",
            "categoria": "Teste",
            "data_encontro": datetime.now().isoformat(),
            "descricao": "Descrição teste",
            "local_id": 1,
            "responsavel_id": 1
        }
        
        # Act
        response = client.put("/api/v1/items/99999", json=update_data)
        
        # Assert
        assert response.status_code == 404
    
    def test_atualizar_item_nao_pode_marcar_como_devolvido(self, client):
        """Testa que não pode marcar como devolvido pelo update"""
        # Arrange - Cria um item disponível
        item_data = {
            "nome": "Item teste",
            "categoria": "Teste",
            "data_encontro": datetime.now().isoformat(),
            "descricao": "Descrição teste",
            "local_id": 1,
            "responsavel_id": 1
        }
        create_response = client.post("/api/v1/items/", json=item_data)
        item_id = create_response.json()["id"]
        
        # Act - Tenta mudar status para devolvido
        update_data = {
            "nome": "Item teste",
            "categoria": "Teste",
            "data_encontro": datetime.now().isoformat(),
            "descricao": "Descrição teste",
            "status": "devolvido",
            "local_id": 1,
            "responsavel_id": 1
        }
        response = client.put(f"/api/v1/items/{item_id}", json=update_data)
        
        # Assert
        assert response.status_code == 400
        assert "devolvido" in response.json()["detail"].lower()


class TestDeleteItemAPI:
    """Testes para DELETE /api/v1/items/{id}"""
    
    def test_deletar_item_com_sucesso(self, client):
        """Testa exclusão de item via API"""
        # Arrange - Cria um item
        item_data = {
            "nome": "Item para deletar",
            "categoria": "Teste",
            "data_encontro": datetime.now().isoformat(),
            "descricao": "Descrição teste",
            "local_id": 1,
            "responsavel_id": 1
        }
        create_response = client.post("/api/v1/items/", json=item_data)
        item_id = create_response.json()["id"]
        
        # Act
        response = client.delete(f"/api/v1/items/{item_id}")
        
        # Assert
        assert response.status_code == 204 or response.status_code == 200
        
        # Verifica que foi deletado
        get_response = client.get(f"/api/v1/items/{item_id}")
        assert get_response.status_code == 404
    
    def test_deletar_item_inexistente(self, client):
        """Testa exclusão de item que não existe retorna 404"""
        # Act
        response = client.delete("/api/v1/items/99999")
        
        # Assert
        assert response.status_code == 404
    
    def test_deletar_item_devolvido_nao_permitido(self, client):
        """Testa que não pode deletar item devolvido"""
        # Arrange - Cria um item e marca como devolvido
        item_data = {
            "nome": "Item teste",
            "categoria": "Teste",
            "data_encontro": datetime.now().isoformat(),
            "descricao": "Descrição teste",
            "local_id": 1,
            "responsavel_id": 1
        }
        create_response = client.post("/api/v1/items/", json=item_data)
        item_id = create_response.json()["id"]
        
        # Marca como devolvido (assumindo que existe endpoint ou método)
        # Nota: Ajustar conforme implementação real
        
        # Act
        response = client.delete(f"/api/v1/items/{item_id}")
        
        # Assert - Pode passar se item não for devolvido ainda
        # Este teste precisa ser ajustado conforme a implementação


class TestFilterItemsAPI:
    """Testes para filtros de busca"""
    
    def test_buscar_por_categoria(self, client):
        """Testa busca de itens por categoria"""
        # Arrange - Cria itens de diferentes categorias
        for categoria in ["Eletrônicos", "Documentos", "Acessórios"]:
            item_data = {
                "nome": f"Item {categoria}",
                "categoria": categoria,
                "data_encontro": datetime.now().isoformat(),
                "descricao": f"Descrição {categoria}",
                "local_id": 1,
                "responsavel_id": 1
            }
            client.post("/api/v1/items/", json=item_data)
        
        # Act
        response = client.get("/api/v1/items/categoria/Eletrônicos")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        if isinstance(data, list):
            assert all(item["categoria"] == "Eletrônicos" for item in data)
        else:
            assert all(item["categoria"] == "Eletrônicos" for item in data["items"])
    
    def test_buscar_por_categoria_vazia(self, client):
        """Testa que categoria vazia retorna erro"""
        # Act
        response = client.get("/api/v1/items/categoria/")
        
        # Assert
        assert response.status_code in [400, 404, 422]
    
    async def test_buscar_por_status_disponivel(self, client):
        """Testa a busca por status 'disponivel'"""
        # Arrange - Cria itens
        for i in range(2):
            item_data = {
                "nome": f"Item disponível {i}",
                "categoria": "Teste",
                "data_encontro": datetime.now().isoformat(),
                "descricao": f"Descrição {i}",
                "local_id": 1,
                "responsavel_id": 1
            }
            client.post("/api/v1/items/", json=item_data)
        
        # Act
        response = client.get("/api/v1/items/status/disponivel")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        if isinstance(data, list):
            assert all(item["status"] == "disponivel" for item in data)
        else:
            assert all(item["status"] == "disponivel" for item in data["items"])
    
    def test_buscar_por_status_invalido(self, client):
        """Testa que status inválido retorna erro"""
        # Act
        response = client.get("/api/v1/items/status/status_invalido")
        
        # Assert
        assert response.status_code == 400
        assert "inválido" in response.json()["detail"].lower()


class TestAPIResponseFormat:
    """Testes para formato de resposta da API"""
    
    def test_response_headers(self, client):
        """Testa que headers corretos são retornados"""
        # Act
        response = client.get("/api/v1/items/")
        
        # Assert
        assert response.headers["content-type"] == "application/json"
    
    def test_response_structure_item_create(self, client):
        """Testa estrutura da resposta ao criar item"""
        # Arrange
        item_data = {
            "nome": "Item estrutura",
            "categoria": "Teste",
            "data_encontro": datetime.now().isoformat(),
            "descricao": "Descrição teste",
            "local_id": 1,
            "responsavel_id": 1
        }
        
        # Act
        response = client.post("/api/v1/items/", json=item_data)
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        
        # Campos obrigatórios na resposta
        required_fields = ["id", "nome", "categoria", "data_encontro", 
                          "descricao", "status", "local_id", "responsavel_id", 
                          "created_at"]
        
        for field in required_fields:
            assert field in data, f"Campo {field} não encontrado na resposta"
    
    def test_error_response_structure(self, client):
        """Testa estrutura de resposta de erro"""
        # Act - Tenta criar item inválido
        response = client.post("/api/v1/items/", json={})
        
        # Assert
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
