"""
Testes unitários para os schemas Pydantic de Reclamante
Testa validações, serialização e deserialização
"""
import pytest
from pydantic import ValidationError
from reclamante.src.application.schemas.reclamante_schema import (
    ReclamanteCreate,
    ReclamanteUpdate,
    ReclamanteResponse,
    ReclamanteListResponse,
)


class TestReclamanteCreateSchema:
    """Testes para o schema ReclamanteCreate"""

    def test_criar_schema_com_dados_validos(self):
        """Testa criação de schema com dados válidos"""
        # Arrange & Act
        data = {
            "nome": "João Silva",
            "documento": "123.456.789-00",
            "telefone": "11999999999",
        }

        schema = ReclamanteCreate(**data)

        # Assert
        assert schema.nome == data["nome"]
        assert schema.documento == data["documento"]
        assert schema.telefone == data["telefone"]

    def test_schema_com_nome_vazio_falha(self):
        """Testa que nome vazio não é aceito"""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ReclamanteCreate(nome="", documento="123", telefone="11999999999")

        assert "nome" in str(exc_info.value).lower()

    def test_schema_com_telefone_vazio_falha(self):
        """Testa que telefone vazio não é aceito"""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ReclamanteCreate(nome="João", documento="123", telefone="")

        assert "telefone" in str(exc_info.value).lower()

    def test_schema_com_nome_longo_demais_falha(self):
        """Testa limite máximo de nome"""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ReclamanteCreate(nome="A" * 256, documento="123", telefone="11999999999")

        assert "nome" in str(exc_info.value).lower()

    def test_schema_com_telefone_longo_demais_falha(self):
        """Testa limite máximo de telefone"""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ReclamanteCreate(nome="João", documento="123", telefone="9" * 101)

        assert "telefone" in str(exc_info.value).lower()

    def test_schema_com_campo_faltando_falha(self):
        """Testa que campo obrigatório faltando causa erro"""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ReclamanteCreate(nome="João", telefone="11999999999")

        assert "documento" in str(exc_info.value).lower()

    def test_schema_serializa_para_dict(self):
        """Testa serialização para dict"""
        # Arrange
        schema = ReclamanteCreate(
            nome="João Silva",
            documento="123.456.789-00",
            telefone="11999999999",
        )

        # Act
        result = schema.model_dump()

        # Assert
        assert isinstance(result, dict)
        assert result["nome"] == "João Silva"

    def test_schema_serializa_para_json(self):
        """Testa serialização para JSON"""
        # Arrange
        schema = ReclamanteCreate(
            nome="João Silva",
            documento="123.456.789-00",
            telefone="11999999999",
        )

        # Act
        result = schema.model_dump_json()

        # Assert
        assert isinstance(result, str)
        assert "João Silva" in result

    def test_schema_documento_vazio_eh_aceito_no_schema(self):
        """Documenta comportamento atual: documento vazio passa no schema"""
        # Arrange & Act
        schema = ReclamanteCreate(nome="João", documento="", telefone="11999999999")

        # Assert
        assert schema.documento == ""


class TestReclamanteUpdateSchema:
    """Testes para o schema ReclamanteUpdate"""

    def test_update_schema_com_dados_validos(self):
        """Testa schema de update com dados válidos"""
        # Arrange & Act
        schema = ReclamanteUpdate(
            nome="João Silva",
            documento="123.456.789-00",
            telefone="11999999999",
        )

        # Assert
        assert schema.nome == "João Silva"
        assert schema.documento == "123.456.789-00"
        assert schema.telefone == "11999999999"

    def test_update_schema_com_nome_vazio_falha(self):
        """Testa que nome vazio no update falha"""
        # Act & Assert
        with pytest.raises(ValidationError):
            ReclamanteUpdate(nome="", documento="123", telefone="11999999999")

    def test_update_schema_com_telefone_vazio_falha(self):
        """Testa que telefone vazio no update falha"""
        # Act & Assert
        with pytest.raises(ValidationError):
            ReclamanteUpdate(nome="João", documento="123", telefone="")

    def test_update_schema_sem_documento_falha(self):
        """Testa que update exige documento"""
        # Act & Assert
        with pytest.raises(ValidationError):
            ReclamanteUpdate(nome="João", telefone="11999999999")


class TestReclamanteResponseSchema:
    """Testes para o schema ReclamanteResponse"""

    def test_response_schema_com_todos_campos(self):
        """Testa schema de resposta com todos os campos"""
        # Arrange & Act
        schema = ReclamanteResponse(
            id=1,
            nome="João Silva",
            documento="123.456.789-00",
            telefone="11999999999",
        )

        # Assert
        assert schema.id == 1
        assert schema.nome == "João Silva"
        assert schema.documento == "123.456.789-00"
        assert schema.telefone == "11999999999"

    def test_response_schema_sem_id_falha(self):
        """Testa que id é obrigatório no response"""
        # Act & Assert
        with pytest.raises(ValidationError):
            ReclamanteResponse(
                nome="João Silva",
                documento="123",
                telefone="11999999999",
            )

    def test_response_schema_serializa_para_json(self):
        """Testa serialização do response para JSON"""
        # Arrange
        schema = ReclamanteResponse(
            id=7,
            nome="Maria",
            documento="DOC-7",
            telefone="11970000000",
        )

        # Act
        json_data = schema.model_dump_json()

        # Assert
        assert '"id":7' in json_data
        assert "Maria" in json_data


class TestReclamanteListResponseSchema:
    """Testes para o schema ReclamanteListResponse"""

    def test_list_response_schema_vazio(self):
        """Testa resposta de lista vazia"""
        # Arrange & Act
        schema = ReclamanteListResponse(reclamantes=[], total=0, skip=0, limit=10)

        # Assert
        assert schema.reclamantes == []
        assert schema.total == 0

    def test_list_response_schema_com_reclamantes(self):
        """Testa resposta de lista com reclamantes"""
        # Arrange
        reclamantes = [
            ReclamanteResponse(id=1, nome="A", documento="D1", telefone="111"),
            ReclamanteResponse(id=2, nome="B", documento="D2", telefone="222"),
        ]

        # Act
        schema = ReclamanteListResponse(
            reclamantes=reclamantes,
            total=2,
            skip=0,
            limit=10,
        )

        # Assert
        assert len(schema.reclamantes) == 2
        assert schema.reclamantes[0].nome == "A"
        assert schema.total == 2

    def test_list_response_schema_paginacao(self):
        """Testa campos de paginação"""
        # Arrange & Act
        schema = ReclamanteListResponse(
            reclamantes=[],
            total=35,
            skip=20,
            limit=10,
        )

        # Assert
        assert schema.total == 35
        assert schema.skip == 20
        assert schema.limit == 10
