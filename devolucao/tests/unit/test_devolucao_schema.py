"""
Testes unitários para os schemas Pydantic de Devolucao
"""
import pytest
from datetime import datetime, timedelta
from pydantic import ValidationError
from devolucao.src.application.schemas.devolucao_schema import (
    DevolucaoCreate,
    DevolucaoUpdate,
    DevolucaoPatch,
    DevolucaoResponse,
    DevolucaoListResponse,
)


class TestDevolucaoCreateSchema:
    """Testes para o schema DevolucaoCreate"""

    def test_criar_schema_com_dados_validos(self):
        """Testa criação de schema com dados válidos"""
        # Arrange & Act
        schema = DevolucaoCreate(
            reclamante_id=1,
            item_id=2,
            observacao="Item devolvido ao dono"
        )

        # Assert
        assert schema.reclamante_id == 1
        assert schema.item_id == 2
        assert schema.observacao == "Item devolvido ao dono"

    def test_schema_com_reclamante_id_zero_falha(self):
        """Testa que reclamante_id zero não é aceito"""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            DevolucaoCreate(
                reclamante_id=0,
                item_id=1,
                observacao="Observação válida"
            )
        assert "reclamante_id" in str(exc_info.value).lower()

    def test_schema_com_reclamante_id_negativo_falha(self):
        """Testa que reclamante_id negativo não é aceito"""
        # Act & Assert
        with pytest.raises(ValidationError):
            DevolucaoCreate(
                reclamante_id=-1,
                item_id=1,
                observacao="Observação válida"
            )

    def test_schema_com_item_id_zero_falha(self):
        """Testa que item_id zero não é aceito"""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            DevolucaoCreate(
                reclamante_id=1,
                item_id=0,
                observacao="Observação válida"
            )
        assert "item_id" in str(exc_info.value).lower()

    def test_schema_com_item_id_negativo_falha(self):
        """Testa que item_id negativo não é aceito"""
        # Act & Assert
        with pytest.raises(ValidationError):
            DevolucaoCreate(
                reclamante_id=1,
                item_id=-5,
                observacao="Observação válida"
            )

    def test_schema_com_observacao_vazia_falha(self):
        """Testa que observação vazia não é aceita"""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            DevolucaoCreate(
                reclamante_id=1,
                item_id=1,
                observacao=""
            )
        assert "observacao" in str(exc_info.value).lower()

    def test_schema_com_campo_faltando_falha(self):
        """Testa que campo obrigatório faltando causa erro"""
        # Arrange - faltando item_id
        with pytest.raises(ValidationError) as exc_info:
            DevolucaoCreate(
                reclamante_id=1,
                observacao="Observação válida"
            )
        assert "item_id" in str(exc_info.value).lower()

    def test_schema_data_devolucao_default(self):
        """Testa que data_devolucao tem valor padrão quando não informada"""
        # Arrange & Act
        schema = DevolucaoCreate(
            reclamante_id=1,
            item_id=1,
            observacao="Observação válida"
        )

        # Assert
        assert schema.data_devolucao is not None
        assert isinstance(schema.data_devolucao, datetime)

    def test_schema_serializa_para_dict(self):
        """Testa serialização para dicionário"""
        # Arrange
        schema = DevolucaoCreate(
            reclamante_id=1,
            item_id=2,
            observacao="Devolvido na portaria"
        )

        # Act
        data = schema.model_dump()

        # Assert
        assert data["reclamante_id"] == 1
        assert data["item_id"] == 2
        assert data["observacao"] == "Devolvido na portaria"

    def test_schema_serializa_para_json(self):
        """Testa serialização para JSON"""
        # Arrange
        schema = DevolucaoCreate(
            reclamante_id=3,
            item_id=5,
            observacao="Item encontrado e devolvido"
        )

        # Act
        json_str = schema.model_dump_json()

        # Assert
        assert "reclamante_id" in json_str
        assert "observacao" in json_str


class TestDevolucaoUpdateSchema:
    """Testes para o schema DevolucaoUpdate"""

    def test_update_schema_com_dados_validos(self):
        """Testa schema de update com dados válidos"""
        # Arrange & Act
        schema = DevolucaoUpdate(
            reclamante_id=2,
            item_id=3,
            observacao="Observação atualizada"
        )

        # Assert
        assert schema.reclamante_id == 2
        assert schema.item_id == 3
        assert schema.observacao == "Observação atualizada"

    def test_update_schema_com_reclamante_id_invalido_falha(self):
        """Testa que reclamante_id inválido no update falha"""
        # Act & Assert
        with pytest.raises(ValidationError):
            DevolucaoUpdate(
                reclamante_id=0,
                item_id=1,
                observacao="Observação"
            )


class TestDevolucaoPatchSchema:
    """Testes para o schema DevolucaoPatch"""

    def test_patch_schema_com_apenas_observacao(self):
        """Testa patch parcial apenas com observação"""
        # Arrange & Act
        schema = DevolucaoPatch(observacao="Nova observação")

        # Assert
        assert schema.observacao == "Nova observação"
        assert schema.reclamante_id is None
        assert schema.item_id is None

    def test_patch_schema_com_apenas_reclamante_id(self):
        """Testa patch parcial apenas com reclamante_id"""
        # Arrange & Act
        schema = DevolucaoPatch(reclamante_id=5)

        # Assert
        assert schema.reclamante_id == 5
        assert schema.observacao is None
        assert schema.item_id is None

    def test_patch_schema_com_todos_campos(self):
        """Testa patch com todos os campos"""
        # Arrange
        now = datetime.now()

        # Act
        schema = DevolucaoPatch(
            reclamante_id=1,
            item_id=2,
            observacao="Completo",
            data_devolucao=now
        )

        # Assert
        assert schema.reclamante_id == 1
        assert schema.item_id == 2
        assert schema.observacao == "Completo"
        assert schema.data_devolucao == now

    def test_patch_schema_vazio(self):
        """Testa patch sem campos — todos None"""
        # Arrange & Act
        schema = DevolucaoPatch()

        # Assert
        assert schema.reclamante_id is None
        assert schema.item_id is None
        assert schema.observacao is None
        assert schema.data_devolucao is None

    def test_patch_schema_com_reclamante_id_invalido_falha(self):
        """Testa que reclamante_id inválido no patch falha"""
        # Act & Assert
        with pytest.raises(ValidationError):
            DevolucaoPatch(reclamante_id=0)


class TestDevolucaoResponseSchema:
    """Testes para o schema DevolucaoResponse"""

    def test_response_schema_com_todos_campos(self):
        """Testa schema de resposta com todos os campos"""
        # Arrange & Act
        now = datetime.now()
        schema = DevolucaoResponse(
            id=1,
            reclamante_id=2,
            item_id=3,
            observacao="Item devolvido",
            data_devolucao=now,
            created_at=now
        )

        # Assert
        assert schema.id == 1
        assert schema.reclamante_id == 2
        assert schema.item_id == 3
        assert schema.observacao == "Item devolvido"
        assert schema.created_at == now
        assert schema.updated_at is None

    def test_response_schema_sem_id_falha(self):
        """Testa que id é obrigatório no response schema"""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            DevolucaoResponse(
                reclamante_id=1,
                item_id=1,
                observacao="Observação",
                data_devolucao=datetime.now(),
                created_at=datetime.now()
            )
        assert "id" in str(exc_info.value).lower()

    def test_response_schema_serializa_para_json(self):
        """Testa serialização do response para JSON"""
        # Arrange
        now = datetime.now()
        schema = DevolucaoResponse(
            id=1,
            reclamante_id=2,
            item_id=3,
            observacao="Devolvido",
            data_devolucao=now,
            created_at=now
        )

        # Act
        json_str = schema.model_dump_json()

        # Assert
        assert "reclamante_id" in json_str
        assert "observacao" in json_str


class TestDevolucaoListResponseSchema:
    """Testes para o schema DevolucaoListResponse"""

    def test_list_response_schema_vazio(self):
        """Testa schema de listagem com lista vazia"""
        # Arrange & Act
        schema = DevolucaoListResponse(
            devolucoes=[],
            total=0,
            skip=0,
            limit=100
        )

        # Assert
        assert schema.devolucoes == []
        assert schema.total == 0
        assert schema.skip == 0
        assert schema.limit == 100

    def test_list_response_schema_com_devolucoes(self):
        """Testa schema de listagem com dados"""
        # Arrange
        now = datetime.now()
        devolucoes = [
            DevolucaoResponse(id=1, reclamante_id=1, item_id=1, observacao="D1", data_devolucao=now, created_at=now),
            DevolucaoResponse(id=2, reclamante_id=2, item_id=2, observacao="D2", data_devolucao=now, created_at=now),
        ]

        # Act
        schema = DevolucaoListResponse(
            devolucoes=devolucoes,
            total=2,
            skip=0,
            limit=100
        )

        # Assert
        assert len(schema.devolucoes) == 2
        assert schema.total == 2

    def test_list_response_schema_paginacao(self):
        """Testa schema de listagem com paginação customizada"""
        # Arrange & Act
        schema = DevolucaoListResponse(
            devolucoes=[],
            total=50,
            skip=10,
            limit=10
        )

        # Assert
        assert schema.skip == 10
        assert schema.limit == 10
        assert schema.total == 50
