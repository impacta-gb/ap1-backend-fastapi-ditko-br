"""
Testes unitários para os casos de uso de Devolucao
"""
import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock
from devolucao.src.application.use_cases.devolucao_use_cases import (
    CreateDevolucaoUseCase,
    GetDevolucaoByIdUseCase,
    GetAllDevolucoesUseCase,
    UpdateDevolucaoUseCase,
    DeleteDevolucaoUseCase,
    GetDevolucoesByDataUseCase,
    CountDevolucoesUseCase,
)
from devolucao.src.domain.entities.devolucao import Devolucao


def criar_devolucao_valida(**kwargs) -> Devolucao:
    """Helper para criar uma devolução válida para testes"""
    dados = {
        "reclamante_id": 1,
        "item_id": 2,
        "observacao": "Item devolvido ao dono",
        "data_devolucao": datetime.now() - timedelta(hours=1),
    }
    dados.update(kwargs)
    return Devolucao(**dados)


class TestCreateDevolucaoUseCase:
    """Testes para CreateDevolucaoUseCase"""

    @pytest.fixture
    def mock_repository(self):
        return AsyncMock()

    @pytest.fixture
    def use_case(self, mock_repository):
        return CreateDevolucaoUseCase(mock_repository)

    @pytest.mark.asyncio
    async def test_criar_devolucao_com_sucesso(self, use_case, mock_repository):
        """Testa criação de devolução com dados válidos"""
        # Arrange
        devolucao = criar_devolucao_valida()
        devolucao_salva = criar_devolucao_valida()
        devolucao_salva.id = 1
        mock_repository.exists_item.return_value = True
        mock_repository.exists_devolucao_for_item.return_value = False
        mock_repository.exists_item_not_devolvido.return_value = True
        mock_repository.exists_reclamante.return_value = True
        mock_repository.create.return_value = devolucao_salva

        # Act
        resultado = await use_case.execute(devolucao)

        # Assert
        assert resultado.id == 1
        mock_repository.create.assert_called_once_with(devolucao)

    @pytest.mark.asyncio
    async def test_criar_devolucao_duplicada_para_mesmo_item_falha(self, use_case, mock_repository):
        """Impede registrar mais de uma devolução para o mesmo item."""
        devolucao = criar_devolucao_valida(item_id=10)
        mock_repository.exists_item.return_value = True
        mock_repository.exists_devolucao_for_item.return_value = True

        with pytest.raises(ValueError, match="já possui devolução registrada"):
            await use_case.execute(devolucao)

        mock_repository.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_criar_devolucao_com_data_timezone_aware_sucesso(self, use_case, mock_repository):
        """Garante suporte a payload com timezone (ex.: sufixo Z)."""
        devolucao = criar_devolucao_valida(
            data_devolucao=datetime.now(timezone.utc) - timedelta(minutes=5)
        )
        devolucao_salva = criar_devolucao_valida()
        devolucao_salva.id = 1

        mock_repository.exists_item.return_value = True
        mock_repository.exists_devolucao_for_item.return_value = False
        mock_repository.exists_item_not_devolvido.return_value = True
        mock_repository.exists_reclamante.return_value = True
        mock_repository.create.return_value = devolucao_salva

        resultado = await use_case.execute(devolucao)

        assert resultado.id == 1
        mock_repository.create.assert_called_once_with(devolucao)

    @pytest.mark.asyncio
    async def test_criar_devolucao_com_data_futura_falha(self, use_case, mock_repository):
        """Testa que data futura gera erro"""
        # Arrange
        devolucao = criar_devolucao_valida(data_devolucao=datetime.now() + timedelta(days=1))

        # Act & Assert
        with pytest.raises(ValueError, match="Data da devolução não pode ser no futuro"):
            await use_case.execute(devolucao)
        mock_repository.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_criar_devolucao_com_reclamante_id_invalido_falha(self, use_case, mock_repository):
        """Testa que reclamante_id inválido gera erro no use case"""
        # Arrange — o domínio valida isso, mas o use case também valida
        # Usamos um mock de Devolucao com atributos inválidos para testar use case isolado
        devolucao = MagicMock()
        devolucao.data_devolucao = datetime.now() - timedelta(hours=1)
        devolucao.reclamante_id = 0
        devolucao.item_id = 1

        # Act & Assert
        with pytest.raises(ValueError, match="ID do reclamante deve ser maior que zero"):
            await use_case.execute(devolucao)
        mock_repository.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_criar_devolucao_com_item_id_invalido_falha(self, use_case, mock_repository):
        """Testa que item_id inválido gera erro no use case"""
        # Arrange
        devolucao = MagicMock()
        devolucao.data_devolucao = datetime.now() - timedelta(hours=1)
        devolucao.reclamante_id = 1
        devolucao.item_id = -1

        # Act & Assert
        with pytest.raises(ValueError, match="ID do item deve ser maior que zero"):
            await use_case.execute(devolucao)
        mock_repository.create.assert_not_called()


class TestGetDevolucaoByIdUseCase:
    """Testes para GetDevolucaoByIdUseCase"""

    @pytest.fixture
    def mock_repository(self):
        return AsyncMock()

    @pytest.fixture
    def use_case(self, mock_repository):
        return GetDevolucaoByIdUseCase(mock_repository)

    @pytest.mark.asyncio
    async def test_buscar_por_id_existente(self, use_case, mock_repository):
        """Testa busca de devolução por ID existente"""
        # Arrange
        devolucao = criar_devolucao_valida()
        devolucao.id = 1
        mock_repository.get_by_id.return_value = devolucao

        # Act
        resultado = await use_case.execute(1)

        # Assert
        assert resultado == devolucao
        mock_repository.get_by_id.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_buscar_por_id_inexistente(self, use_case, mock_repository):
        """Testa busca de devolução por ID inexistente"""
        # Arrange
        mock_repository.get_by_id.return_value = None

        # Act
        resultado = await use_case.execute(999)

        # Assert
        assert resultado is None

    @pytest.mark.asyncio
    async def test_buscar_por_id_invalido_falha(self, use_case, mock_repository):
        """Testa que ID inválido gera erro"""
        # Act & Assert
        with pytest.raises(ValueError, match="ID da devolução deve ser maior que zero"):
            await use_case.execute(0)
        mock_repository.get_by_id.assert_not_called()

    @pytest.mark.asyncio
    async def test_buscar_por_id_negativo_falha(self, use_case, mock_repository):
        """Testa que ID negativo gera erro"""
        # Act & Assert
        with pytest.raises(ValueError, match="ID da devolução deve ser maior que zero"):
            await use_case.execute(-1)
        mock_repository.get_by_id.assert_not_called()


class TestGetAllDevolucoesUseCase:
    """Testes para GetAllDevolucoesUseCase"""

    @pytest.fixture
    def mock_repository(self):
        return AsyncMock()

    @pytest.fixture
    def use_case(self, mock_repository):
        return GetAllDevolucoesUseCase(mock_repository)

    @pytest.mark.asyncio
    async def test_listar_com_paginacao_padrao(self, use_case, mock_repository):
        """Testa listagem com paginação padrão"""
        # Arrange
        devolucoes = [criar_devolucao_valida(), criar_devolucao_valida()]
        mock_repository.get_all.return_value = devolucoes

        # Act
        resultado = await use_case.execute()

        # Assert
        assert len(resultado) == 2
        mock_repository.get_all.assert_called_once_with(0, 100)

    @pytest.mark.asyncio
    async def test_listar_com_skip_negativo_falha(self, use_case, mock_repository):
        """Testa que skip negativo gera erro"""
        # Act & Assert
        with pytest.raises(ValueError, match="Skip não pode ser negativo"):
            await use_case.execute(skip=-1)
        mock_repository.get_all.assert_not_called()

    @pytest.mark.asyncio
    async def test_listar_com_limit_zero_falha(self, use_case, mock_repository):
        """Testa que limit zero gera erro"""
        # Act & Assert
        with pytest.raises(ValueError, match="Limit deve estar entre 1 e 1000"):
            await use_case.execute(limit=0)
        mock_repository.get_all.assert_not_called()

    @pytest.mark.asyncio
    async def test_listar_com_limit_acima_do_maximo_falha(self, use_case, mock_repository):
        """Testa que limit acima de 1000 gera erro"""
        # Act & Assert
        with pytest.raises(ValueError, match="Limit deve estar entre 1 e 1000"):
            await use_case.execute(limit=1001)
        mock_repository.get_all.assert_not_called()

    @pytest.mark.asyncio
    async def test_listar_com_paginacao_customizada(self, use_case, mock_repository):
        """Testa listagem com paginação customizada válida"""
        # Arrange
        mock_repository.get_all.return_value = []

        # Act
        await use_case.execute(skip=10, limit=20)

        # Assert
        mock_repository.get_all.assert_called_once_with(10, 20)

    @pytest.mark.asyncio
    async def test_listar_com_limit_maximo_permitido(self, use_case, mock_repository):
        """Testa listagem com limit exatamente no máximo (1000)"""
        # Arrange
        mock_repository.get_all.return_value = []

        # Act
        await use_case.execute(limit=1000)

        # Assert
        mock_repository.get_all.assert_called_once_with(0, 1000)


class TestUpdateDevolucaoUseCase:
    """Testes para UpdateDevolucaoUseCase"""

    @pytest.fixture
    def mock_repository(self):
        return AsyncMock()

    @pytest.fixture
    def use_case(self, mock_repository):
        return UpdateDevolucaoUseCase(mock_repository)

    @pytest.mark.asyncio
    async def test_atualizar_devolucao_existente(self, use_case, mock_repository):
        """Testa atualização de devolução existente"""
        # Arrange
        existente = criar_devolucao_valida()
        existente.id = 1
        atualizada = criar_devolucao_valida(observacao="Observação atualizada")
        atualizada.id = 1

        mock_repository.get_by_id.return_value = existente
        mock_repository.update.return_value = atualizada

        nova_devolucao = criar_devolucao_valida(observacao="Observação atualizada")

        # Act
        resultado = await use_case.execute(1, nova_devolucao)

        # Assert
        assert resultado.observacao == "Observação atualizada"
        mock_repository.update.assert_called_once_with(1, nova_devolucao)

    @pytest.mark.asyncio
    async def test_atualizar_devolucao_inexistente_retorna_none(self, use_case, mock_repository):
        """Testa que atualização de devolução inexistente retorna None"""
        # Arrange
        mock_repository.get_by_id.return_value = None
        devolucao = criar_devolucao_valida()

        # Act
        resultado = await use_case.execute(999, devolucao)

        # Assert
        assert resultado is None
        mock_repository.update.assert_not_called()

    @pytest.mark.asyncio
    async def test_atualizar_com_data_futura_falha(self, use_case, mock_repository):
        """Testa que atualização com data futura gera erro"""
        # Arrange
        existente = criar_devolucao_valida()
        mock_repository.get_by_id.return_value = existente
        devolucao_futura = criar_devolucao_valida(data_devolucao=datetime.now() + timedelta(days=1))

        # Act & Assert
        with pytest.raises(ValueError, match="Data da devolução não pode ser no futuro"):
            await use_case.execute(1, devolucao_futura)
        mock_repository.update.assert_not_called()


class TestDeleteDevolucaoUseCase:
    """Testes para DeleteDevolucaoUseCase"""

    @pytest.fixture
    def mock_repository(self):
        return AsyncMock()

    @pytest.fixture
    def use_case(self, mock_repository):
        return DeleteDevolucaoUseCase(mock_repository)

    @pytest.mark.asyncio
    async def test_deletar_devolucao_existente(self, use_case, mock_repository):
        """Testa deleção de devolução existente"""
        # Arrange
        devolucao = criar_devolucao_valida()
        mock_repository.get_by_id.return_value = devolucao
        mock_repository.delete.return_value = True

        # Act
        resultado = await use_case.execute(1)

        # Assert
        assert resultado is True
        mock_repository.delete.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_deletar_devolucao_inexistente_retorna_false(self, use_case, mock_repository):
        """Testa que deleção de devolução inexistente retorna False"""
        # Arrange
        mock_repository.get_by_id.return_value = None

        # Act
        resultado = await use_case.execute(999)

        # Assert
        assert resultado is False
        mock_repository.delete.assert_not_called()

    @pytest.mark.asyncio
    async def test_deletar_com_id_invalido_falha(self, use_case, mock_repository):
        """Testa que ID inválido gera erro"""
        # Act & Assert
        with pytest.raises(ValueError, match="ID da devolução deve ser maior que zero"):
            await use_case.execute(0)
        mock_repository.get_by_id.assert_not_called()

    @pytest.mark.asyncio
    async def test_deletar_com_id_negativo_falha(self, use_case, mock_repository):
        """Testa que ID negativo gera erro"""
        # Act & Assert
        with pytest.raises(ValueError, match="ID da devolução deve ser maior que zero"):
            await use_case.execute(-5)
        mock_repository.get_by_id.assert_not_called()


class TestGetDevolucoesByDataUseCase:
    """Testes para GetDevolucoesByDataUseCase"""

    @pytest.fixture
    def mock_repository(self):
        return AsyncMock()

    @pytest.fixture
    def use_case(self, mock_repository):
        return GetDevolucoesByDataUseCase(mock_repository)

    @pytest.mark.asyncio
    async def test_buscar_por_data_com_sucesso(self, use_case, mock_repository):
        """Testa busca de devoluções por data"""
        # Arrange
        data = datetime(2024, 1, 15)
        devolucoes = [criar_devolucao_valida(data_devolucao=data)]
        mock_repository.get_by_data.return_value = devolucoes

        # Act
        resultado = await use_case.execute(data)

        # Assert
        assert len(resultado) == 1
        mock_repository.get_by_data.assert_called_once_with(data)

    @pytest.mark.asyncio
    async def test_buscar_por_data_nula_falha(self, use_case, mock_repository):
        """Testa que data nula gera erro"""
        # Act & Assert
        with pytest.raises(ValueError, match="Data não pode ser nula"):
            await use_case.execute(None)
        mock_repository.get_by_data.assert_not_called()

    @pytest.mark.asyncio
    async def test_buscar_por_data_sem_resultados(self, use_case, mock_repository):
        """Testa busca por data sem resultados"""
        # Arrange
        data = datetime(2020, 1, 1)
        mock_repository.get_by_data.return_value = []

        # Act
        resultado = await use_case.execute(data)

        # Assert
        assert resultado == []


class TestCountDevolucoesUseCase:
    """Testes para CountDevolucoesUseCase"""

    @pytest.fixture
    def mock_repository(self):
        return AsyncMock()

    @pytest.fixture
    def use_case(self, mock_repository):
        return CountDevolucoesUseCase(mock_repository)

    @pytest.mark.asyncio
    async def test_contar_total_com_registros(self, use_case, mock_repository):
        """Testa contagem total de devoluções"""
        # Arrange
        mock_repository.count.return_value = 42

        # Act
        resultado = await use_case.execute()

        # Assert
        assert resultado == 42
        mock_repository.count.assert_called_once()

    @pytest.mark.asyncio
    async def test_contar_total_sem_registros(self, use_case, mock_repository):
        """Testa contagem quando não há devoluções"""
        # Arrange
        mock_repository.count.return_value = 0

        # Act
        resultado = await use_case.execute()

        # Assert
        assert resultado == 0
