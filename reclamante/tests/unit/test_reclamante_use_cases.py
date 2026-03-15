"""
Testes unitários para os casos de uso de Reclamante
"""
import pytest
from unittest.mock import AsyncMock
from reclamante.src.domain.entities.reclamante import Reclamante
from reclamante.src.application.use_cases.reclamante_use_cases import (
    CreateReclamanteUseCase,
    GetReclamanteByIdUseCase,
    GetAllReclamantesUseCase,
    UpdateReclamanteUseCase,
    DeleteReclamanteUseCase,
)


def make_reclamante(id=None, nome="João", documento="123", telefone="11999999999"):
    """Factory helper para criar entidades Reclamante"""
    return Reclamante(id=id, nome=nome, documento=documento, telefone=telefone)


class TestCreateReclamanteUseCase:
    """Testes para o caso de uso de criação"""

    @pytest.mark.asyncio
    async def test_criar_reclamante_com_sucesso(self):
        """Testa criação com dados válidos"""
        # Arrange
        repository = AsyncMock()
        reclamante = make_reclamante()
        repository.create.return_value = make_reclamante(id=1)
        use_case = CreateReclamanteUseCase(repository)

        # Act
        result = await use_case.execute(reclamante)

        # Assert
        assert result.id == 1
        repository.create.assert_called_once_with(reclamante)

    @pytest.mark.asyncio
    async def test_criar_reclamante_delega_para_repositorio(self):
        """Testa que o caso de uso delega para o repositório"""
        # Arrange
        repository = AsyncMock()
        repository.create.return_value = make_reclamante(id=2)
        use_case = CreateReclamanteUseCase(repository)

        # Act
        await use_case.execute(make_reclamante())

        # Assert
        repository.create.assert_called_once()


class TestGetReclamanteByIdUseCase:
    """Testes para o caso de uso de busca por ID"""

    @pytest.mark.asyncio
    async def test_buscar_reclamante_existente(self):
        """Testa busca de reclamante existente"""
        # Arrange
        repository = AsyncMock()
        repository.get_by_id.return_value = make_reclamante(id=1)
        use_case = GetReclamanteByIdUseCase(repository)

        # Act
        result = await use_case.execute(1)

        # Assert
        assert result is not None
        assert result.id == 1
        repository.get_by_id.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_buscar_reclamante_inexistente(self):
        """Testa busca de reclamante inexistente"""
        # Arrange
        repository = AsyncMock()
        repository.get_by_id.return_value = None
        use_case = GetReclamanteByIdUseCase(repository)

        # Act
        result = await use_case.execute(999)

        # Assert
        assert result is None
        repository.get_by_id.assert_called_once_with(999)

    @pytest.mark.asyncio
    async def test_buscar_reclamante_com_id_zero_falha(self):
        """Testa validação de ID zero"""
        # Arrange
        repository = AsyncMock()
        use_case = GetReclamanteByIdUseCase(repository)

        # Act & Assert
        with pytest.raises(ValueError, match="ID de reclamante deve ser maior que zero"):
            await use_case.execute(0)

        repository.get_by_id.assert_not_called()

    @pytest.mark.asyncio
    async def test_buscar_reclamante_com_id_negativo_falha(self):
        """Testa validação de ID negativo"""
        # Arrange
        repository = AsyncMock()
        use_case = GetReclamanteByIdUseCase(repository)

        # Act & Assert
        with pytest.raises(ValueError, match="ID de reclamante deve ser maior que zero"):
            await use_case.execute(-10)

        repository.get_by_id.assert_not_called()


class TestGetAllReclamantesUseCase:
    """Testes para o caso de uso de listagem"""

    @pytest.mark.asyncio
    async def test_listar_reclamantes_com_paginacao_padrao(self):
        """Testa listagem com parâmetros padrão"""
        # Arrange
        repository = AsyncMock()
        repository.get_all.return_value = [make_reclamante(id=1)]
        use_case = GetAllReclamantesUseCase(repository)

        # Act
        result = await use_case.execute()

        # Assert
        assert len(result) == 1
        repository.get_all.assert_called_once_with(0, 100)

    @pytest.mark.asyncio
    async def test_listar_reclamantes_com_paginacao_customizada(self):
        """Testa listagem com paginação customizada"""
        # Arrange
        repository = AsyncMock()
        repository.get_all.return_value = []
        use_case = GetAllReclamantesUseCase(repository)

        # Act
        await use_case.execute(skip=5, limit=20)

        # Assert
        repository.get_all.assert_called_once_with(5, 20)

    @pytest.mark.asyncio
    async def test_listar_reclamantes_com_skip_negativo_falha(self):
        """Testa validação de skip negativo"""
        # Arrange
        repository = AsyncMock()
        use_case = GetAllReclamantesUseCase(repository)

        # Act & Assert
        with pytest.raises(ValueError, match="Skip não pode ser negativo"):
            await use_case.execute(skip=-1)

        repository.get_all.assert_not_called()

    @pytest.mark.asyncio
    async def test_listar_reclamantes_com_limit_zero_falha(self):
        """Testa validação de limit igual a zero"""
        # Arrange
        repository = AsyncMock()
        use_case = GetAllReclamantesUseCase(repository)

        # Act & Assert
        with pytest.raises(ValueError, match="Limit deve estar entre 1 e 1000"):
            await use_case.execute(limit=0)

        repository.get_all.assert_not_called()

    @pytest.mark.asyncio
    async def test_listar_reclamantes_com_limit_maior_que_1000_falha(self):
        """Testa validação de limit acima de 1000"""
        # Arrange
        repository = AsyncMock()
        use_case = GetAllReclamantesUseCase(repository)

        # Act & Assert
        with pytest.raises(ValueError, match="Limit deve estar entre 1 e 1000"):
            await use_case.execute(limit=1001)

        repository.get_all.assert_not_called()


class TestUpdateReclamanteUseCase:
    """Testes para o caso de uso de atualização"""

    @pytest.mark.asyncio
    async def test_atualizar_reclamante_com_sucesso(self):
        """Testa atualização de reclamante existente"""
        # Arrange
        repository = AsyncMock()
        existente = make_reclamante(id=1, nome="João")
        atualizado = make_reclamante(id=1, nome="João Silva", telefone="11988887777")
        repository.get_by_id.return_value = existente
        repository.update.return_value = atualizado
        use_case = UpdateReclamanteUseCase(repository)

        # Act
        result = await use_case.execute(1, atualizado)

        # Assert
        assert result is not None
        assert result.nome == "João Silva"
        repository.update.assert_called_once_with(1, atualizado)

    @pytest.mark.asyncio
    async def test_atualizar_reclamante_inexistente_retorna_none(self):
        """Testa atualização quando reclamante não existe"""
        # Arrange
        repository = AsyncMock()
        repository.get_by_id.return_value = None
        use_case = UpdateReclamanteUseCase(repository)

        # Act
        result = await use_case.execute(999, make_reclamante(nome="Novo"))

        # Assert
        assert result is None
        repository.update.assert_not_called()

    @pytest.mark.asyncio
    async def test_atualizar_reclamante_com_id_negativo_retorna_none(self):
        """Documenta comportamento atual para ID negativo no update"""
        # Arrange
        repository = AsyncMock()
        repository.get_by_id.return_value = None
        use_case = UpdateReclamanteUseCase(repository)

        # Act
        result = await use_case.execute(-1, make_reclamante(nome="Novo"))

        # Assert
        assert result is None
        repository.get_by_id.assert_called_once_with(-1)


class TestDeleteReclamanteUseCase:
    """Testes para o caso de uso de exclusão"""

    @pytest.mark.asyncio
    async def test_deletar_reclamante_existente(self):
        """Testa exclusão de reclamante existente"""
        # Arrange
        repository = AsyncMock()
        repository.get_by_id.return_value = make_reclamante(id=1)
        repository.delete.return_value = True
        use_case = DeleteReclamanteUseCase(repository)

        # Act
        result = await use_case.execute(1)

        # Assert
        assert result is True
        repository.delete.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_deletar_reclamante_inexistente_retorna_false(self):
        """Testa exclusão de reclamante inexistente"""
        # Arrange
        repository = AsyncMock()
        repository.get_by_id.return_value = None
        use_case = DeleteReclamanteUseCase(repository)

        # Act
        result = await use_case.execute(999)

        # Assert
        assert result is False
        repository.delete.assert_not_called()

    @pytest.mark.asyncio
    async def test_deletar_reclamante_com_id_negativo_retorna_false(self):
        """Documenta comportamento atual para ID negativo no delete"""
        # Arrange
        repository = AsyncMock()
        repository.get_by_id.return_value = None
        use_case = DeleteReclamanteUseCase(repository)

        # Act
        result = await use_case.execute(-5)

        # Assert
        assert result is False
        repository.get_by_id.assert_called_once_with(-5)
