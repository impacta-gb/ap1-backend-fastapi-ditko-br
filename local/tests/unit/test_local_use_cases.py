"""
Testes unitários para os casos de uso de Local
"""
import pytest
from unittest.mock import AsyncMock
from local.src.domain.entities.local import Local
from local.src.application.use_cases.local_use_cases import (
    CreateLocalUseCase,
    GetLocalByIdUseCase,
    GetAllLocalsUseCase,
    UpdateLocalUseCase,
    DeleteLocalUseCase,
    GetLocalsByBairroUseCase,
)


def make_local(id=None, tipo="Metrô", descricao="Estação Central", bairro="Centro"):
    """Factory helper para criar entidades Local"""
    return Local(id=id, tipo=tipo, descricao=descricao, bairro=bairro)


class TestCreateLocalUseCase:
    """Testes para o caso de uso de criação de local"""

    @pytest.mark.asyncio
    async def test_criar_local_com_sucesso(self):
        """Testa criação de local com dados válidos"""
        # Arrange
        repository_mock = AsyncMock()
        local = make_local()
        local_criado = make_local(id=1)

        repository_mock.create.return_value = local_criado
        use_case = CreateLocalUseCase(repository_mock)

        # Act
        resultado = await use_case.execute(local)

        # Assert
        assert resultado.id == 1
        assert resultado.tipo == "Metrô"
        repository_mock.create.assert_called_once_with(local)

    @pytest.mark.asyncio
    async def test_criar_local_chama_repositorio(self):
        """Testa que o use case sempre delega para o repositório"""
        # Arrange
        repository_mock = AsyncMock()
        local = make_local()
        repository_mock.create.return_value = make_local(id=2)
        use_case = CreateLocalUseCase(repository_mock)

        # Act
        await use_case.execute(local)

        # Assert
        repository_mock.create.assert_called_once()


class TestGetLocalByIdUseCase:
    """Testes para o caso de uso de busca de local por ID"""

    @pytest.mark.asyncio
    async def test_buscar_local_existente(self):
        """Testa busca de local que existe"""
        # Arrange
        repository_mock = AsyncMock()
        local = make_local(id=1)

        repository_mock.get_by_id.return_value = local
        use_case = GetLocalByIdUseCase(repository_mock)

        # Act
        resultado = await use_case.execute(1)

        # Assert
        assert resultado is not None
        assert resultado.id == 1
        repository_mock.get_by_id.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_buscar_local_inexistente(self):
        """Testa busca de local que não existe"""
        # Arrange
        repository_mock = AsyncMock()
        repository_mock.get_by_id.return_value = None
        use_case = GetLocalByIdUseCase(repository_mock)

        # Act
        resultado = await use_case.execute(999)

        # Assert
        assert resultado is None
        repository_mock.get_by_id.assert_called_once_with(999)

    @pytest.mark.asyncio
    async def test_buscar_local_com_id_invalido(self):
        """Testa que não é possível buscar local com ID <= 0"""
        # Arrange
        repository_mock = AsyncMock()
        use_case = GetLocalByIdUseCase(repository_mock)

        # Act & Assert
        with pytest.raises(ValueError, match="ID de local deve ser maior que zero"):
            await use_case.execute(0)

        repository_mock.get_by_id.assert_not_called()

    @pytest.mark.asyncio
    async def test_buscar_local_com_id_negativo(self):
        """Testa que não é possível buscar local com ID negativo"""
        # Arrange
        repository_mock = AsyncMock()
        use_case = GetLocalByIdUseCase(repository_mock)

        # Act & Assert
        with pytest.raises(ValueError, match="ID de local deve ser maior que zero"):
            await use_case.execute(-10)

        repository_mock.get_by_id.assert_not_called()


class TestGetAllLocalsUseCase:
    """Testes para o caso de uso de listagem de locais"""

    @pytest.mark.asyncio
    async def test_listar_todos_locais(self):
        """Testa listagem de locais com paginação padrão"""
        # Arrange
        repository_mock = AsyncMock()
        locais = [
            make_local(id=1, bairro="Centro"),
            make_local(id=2, bairro="Mooca"),
        ]

        repository_mock.get_all.return_value = locais
        use_case = GetAllLocalsUseCase(repository_mock)

        # Act
        resultado = await use_case.execute()

        # Assert
        assert len(resultado) == 2
        repository_mock.get_all.assert_called_once_with(0, 100)

    @pytest.mark.asyncio
    async def test_listar_locais_com_paginacao_customizada(self):
        """Testa listagem com paginação customizada"""
        # Arrange
        repository_mock = AsyncMock()
        repository_mock.get_all.return_value = []
        use_case = GetAllLocalsUseCase(repository_mock)

        # Act
        await use_case.execute(skip=5, limit=20)

        # Assert
        repository_mock.get_all.assert_called_once_with(5, 20)

    @pytest.mark.asyncio
    async def test_listar_locais_com_skip_negativo(self):
        """Testa que skip negativo lança erro"""
        # Arrange
        repository_mock = AsyncMock()
        use_case = GetAllLocalsUseCase(repository_mock)

        # Act & Assert
        with pytest.raises(ValueError, match="Skip não pode ser negativo"):
            await use_case.execute(skip=-1)

        repository_mock.get_all.assert_not_called()

    @pytest.mark.asyncio
    async def test_listar_locais_com_limit_zero(self):
        """Testa que limit igual a zero lança erro"""
        # Arrange
        repository_mock = AsyncMock()
        use_case = GetAllLocalsUseCase(repository_mock)

        # Act & Assert
        with pytest.raises(ValueError, match="Limit deve estar entre 1 e 1000"):
            await use_case.execute(limit=0)

        repository_mock.get_all.assert_not_called()

    @pytest.mark.asyncio
    async def test_listar_locais_com_limit_maior_que_1000(self):
        """Testa que limit maior que 1000 lança erro"""
        # Arrange
        repository_mock = AsyncMock()
        use_case = GetAllLocalsUseCase(repository_mock)

        # Act & Assert
        with pytest.raises(ValueError, match="Limit deve estar entre 1 e 1000"):
            await use_case.execute(limit=1001)

        repository_mock.get_all.assert_not_called()


class TestUpdateLocalUseCase:
    """Testes para o caso de uso de atualização de local"""

    @pytest.mark.asyncio
    async def test_atualizar_local_com_sucesso(self):
        """Testa atualização de local com dados válidos"""
        # Arrange
        repository_mock = AsyncMock()
        local_existente = make_local(id=1)
        local_atualizado = make_local(id=1, descricao="Descrição atualizada")

        repository_mock.get_by_id.return_value = local_existente
        repository_mock.update.return_value = local_atualizado
        use_case = UpdateLocalUseCase(repository_mock)

        # Act
        resultado = await use_case.execute(1, local_atualizado)

        # Assert
        assert resultado is not None
        assert resultado.descricao == "Descrição atualizada"
        repository_mock.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_atualizar_local_inexistente(self):
        """Testa atualização de local que não existe retorna None"""
        # Arrange
        repository_mock = AsyncMock()
        repository_mock.get_by_id.return_value = None
        use_case = UpdateLocalUseCase(repository_mock)

        local = make_local()

        # Act
        resultado = await use_case.execute(9999, local)

        # Assert
        assert resultado is None
        repository_mock.update.assert_not_called()


class TestDeleteLocalUseCase:
    """Testes para o caso de uso de exclusão de local"""

    @pytest.mark.asyncio
    async def test_deletar_local_existente(self):
        """Testa exclusão de local existente"""
        # Arrange
        repository_mock = AsyncMock()
        local = make_local(id=1)

        repository_mock.get_by_id.return_value = local
        repository_mock.delete.return_value = True
        use_case = DeleteLocalUseCase(repository_mock)

        # Act
        resultado = await use_case.execute(1)

        # Assert
        assert resultado is True
        repository_mock.delete.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_deletar_local_inexistente(self):
        """Testa exclusão de local inexistente retorna False"""
        # Arrange
        repository_mock = AsyncMock()
        repository_mock.get_by_id.return_value = None
        use_case = DeleteLocalUseCase(repository_mock)

        # Act
        resultado = await use_case.execute(999)

        # Assert
        assert resultado is False
        repository_mock.delete.assert_not_called()


class TestGetLocalsByBairroUseCase:
    """Testes para o caso de uso de busca por bairro"""

    @pytest.mark.asyncio
    async def test_buscar_por_bairro_com_sucesso(self):
        """Testa busca de locais por bairro"""
        # Arrange
        repository_mock = AsyncMock()
        locais = [
            make_local(id=1, bairro="Centro"),
            make_local(id=2, bairro="Centro"),
        ]

        repository_mock.get_by_bairro.return_value = locais
        use_case = GetLocalsByBairroUseCase(repository_mock)

        # Act
        resultado = await use_case.execute("Centro")

        # Assert
        assert len(resultado) == 2
        repository_mock.get_by_bairro.assert_called_once_with("Centro")

    @pytest.mark.asyncio
    async def test_buscar_por_bairro_vazio(self):
        """Testa que bairro vazio lança erro"""
        # Arrange
        repository_mock = AsyncMock()
        use_case = GetLocalsByBairroUseCase(repository_mock)

        # Act & Assert
        with pytest.raises(ValueError, match="Bairro não pode estar vazio"):
            await use_case.execute("")

        repository_mock.get_by_bairro.assert_not_called()

    @pytest.mark.asyncio
    async def test_buscar_por_bairro_apenas_espacos(self):
        """Testa que bairro com apenas espaços lança erro"""
        # Arrange
        repository_mock = AsyncMock()
        use_case = GetLocalsByBairroUseCase(repository_mock)

        # Act & Assert
        with pytest.raises(ValueError, match="Bairro não pode estar vazio"):
            await use_case.execute("   ")

        repository_mock.get_by_bairro.assert_not_called()

    @pytest.mark.asyncio
    async def test_buscar_por_bairro_sem_resultados(self):
        """Testa busca por bairro que não possui locais"""
        # Arrange
        repository_mock = AsyncMock()
        repository_mock.get_by_bairro.return_value = []
        use_case = GetLocalsByBairroUseCase(repository_mock)

        # Act
        resultado = await use_case.execute("Bairro Inexistente")

        # Assert
        assert resultado == []
        repository_mock.get_by_bairro.assert_called_once_with("Bairro Inexistente")
