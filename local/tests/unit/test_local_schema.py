"""
Testes unitários para os schemas Pydantic de Local
Testa validações, serialização e deserialização
"""
import pytest
from datetime import datetime
from pydantic import ValidationError
from local.src.application.schemas.local_schema import (
    LocalCreate,
    LocalUpdate,
    LocalResponse,
    LocalListResponse,
)


class TestLocalCreateSchema:
    """Testes para o schema LocalCreate"""

    def test_criar_schema_com_dados_validos(self):
        """Testa criação de schema com dados válidos"""
        # Arrange & Act
        data = {
            "tipo": "Metrô",
            "descricao": "Estação Sé - Plataforma Central",
            "bairro": "Centro"
        }

        schema = LocalCreate(**data)

        # Assert
        assert schema.tipo == "Metrô"
        assert schema.descricao == "Estação Sé - Plataforma Central"
        assert schema.bairro == "Centro"

    def test_schema_com_tipo_vazio_falha(self):
        """Testa que tipo vazio não é aceito"""
        # Arrange
        data = {
            "tipo": "",
            "descricao": "Descrição válida",
            "bairro": "Centro"
        }

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            LocalCreate(**data)

        assert "tipo" in str(exc_info.value).lower()

    def test_schema_com_descricao_vazia_falha(self):
        """Testa que descrição vazia não é aceita"""
        # Arrange
        data = {
            "tipo": "Metrô",
            "descricao": "",
            "bairro": "Centro"
        }

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            LocalCreate(**data)

        assert "descricao" in str(exc_info.value).lower()

    def test_schema_com_bairro_vazio_falha(self):
        """Testa que bairro vazio não é aceito"""
        # Arrange
        data = {
            "tipo": "Metrô",
            "descricao": "Descrição válida",
            "bairro": ""
        }

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            LocalCreate(**data)

        assert "bairro" in str(exc_info.value).lower()

    def test_schema_com_campo_faltando_falha(self):
        """Testa que campo obrigatório faltando causa erro"""
        # Arrange - faltando bairro
        data = {
            "tipo": "Metrô",
            "descricao": "Estação Sé"
        }

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            LocalCreate(**data)

        assert "bairro" in str(exc_info.value).lower()

    def test_schema_serializa_para_dict(self):
        """Testa serialização para dicionário"""
        # Arrange
        schema = LocalCreate(
            tipo="Parque",
            descricao="Parque Ibirapuera",
            bairro="Moema"
        )

        # Act
        data = schema.model_dump()

        # Assert
        assert data["tipo"] == "Parque"
        assert data["descricao"] == "Parque Ibirapuera"
        assert data["bairro"] == "Moema"

    def test_schema_serializa_para_json(self):
        """Testa serialização para JSON"""
        # Arrange
        schema = LocalCreate(
            tipo="Shopping",
            descricao="Piso Térreo",
            bairro="Centro"
        )

        # Act
        json_str = schema.model_dump_json()

        # Assert
        assert "Shopping" in json_str
        assert "Centro" in json_str


class TestLocalUpdateSchema:
    """Testes para o schema LocalUpdate"""

    def test_update_schema_com_dados_validos(self):
        """Testa schema de update com dados válidos"""
        # Arrange & Act
        schema = LocalUpdate(
            tipo="Aeroporto",
            descricao="Terminal 2 - Embarque",
            bairro="Cumbica"
        )

        # Assert
        assert schema.tipo == "Aeroporto"
        assert schema.descricao == "Terminal 2 - Embarque"
        assert schema.bairro == "Cumbica"

    def test_update_schema_com_campos_opcionais(self):
        """Testa que todos os campos do update são opcionais"""
        # Arrange & Act
        schema = LocalUpdate()

        # Assert - todos os campos devem ser None quando omitidos
        assert schema.tipo is None
        assert schema.descricao is None
        assert schema.bairro is None

    def test_update_schema_apenas_tipo(self):
        """Testa update apenas do tipo"""
        # Arrange & Act
        schema = LocalUpdate(tipo="Rodoviária")

        # Assert
        assert schema.tipo == "Rodoviária"
        assert schema.descricao is None
        assert schema.bairro is None

    def test_update_schema_apenas_bairro(self):
        """Testa update apenas do bairro"""
        # Arrange & Act
        schema = LocalUpdate(bairro="Pinheiros")

        # Assert
        assert schema.tipo is None
        assert schema.descricao is None
        assert schema.bairro == "Pinheiros"

    def test_update_schema_com_tipo_vazio_falha(self):
        """Testa que tipo vazio no update não é aceito"""
        # Arrange & Act & Assert
        with pytest.raises(ValidationError):
            LocalUpdate(tipo="")


class TestLocalResponseSchema:
    """Testes para o schema LocalResponse"""

    def test_response_schema_com_todos_campos(self):
        """Testa schema de resposta com todos os campos"""
        # Arrange & Act
        now = datetime.now()
        schema = LocalResponse(
            id=1,
            tipo="Metrô",
            descricao="Estação Central",
            bairro="Centro",
            created_at=now
        )

        # Assert
        assert schema.id == 1
        assert schema.tipo == "Metrô"
        assert schema.descricao == "Estação Central"
        assert schema.bairro == "Centro"
        assert schema.created_at == now
        assert schema.updated_at is None

    def test_response_schema_sem_id_falha(self):
        """Testa que id é obrigatório no response schema"""
        # Arrange & Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            LocalResponse(
                tipo="Metrô",
                descricao="Estação Central",
                bairro="Centro",
                created_at=datetime.now()
            )

        assert "id" in str(exc_info.value).lower()

    def test_response_schema_serializa_para_json(self):
        """Testa serialização do response para JSON"""
        # Arrange
        schema = LocalResponse(
            id=1,
            tipo="Parque",
            descricao="Parque do Povo",
            bairro="Liberdade",
            created_at=datetime.now()
        )

        # Act
        json_str = schema.model_dump_json()

        # Assert
        assert "Parque" in json_str
        assert "Liberdade" in json_str


class TestLocalListResponseSchema:
    """Testes para o schema LocalListResponse"""

    def test_list_response_schema_vazio(self):
        """Testa schema de listagem com lista vazia"""
        # Arrange & Act
        schema = LocalListResponse(
            locals=[],
            total=0,
            skip=0,
            limit=100
        )

        # Assert
        assert schema.locals == []
        assert schema.total == 0
        assert schema.skip == 0
        assert schema.limit == 100

    def test_list_response_schema_com_locais(self):
        """Testa schema de listagem com dados"""
        # Arrange
        now = datetime.now()
        locais = [
            LocalResponse(id=1, tipo="Metrô", descricao="Estação A", bairro="Centro", created_at=now),
            LocalResponse(id=2, tipo="Ônibus", descricao="Terminal B", bairro="Tatuapé", created_at=now),
        ]

        # Act
        schema = LocalListResponse(
            locals=locais,
            total=2,
            skip=0,
            limit=100
        )

        # Assert
        assert len(schema.locals) == 2
        assert schema.total == 2

    def test_list_response_schema_paginacao(self):
        """Testa schema de listagem com paginação customizada"""
        # Arrange & Act
        schema = LocalListResponse(
            locals=[],
            total=50,
            skip=10,
            limit=10
        )

        # Assert
        assert schema.skip == 10
        assert schema.limit == 10
        assert schema.total == 50
