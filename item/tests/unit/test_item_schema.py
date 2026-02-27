"""
Testes unitários para os schemas Pydantic de Item
Testa validações, serialização e deserialização
"""
import pytest
from datetime import datetime, timedelta
from pydantic import ValidationError
from item.src.application.schemas.item_schema import (
    ItemCreate,
    ItemResponse,
    ItemUpdate,
    ItemListResponse
)


class TestItemCreateSchema:
    """Testes para o schema ItemCreate"""
    
    def test_criar_schema_com_dados_validos(self):
        """Testa criação de schema com dados válidos"""
        # Arrange & Act
        data = {
            "nome": "Notebook Dell",
            "categoria": "Eletrônicos",
            "data_encontro": datetime.now() - timedelta(days=1),
            "descricao": "Notebook Dell Inspiron 15 preto",
            "local_id": 1,
            "responsavel_id": 1
        }
        
        schema = ItemCreate(**data)
        
        # Assert
        assert schema.nome == "Notebook Dell"
        assert schema.categoria == "Eletrônicos"
        assert schema.local_id == 1
        assert schema.responsavel_id == 1
    
    def test_schema_com_nome_vazio_falha(self):
        """Testa que nome vazio não é aceito"""
        # Arrange
        data = {
            "nome": "",
            "categoria": "Teste",
            "data_encontro": datetime.now(),
            "descricao": "Descrição teste",
            "local_id": 1,
            "responsavel_id": 1
        }
        
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ItemCreate(**data)
        
        assert "nome" in str(exc_info.value).lower()
    
    def test_schema_com_categoria_vazia_falha(self):
        """Testa que categoria vazia não é aceita"""
        # Arrange
        data = {
            "nome": "Item teste",
            "categoria": "",
            "data_encontro": datetime.now(),
            "descricao": "Descrição teste",
            "local_id": 1,
            "responsavel_id": 1
        }
        
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ItemCreate(**data)
        
        assert "categoria" in str(exc_info.value).lower()
    
    def test_schema_com_descricao_vazia_falha(self):
        """Testa que descrição vazia não é aceita"""
        # Arrange
        data = {
            "nome": "Item teste",
            "categoria": "Teste",
            "data_encontro": datetime.now(),
            "descricao": "",
            "local_id": 1,
            "responsavel_id": 1
        }
        
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ItemCreate(**data)
        
        assert "descricao" in str(exc_info.value).lower()
    
    def test_schema_com_campo_faltando_falha(self):
        """Testa que campo obrigatório faltando causa erro"""
        # Arrange - faltando data_encontro
        data = {
            "nome": "Item teste",
            "categoria": "Teste",
            "descricao": "Descrição teste",
            "local_id": 1,
            "responsavel_id": 1
        }
        
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ItemCreate(**data)
        
        assert "data_encontro" in str(exc_info.value).lower()
    
    def test_schema_com_local_id_zero_ou_negativo(self):
        """Testa que local_id <= 0 não é aceito"""
        # Arrange
        data = {
            "nome": "Item teste",
            "categoria": "Teste",
            "data_encontro": datetime.now(),
            "descricao": "Descrição teste",
            "local_id": 0,
            "responsavel_id": 1
        }
        
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ItemCreate(**data)
        
        assert "local_id" in str(exc_info.value).lower()
    
    def test_schema_com_responsavel_id_zero_ou_negativo(self):
        """Testa que responsavel_id <= 0 não é aceito"""
        # Arrange
        data = {
            "nome": "Item teste",
            "categoria": "Teste",
            "data_encontro": datetime.now(),
            "descricao": "Descrição teste",
            "local_id": 1,
            "responsavel_id": -1
        }
        
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ItemCreate(**data)
        
        assert "responsavel_id" in str(exc_info.value).lower()
    
    def test_schema_serializa_para_dict(self):
        """Testa que schema pode ser serializado para dict"""
        # Arrange
        data = {
            "nome": "Item teste",
            "categoria": "Teste",
            "data_encontro": datetime.now(),
            "descricao": "Descrição teste",
            "local_id": 1,
            "responsavel_id": 1
        }
        
        schema = ItemCreate(**data)
        
        # Act
        result = schema.model_dump()
        
        # Assert
        assert isinstance(result, dict)
        assert result["nome"] == "Item teste"
        assert result["categoria"] == "Teste"
    
    def test_schema_serializa_para_json(self):
        """Testa que schema pode ser serializado para JSON"""
        # Arrange
        data = {
            "nome": "Item teste",
            "categoria": "Teste",
            "data_encontro": datetime.now(),
            "descricao": "Descrição teste",
            "local_id": 1,
            "responsavel_id": 1
        }
        
        schema = ItemCreate(**data)
        
        # Act
        result = schema.model_dump_json()
        
        # Assert
        assert isinstance(result, str)
        assert "Item teste" in result


class TestItemUpdateSchema:
    """Testes para o schema ItemUpdate"""
    
    def test_update_schema_com_dados_validos(self):
        """Testa schema de update com dados válidos"""
        # Arrange & Act
        data = {
            "nome": "Notebook Atualizado",
            "categoria": "Eletrônicos",
            "data_encontro": datetime.now(),
            "descricao": "Descrição atualizada",
            "status": "em_analise",
            "local_id": 1,
            "responsavel_id": 1
        }
        
        schema = ItemUpdate(**data)
        
        # Assert
        assert schema.nome == "Notebook Atualizado"
        assert schema.status == "em_analise"
    
    def test_update_schema_com_status_valido(self):
        """Testa que status válidos são aceitos"""
        # Arrange
        status_validos = ["disponivel", "devolvido", "em_analise"]
        
        for status in status_validos:
            data = {
                "nome": "Item teste",
                "categoria": "Teste",
                "data_encontro": datetime.now(),
                "descricao": "Descrição teste",
                "status": status,
                "local_id": 1,
                "responsavel_id": 1
            }
            
            # Act
            schema = ItemUpdate(**data)
            
            # Assert
            assert schema.status.lower().replace('í', 'i').replace('á', 'a').replace('é', 'e') in ["disponivel", "devolvido", "em_analise"]
    
    def test_update_schema_aceita_qualquer_status(self):
        """Testa que schema aceita qualquer string como status (validação é no use case)"""
        # Arrange
        data = {
            "nome": "Item teste",
            "categoria": "Teste",
            "data_encontro": datetime.now(),
            "descricao": "Descrição teste",
            "status": "qualquer_status",  # Schema não valida, use case valida
            "local_id": 1,
            "responsavel_id": 1
        }
        
        # Act
        schema = ItemUpdate(**data)
        
        # Assert
        assert schema.status == "qualquer_status"
        # Nota: Validação de status é feita no Use Case, não no Schema


class TestItemResponseSchema:
    """Testes para o schema ItemResponse"""
    
    def test_response_schema_com_todos_campos(self):
        """Testa schema de resposta com todos os campos"""
        # Arrange & Act
        data = {
            "id": 1,
            "nome": "Item teste",
            "categoria": "Teste",
            "data_encontro": datetime.now(),
            "descricao": "Descrição teste",
            "status": "disponivel",
            "local_id": 1,
            "responsavel_id": 1,
            "created_at": datetime.now(),
            "updated_at": None
        }
        
        schema = ItemResponse(**data)
        
        # Assert
        assert schema.id == 1
        assert schema.nome == "Item teste"
        assert schema.created_at is not None
    
    def test_response_schema_sem_id_falha(self):
        """Testa que ID é obrigatório no response"""
        # Arrange
        data = {
            "nome": "Item teste",
            "categoria": "Teste",
            "data_encontro": datetime.now(),
            "descricao": "Descrição teste",
            "status": "disponivel",
            "local_id": 1,
            "responsavel_id": 1,
            "created_at": datetime.now()
        }
        
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ItemResponse(**data)
        
        assert "id" in str(exc_info.value).lower()
    
    def test_response_schema_updated_at_opcional(self):
        """Testa que updated_at é opcional"""
        # Arrange
        data = {
            "id": 1,
            "nome": "Item teste",
            "categoria": "Teste",
            "data_encontro": datetime.now(),
            "descricao": "Descrição teste",
            "status": "disponivel",
            "local_id": 1,
            "responsavel_id": 1,
            "created_at": datetime.now()
        }
        
        # Act
        schema = ItemResponse(**data)
        
        # Assert
        assert schema.updated_at is None
    
    def test_response_schema_serializa_para_json(self):
        """Testa serialização para JSON"""
        # Arrange
        data = {
            "id": 1,
            "nome": "Item teste",
            "categoria": "Teste",
            "data_encontro": datetime.now(),
            "descricao": "Descrição teste",
            "status": "disponivel",
            "local_id": 1,
            "responsavel_id": 1,
            "created_at": datetime.now(),
            "updated_at": None
        }
        
        schema = ItemResponse(**data)
        
        # Act
        result = schema.model_dump_json()
        
        # Assert
        assert isinstance(result, str)
        assert '"id":1' in result.replace(" ", "")
        assert "Item teste" in result


class TestItemListResponseSchema:
    """Testes para o schema ItemListResponse"""
    
    def test_list_response_schema_vazio(self):
        """Testa schema de lista vazia"""
        # Arrange & Act
        data = {
            "items": [],
            "total": 0,
            "skip": 0,
            "limit": 100
        }
        
        schema = ItemListResponse(**data)
        
        # Assert
        assert len(schema.items) == 0
        assert schema.total == 0
    
    def test_list_response_schema_com_itens(self):
        """Testa schema de lista com itens"""
        # Arrange
        item_data = {
            "id": 1,
            "nome": "Item teste",
            "categoria": "Teste",
            "data_encontro": datetime.now(),
            "descricao": "Descrição teste",
            "status": "disponivel",
            "local_id": 1,
            "responsavel_id": 1,
            "created_at": datetime.now(),
            "updated_at": None
        }
        
        data = {
            "items": [item_data, item_data],
            "total": 2,
            "skip": 0,
            "limit": 100
        }
        
        # Act
        schema = ItemListResponse(**data)
        
        # Assert
        assert len(schema.items) == 2
        assert schema.total == 2
        assert all(isinstance(item, ItemResponse) for item in schema.items)
    
    def test_list_response_schema_paginacao(self):
        """Testa schema com informações de paginação"""
        # Arrange
        data = {
            "items": [],
            "total": 100,
            "skip": 10,
            "limit": 20
        }
        
        # Act
        schema = ItemListResponse(**data)
        
        # Assert
        assert schema.skip == 10
        assert schema.limit == 20
        assert schema.total == 100


class TestSchemaValidacoes:
    """Testes para validações específicas dos schemas"""
    
    def test_validacao_nome_tamanho_maximo(self):
        """Testa validação de tamanho máximo do nome"""
        # Arrange - nome muito longo
        data = {
            "nome": "A" * 300,  # 300 caracteres
            "categoria": "Teste",
            "data_encontro": datetime.now(),
            "descricao": "Descrição teste",
            "local_id": 1,
            "responsavel_id": 1
        }
        
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ItemCreate(**data)
        
        assert "nome" in str(exc_info.value).lower()
    
    def test_validacao_categoria_tamanho_maximo(self):
        """Testa validação de tamanho máximo da categoria"""
        # Arrange - categoria muito longa
        data = {
            "nome": "Item teste",
            "categoria": "A" * 150,  # 150 caracteres
            "data_encontro": datetime.now(),
            "descricao": "Descrição teste",
            "local_id": 1,
            "responsavel_id": 1
        }
        
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ItemCreate(**data)
        
        assert "categoria" in str(exc_info.value).lower()
    
    def test_validacao_tipo_data_incorreto(self):
        """Testa que tipo incorreto de data causa erro"""
        # Arrange
        data = {
            "nome": "Item teste",
            "categoria": "Teste",
            "data_encontro": "data_invalida",  # String ao invés de datetime
            "descricao": "Descrição teste",
            "local_id": 1,
            "responsavel_id": 1
        }
        
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ItemCreate(**data)
        
        assert "data_encontro" in str(exc_info.value).lower()
    
    def test_validacao_tipo_id_incorreto(self):
        """Testa que tipo incorreto de ID causa erro"""
        # Arrange
        data = {
            "nome": "Item teste",
            "categoria": "Teste",
            "data_encontro": datetime.now(),
            "descricao": "Descrição teste",
            "local_id": "um",  # String ao invés de int
            "responsavel_id": 1
        }
        
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ItemCreate(**data)
        
        assert "local_id" in str(exc_info.value).lower()
