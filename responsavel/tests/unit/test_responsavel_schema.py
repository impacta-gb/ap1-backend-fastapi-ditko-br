"""
Testes unitários para os schemas Pydantic de Responsavel
Testa validações, serialização e deserialização
"""
import pytest
from pydantic import ValidationError
from responsavel.src.application.schemas.responsavel_schema import (
    ResponsavelCreate,
    ResponsavelUpdate,
    ResponsavelPatch,
    ResponsavelResponse,
    ResponsavelListResponse,
    ResponsavelStatusUpdate
)


class TestResponsavelCreateSchema:
    """Testes para o schema ResponsavelCreate"""

    def test_criar_schema_com_dados_validos(self):
        """Testa criação de schema com dados válidos"""
        # Arrange & Act
        data = {
            "nome": "João Silva",
            "cargo": "Segurança",
            "telefone": "11999999999"
        }

        schema = ResponsavelCreate(**data)

        # Assert
        assert schema.nome == "João Silva"
        assert schema.cargo == "Segurança"
        assert schema.telefone == "11999999999"

    def test_schema_com_nome_vazio_falha(self):
        """Testa que nome vazio não é aceito"""
        # Arrange
        data = {
            "nome": "",
            "cargo": "Segurança",
            "telefone": "11999999999"
        }

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ResponsavelCreate(**data)

        assert "nome" in str(exc_info.value).lower()

    def test_schema_com_cargo_vazio_falha(self):
        """Testa que cargo vazio não é aceito"""
        # Arrange
        data = {
            "nome": "João Silva",
            "cargo": "",
            "telefone": "11999999999"
        }

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ResponsavelCreate(**data)

        assert "cargo" in str(exc_info.value).lower()

    def test_schema_com_telefone_vazio_falha(self):
        """Testa que telefone vazio não é aceito"""
        # Arrange
        data = {
            "nome": "João Silva",
            "cargo": "Segurança",
            "telefone": ""
        }

        # Act & Assert
        with pytest.raises(ValidationError):
            ResponsavelCreate(**data)

    def test_schema_com_campo_faltando_falha(self):
        """Testa que campo obrigatório faltando causa erro"""
        # Arrange - faltando cargo
        data = {
            "nome": "João Silva",
            "telefone": "11999999999"
        }

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ResponsavelCreate(**data)

        assert "cargo" in str(exc_info.value).lower()

    def test_schema_com_telefone_invalido_falha(self):
        """Testa que telefone com formato inválido não é aceito"""
        # Arrange
        data = {
            "nome": "João Silva",
            "cargo": "Segurança",
            "telefone": "12345"  # Menos de 10 dígitos
        }

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ResponsavelCreate(**data)

        assert "telefone" in str(exc_info.value).lower()

    def test_schema_com_telefone_com_letras_falha(self):
        """Testa que telefone com letras não é aceito"""
        # Arrange
        data = {
            "nome": "João Silva",
            "cargo": "Segurança",
            "telefone": "1199ABCDEFG"
        }

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ResponsavelCreate(**data)

        assert "telefone" in str(exc_info.value).lower()

    def test_schema_sem_campo_ativo(self):
        """Testa que o schema de criação não tem campo ativo (regra de negócio)"""
        # Arrange & Act
        data = {
            "nome": "João Silva",
            "cargo": "Segurança",
            "telefone": "11999999999"
        }

        schema = ResponsavelCreate(**data)

        # Assert - ativo não deve existir no schema de criação
        assert not hasattr(schema, "ativo")

    def test_schema_serializa_para_dict(self):
        """Testa que schema pode ser serializado para dict"""
        # Arrange
        data = {
            "nome": "João Silva",
            "cargo": "Segurança",
            "telefone": "11999999999"
        }

        schema = ResponsavelCreate(**data)

        # Act
        result = schema.model_dump()

        # Assert
        assert isinstance(result, dict)
        assert result["nome"] == "João Silva"

    def test_schema_serializa_para_json(self):
        """Testa que schema pode ser serializado para JSON"""
        # Arrange
        data = {
            "nome": "João Silva",
            "cargo": "Segurança",
            "telefone": "11999999999"
        }

        schema = ResponsavelCreate(**data)

        # Act
        result = schema.model_dump_json()

        # Assert
        assert isinstance(result, str)
        assert "João Silva" in result

    def test_schema_com_nome_longo_demais_falha(self):
        """Testa que nome muito longo não é aceito"""
        # Arrange
        data = {
            "nome": "A" * 300,  # 300 caracteres
            "cargo": "Segurança",
            "telefone": "11999999999"
        }

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ResponsavelCreate(**data)

        assert "nome" in str(exc_info.value).lower()


class TestResponsavelUpdateSchema:
    """Testes para o schema ResponsavelUpdate"""

    def test_update_schema_com_dados_validos(self):
        """Testa schema de update com dados válidos"""
        # Arrange & Act
        data = {
            "nome": "João Santos",
            "cargo": "Supervisor de Segurança",
            "telefone": "11988888888"
        }

        schema = ResponsavelUpdate(**data)

        # Assert
        assert schema.nome == "João Santos"
        assert schema.cargo == "Supervisor de Segurança"
        assert schema.telefone == "11988888888"

    def test_update_schema_sem_campo_ativo(self):
        """Testa que o schema de update não tem campo ativo"""
        # Arrange & Act
        data = {
            "nome": "João Santos",
            "cargo": "Supervisor",
            "telefone": "11988888888"
        }

        schema = ResponsavelUpdate(**data)

        # Assert - ativo não deve existir no schema de update
        assert not hasattr(schema, "ativo")

    def test_update_schema_com_telefone_invalido_falha(self):
        """Testa que telefone inválido no update não é aceito"""
        # Arrange
        data = {
            "nome": "João Santos",
            "cargo": "Supervisor",
            "telefone": "123"  # Inválido
        }

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ResponsavelUpdate(**data)

        assert "telefone" in str(exc_info.value).lower()


class TestResponsavelPatchSchema:
    """Testes para o schema ResponsavelPatch"""

    def test_patch_schema_com_apenas_nome(self):
        """Testa schema de patch com apenas nome"""
        # Arrange & Act
        schema = ResponsavelPatch(nome="Novo Nome")

        # Assert
        assert schema.nome == "Novo Nome"
        assert schema.cargo is None
        assert schema.telefone is None

    def test_patch_schema_com_apenas_cargo(self):
        """Testa schema de patch com apenas cargo"""
        # Arrange & Act
        schema = ResponsavelPatch(cargo="Novo Cargo")

        # Assert
        assert schema.cargo == "Novo Cargo"
        assert schema.nome is None
        assert schema.telefone is None

    def test_patch_schema_com_todos_campos(self):
        """Testa schema de patch com todos os campos opcionais"""
        # Arrange & Act
        schema = ResponsavelPatch(
            nome="Nome Novo",
            cargo="Cargo Novo",
            telefone="11977777777"
        )

        # Assert
        assert schema.nome == "Nome Novo"
        assert schema.cargo == "Cargo Novo"
        assert schema.telefone == "11977777777"

    def test_patch_schema_vazio(self):
        """Testa schema de patch sem campos (todos opcionais)"""
        # Arrange & Act
        schema = ResponsavelPatch()

        # Assert
        assert schema.nome is None
        assert schema.cargo is None
        assert schema.telefone is None

    def test_patch_schema_com_telefone_invalido_falha(self):
        """Testa que telefone inválido no patch não é aceito"""
        # Arrange & Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ResponsavelPatch(telefone="123")

        assert "telefone" in str(exc_info.value).lower()


class TestResponsavelResponseSchema:
    """Testes para o schema ResponsavelResponse"""

    def test_response_schema_com_todos_campos(self):
        """Testa schema de resposta com todos os campos"""
        # Arrange & Act
        data = {
            "id": 1,
            "nome": "João Silva",
            "cargo": "Segurança",
            "telefone": "11999999999",
            "ativo": True
        }

        schema = ResponsavelResponse(**data)

        # Assert
        assert schema.id == 1
        assert schema.nome == "João Silva"
        assert schema.ativo is True

    def test_response_schema_sem_id_falha(self):
        """Testa que ID é obrigatório no response"""
        # Arrange
        data = {
            "nome": "João Silva",
            "cargo": "Segurança",
            "telefone": "11999999999",
            "ativo": True
        }

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ResponsavelResponse(**data)

        assert "id" in str(exc_info.value).lower()

    def test_response_schema_serializa_para_json(self):
        """Testa serialização para JSON"""
        # Arrange
        data = {
            "id": 1,
            "nome": "João Silva",
            "cargo": "Segurança",
            "telefone": "11999999999",
            "ativo": True
        }

        schema = ResponsavelResponse(**data)

        # Act
        result = schema.model_dump_json()

        # Assert
        assert isinstance(result, str)
        assert '"id":1' in result.replace(" ", "")
        assert "João Silva" in result


class TestResponsavelListResponseSchema:
    """Testes para o schema ResponsavelListResponse"""

    def test_list_response_schema_vazio(self):
        """Testa schema de lista vazia"""
        # Arrange & Act
        data = {
            "responsaveis": [],
            "total": 0,
            "skip": 0,
            "limit": 100
        }

        schema = ResponsavelListResponse(**data)

        # Assert
        assert len(schema.responsaveis) == 0
        assert schema.total == 0

    def test_list_response_schema_com_responsaveis(self):
        """Testa schema de lista com responsáveis"""
        # Arrange
        responsavel_data = {
            "id": 1,
            "nome": "João Silva",
            "cargo": "Segurança",
            "telefone": "11999999999",
            "ativo": True
        }

        data = {
            "responsaveis": [responsavel_data, responsavel_data],
            "total": 2,
            "skip": 0,
            "limit": 100
        }

        # Act
        schema = ResponsavelListResponse(**data)

        # Assert
        assert len(schema.responsaveis) == 2
        assert schema.total == 2
        assert all(isinstance(r, ResponsavelResponse) for r in schema.responsaveis)

    def test_list_response_schema_paginacao(self):
        """Testa schema com informações de paginação"""
        # Arrange
        data = {
            "responsaveis": [],
            "total": 50,
            "skip": 10,
            "limit": 20
        }

        # Act
        schema = ResponsavelListResponse(**data)

        # Assert
        assert schema.skip == 10
        assert schema.limit == 20
        assert schema.total == 50


class TestResponsavelStatusUpdateSchema:
    """Testes para o schema ResponsavelStatusUpdate"""

    def test_status_update_com_ativo_true(self):
        """Testa schema de status update com ativo=True"""
        # Arrange & Act
        schema = ResponsavelStatusUpdate(ativo=True)

        # Assert
        assert schema.ativo is True

    def test_status_update_com_ativo_false(self):
        """Testa schema de status update com ativo=False"""
        # Arrange & Act
        schema = ResponsavelStatusUpdate(ativo=False)

        # Assert
        assert schema.ativo is False

    def test_status_update_sem_ativo_falha(self):
        """Testa que campo ativo é obrigatório"""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ResponsavelStatusUpdate()  # type: ignore

        assert "ativo" in str(exc_info.value).lower()
