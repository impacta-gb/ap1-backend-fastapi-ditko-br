"""
Testes unitários para os casos de uso de Responsavel
"""
import pytest
from unittest.mock import AsyncMock
from responsavel.src.domain.entities.responsavel import Responsavel
from responsavel.src.application.use_cases.responsavel_use_cases import (
    CreateResponsavelUseCase,
    GetResponsavelByIdUseCase,
    GetAllResponsaveisUseCase,
    UpdateResponsavelUseCase,
    DeleteResponsavelUseCase,
    DesativarResponsavelUseCase,
    ReativarResponsavelUseCase,
    GetResponsaveisByAtivoUseCase
)


class TestCreateResponsavelUseCase:
    """Testes para o caso de uso de criação de responsável"""

    @pytest.mark.asyncio
    async def test_criar_responsavel_com_sucesso(self):
        """Testa criação de responsável com dados válidos"""
        # Arrange
        repository_mock = AsyncMock()

        responsavel = Responsavel(
            nome="João Silva",
            cargo="Segurança",
            telefone="11999999999",
            ativo=True
        )

        responsavel_criado = Responsavel(
            id=1,
            nome="João Silva",
            cargo="Segurança",
            telefone="11999999999",
            ativo=True
        )

        repository_mock.create.return_value = responsavel_criado
        use_case = CreateResponsavelUseCase(repository_mock)

        # Act
        resultado = await use_case.execute(responsavel)

        # Assert
        assert resultado.id == 1
        assert resultado.ativo is True
        repository_mock.create.assert_called_once_with(responsavel)

    @pytest.mark.asyncio
    async def test_criar_responsavel_sempre_define_ativo_como_true(self):
        """Testa que o use case sempre define ativo como True na criação"""
        # Arrange
        repository_mock = AsyncMock()

        responsavel = Responsavel(
            nome="João Silva",
            cargo="Segurança",
            telefone="11999999999",
            ativo=False  # Tentando criar inativo
        )

        responsavel_criado = Responsavel(
            id=1,
            nome="João Silva",
            cargo="Segurança",
            telefone="11999999999",
            ativo=True
        )

        repository_mock.create.return_value = responsavel_criado
        use_case = CreateResponsavelUseCase(repository_mock)

        # Act
        resultado = await use_case.execute(responsavel)

        # Assert - O use case deve ter mudado para True
        assert responsavel.ativo is True
        assert resultado.ativo is True

    @pytest.mark.asyncio
    async def test_criar_responsavel_com_telefone_invalido(self):
        """Testa que não é possível criar responsável com telefone inválido"""
        # Arrange
        repository_mock = AsyncMock()

        responsavel = Responsavel(
            nome="João Silva",
            cargo="Segurança",
            telefone="12345",  # Telefone muito curto
            ativo=True
        )

        use_case = CreateResponsavelUseCase(repository_mock)

        # Act & Assert
        with pytest.raises(ValueError, match="Telefone deve conter 10 ou 11 dígitos"):
            await use_case.execute(responsavel)

        repository_mock.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_criar_responsavel_com_telefone_letras(self):
        """Testa que não é possível criar responsável com letras no telefone"""
        # Arrange
        repository_mock = AsyncMock()

        responsavel = Responsavel(
            nome="João Silva",
            cargo="Segurança",
            telefone="1199abcdefg",
            ativo=True
        )

        use_case = CreateResponsavelUseCase(repository_mock)

        # Act & Assert
        with pytest.raises(ValueError, match="Telefone deve conter 10 ou 11 dígitos"):
            await use_case.execute(responsavel)

        repository_mock.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_criar_responsavel_com_telefone_formatado(self):
        """Testa que telefone com formatação é aceito se tiver 10-11 dígitos"""
        # Arrange
        repository_mock = AsyncMock()

        responsavel = Responsavel(
            nome="João Silva",
            cargo="Segurança",
            telefone="(11)99999-9999",  # Formatado mas com 11 dígitos
            ativo=True
        )

        responsavel_criado = Responsavel(
            id=1,
            nome="João Silva",
            cargo="Segurança",
            telefone="(11)99999-9999",
            ativo=True
        )

        repository_mock.create.return_value = responsavel_criado
        use_case = CreateResponsavelUseCase(repository_mock)

        # Act
        resultado = await use_case.execute(responsavel)

        # Assert
        assert resultado.id == 1
        repository_mock.create.assert_called_once()


class TestGetResponsavelByIdUseCase:
    """Testes para o caso de uso de busca de responsável por ID"""

    @pytest.mark.asyncio
    async def test_buscar_responsavel_existente(self):
        """Testa busca de responsável que existe"""
        # Arrange
        repository_mock = AsyncMock()
        responsavel = Responsavel(
            id=1,
            nome="João Silva",
            cargo="Segurança",
            telefone="11999999999",
            ativo=True
        )

        repository_mock.get_by_id.return_value = responsavel
        use_case = GetResponsavelByIdUseCase(repository_mock)

        # Act
        resultado = await use_case.execute(1)

        # Assert
        assert resultado is not None
        assert resultado.id == 1
        repository_mock.get_by_id.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_buscar_responsavel_inexistente(self):
        """Testa busca de responsável que não existe"""
        # Arrange
        repository_mock = AsyncMock()
        repository_mock.get_by_id.return_value = None
        use_case = GetResponsavelByIdUseCase(repository_mock)

        # Act
        resultado = await use_case.execute(999)

        # Assert
        assert resultado is None
        repository_mock.get_by_id.assert_called_once_with(999)

    @pytest.mark.asyncio
    async def test_buscar_responsavel_com_id_invalido(self):
        """Testa que não é possível buscar responsável com ID <= 0"""
        # Arrange
        repository_mock = AsyncMock()
        use_case = GetResponsavelByIdUseCase(repository_mock)

        # Act & Assert
        with pytest.raises(ValueError, match="ID do responsável deve ser maior que zero"):
            await use_case.execute(0)

        repository_mock.get_by_id.assert_not_called()

    @pytest.mark.asyncio
    async def test_buscar_responsavel_com_id_negativo(self):
        """Testa que não é possível buscar responsável com ID negativo"""
        # Arrange
        repository_mock = AsyncMock()
        use_case = GetResponsavelByIdUseCase(repository_mock)

        # Act & Assert
        with pytest.raises(ValueError, match="ID do responsável deve ser maior que zero"):
            await use_case.execute(-5)

        repository_mock.get_by_id.assert_not_called()


class TestGetAllResponsaveisUseCase:
    """Testes para o caso de uso de listagem de responsáveis"""

    @pytest.mark.asyncio
    async def test_listar_todos_responsaveis(self):
        """Testa listagem de responsáveis com paginação padrão"""
        # Arrange
        repository_mock = AsyncMock()
        responsaveis = [
            Responsavel(id=1, nome="João", cargo="Segurança", telefone="11999999999", ativo=True),
            Responsavel(id=2, nome="Maria", cargo="Recepcionista", telefone="11988888888", ativo=True),
        ]

        repository_mock.get_all.return_value = responsaveis
        use_case = GetAllResponsaveisUseCase(repository_mock)

        # Act
        resultado = await use_case.execute()

        # Assert
        assert len(resultado) == 2
        repository_mock.get_all.assert_called_once_with(0, 100)

    @pytest.mark.asyncio
    async def test_listar_responsaveis_com_paginacao_customizada(self):
        """Testa listagem de responsáveis com paginação customizada"""
        # Arrange
        repository_mock = AsyncMock()
        repository_mock.get_all.return_value = []
        use_case = GetAllResponsaveisUseCase(repository_mock)

        # Act
        await use_case.execute(skip=10, limit=50)

        # Assert
        repository_mock.get_all.assert_called_once_with(10, 50)

    @pytest.mark.asyncio
    async def test_listar_responsaveis_com_skip_negativo(self):
        """Testa que não é possível usar skip negativo"""
        # Arrange
        repository_mock = AsyncMock()
        use_case = GetAllResponsaveisUseCase(repository_mock)

        # Act & Assert
        with pytest.raises(ValueError, match="Skip não pode ser negativo"):
            await use_case.execute(skip=-1)

        repository_mock.get_all.assert_not_called()

    @pytest.mark.asyncio
    async def test_listar_responsaveis_com_limit_zero(self):
        """Testa que não é possível usar limit <= 0"""
        # Arrange
        repository_mock = AsyncMock()
        use_case = GetAllResponsaveisUseCase(repository_mock)

        # Act & Assert
        with pytest.raises(ValueError, match="Limit deve estar entre 1 e 1000"):
            await use_case.execute(limit=0)

        repository_mock.get_all.assert_not_called()

    @pytest.mark.asyncio
    async def test_listar_responsaveis_com_limit_maior_que_1000(self):
        """Testa que não é possível usar limit > 1000"""
        # Arrange
        repository_mock = AsyncMock()
        use_case = GetAllResponsaveisUseCase(repository_mock)

        # Act & Assert
        with pytest.raises(ValueError, match="Limit deve estar entre 1 e 1000"):
            await use_case.execute(limit=1001)

        repository_mock.get_all.assert_not_called()


class TestUpdateResponsavelUseCase:
    """Testes para o caso de uso de atualização de responsável"""

    @pytest.mark.asyncio
    async def test_atualizar_responsavel_com_sucesso(self):
        """Testa atualização de responsável com dados válidos"""
        # Arrange
        repository_mock = AsyncMock()

        responsavel_existente = Responsavel(
            id=1,
            nome="João Silva",
            cargo="Segurança",
            telefone="11999999999",
            ativo=True
        )

        responsavel_atualizado = Responsavel(
            nome="João Santos",
            cargo="Supervisor de Segurança",
            telefone="11999999999",
            ativo=True
        )

        repository_mock.get_by_id.return_value = responsavel_existente
        repository_mock.update.return_value = responsavel_atualizado
        use_case = UpdateResponsavelUseCase(repository_mock)

        # Act
        resultado = await use_case.execute(1, responsavel_atualizado)

        # Assert
        assert resultado is not None
        repository_mock.get_by_id.assert_called_once_with(1)
        repository_mock.update.assert_called_once_with(1, responsavel_atualizado)

    @pytest.mark.asyncio
    async def test_atualizar_responsavel_inexistente(self):
        """Testa atualização de responsável que não existe"""
        # Arrange
        repository_mock = AsyncMock()
        repository_mock.get_by_id.return_value = None
        use_case = UpdateResponsavelUseCase(repository_mock)

        responsavel = Responsavel(
            nome="João Silva",
            cargo="Segurança",
            telefone="11999999999",
            ativo=True
        )

        # Act
        resultado = await use_case.execute(999, responsavel)

        # Assert
        assert resultado is None
        repository_mock.update.assert_not_called()

    @pytest.mark.asyncio
    async def test_atualizar_responsavel_com_telefone_invalido(self):
        """Testa que não é possível atualizar responsável com telefone inválido"""
        # Arrange
        repository_mock = AsyncMock()

        responsavel_existente = Responsavel(
            id=1,
            nome="João Silva",
            cargo="Segurança",
            telefone="11999999999",
            ativo=True
        )

        responsavel_novo = Responsavel(
            nome="João Silva",
            cargo="Segurança",
            telefone="12345",  # Telefone inválido (mudou)
            ativo=True
        )

        repository_mock.get_by_id.return_value = responsavel_existente
        use_case = UpdateResponsavelUseCase(repository_mock)

        # Act & Assert
        with pytest.raises(ValueError, match="Telefone deve conter 10 ou 11 dígitos"):
            await use_case.execute(1, responsavel_novo)

        repository_mock.update.assert_not_called()

    @pytest.mark.asyncio
    async def test_atualizar_responsavel_mesmo_telefone_nao_valida(self):
        """Testa que manter o mesmo telefone não revalida o formato"""
        # Arrange
        repository_mock = AsyncMock()

        responsavel_existente = Responsavel(
            id=1,
            nome="João Silva",
            cargo="Segurança",
            telefone="11999999999",
            ativo=True
        )

        responsavel_novo = Responsavel(
            nome="João Santos",
            cargo="Supervisor",
            telefone="11999999999",  # Mesmo telefone - não revalida
            ativo=True
        )

        repository_mock.get_by_id.return_value = responsavel_existente
        repository_mock.update.return_value = responsavel_novo
        use_case = UpdateResponsavelUseCase(repository_mock)

        # Act
        resultado = await use_case.execute(1, responsavel_novo)

        # Assert
        assert resultado is not None
        repository_mock.update.assert_called_once()


class TestDeleteResponsavelUseCase:
    """Testes para o caso de uso de exclusão de responsável"""

    @pytest.mark.asyncio
    async def test_deletar_responsavel_existente(self):
        """Testa exclusão de responsável existente"""
        # Arrange
        repository_mock = AsyncMock()

        responsavel = Responsavel(
            id=1,
            nome="João Silva",
            cargo="Segurança",
            telefone="11999999999",
            ativo=True
        )

        repository_mock.get_by_id.return_value = responsavel
        repository_mock.delete.return_value = True
        use_case = DeleteResponsavelUseCase(repository_mock)

        # Act
        resultado = await use_case.execute(1)

        # Assert
        assert resultado is True
        repository_mock.delete.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_deletar_responsavel_inexistente(self):
        """Testa exclusão de responsável que não existe"""
        # Arrange
        repository_mock = AsyncMock()
        repository_mock.get_by_id.return_value = None
        use_case = DeleteResponsavelUseCase(repository_mock)

        # Act
        resultado = await use_case.execute(999)

        # Assert
        assert resultado is False
        repository_mock.delete.assert_not_called()

    @pytest.mark.asyncio
    async def test_deletar_responsavel_com_id_invalido(self):
        """Testa que não é possível deletar responsável com ID inválido"""
        # Arrange
        repository_mock = AsyncMock()
        use_case = DeleteResponsavelUseCase(repository_mock)

        # Act & Assert
        with pytest.raises(ValueError, match="ID do responsável deve ser maior que zero"):
            await use_case.execute(0)

        repository_mock.delete.assert_not_called()


class TestDesativarResponsavelUseCase:
    """Testes para o caso de uso de desativação de responsável"""

    @pytest.mark.asyncio
    async def test_desativar_responsavel_ativo(self):
        """Testa desativação de responsável ativo"""
        # Arrange
        repository_mock = AsyncMock()

        responsavel_ativo = Responsavel(
            id=1,
            nome="João Silva",
            cargo="Segurança",
            telefone="11999999999",
            ativo=True
        )

        responsavel_inativo = Responsavel(
            id=1,
            nome="João Silva",
            cargo="Segurança",
            telefone="11999999999",
            ativo=False
        )

        repository_mock.get_by_id.return_value = responsavel_ativo
        repository_mock.update.return_value = responsavel_inativo
        use_case = DesativarResponsavelUseCase(repository_mock)

        # Act
        resultado = await use_case.execute(1)

        # Assert
        assert resultado is not None
        repository_mock.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_desativar_responsavel_ja_inativo(self):
        """Testa que desativar responsável já inativo retorna sem erro"""
        # Arrange
        repository_mock = AsyncMock()

        responsavel_inativo = Responsavel(
            id=1,
            nome="João Silva",
            cargo="Segurança",
            telefone="11999999999",
            ativo=False
        )

        repository_mock.get_by_id.return_value = responsavel_inativo
        use_case = DesativarResponsavelUseCase(repository_mock)

        # Act
        resultado = await use_case.execute(1)

        # Assert
        assert resultado is not None
        assert resultado.ativo is False
        # Não deve chamar update, pois já estava inativo
        repository_mock.update.assert_not_called()

    @pytest.mark.asyncio
    async def test_desativar_responsavel_inexistente(self):
        """Testa que desativar responsável inexistente retorna None"""
        # Arrange
        repository_mock = AsyncMock()
        repository_mock.get_by_id.return_value = None
        use_case = DesativarResponsavelUseCase(repository_mock)

        # Act
        resultado = await use_case.execute(999)

        # Assert
        assert resultado is None
        repository_mock.update.assert_not_called()

    @pytest.mark.asyncio
    async def test_desativar_responsavel_com_id_invalido(self):
        """Testa que ID inválido causa erro"""
        # Arrange
        repository_mock = AsyncMock()
        use_case = DesativarResponsavelUseCase(repository_mock)

        # Act & Assert
        with pytest.raises(ValueError, match="ID do responsável deve ser maior que zero"):
            await use_case.execute(-1)


class TestReativarResponsavelUseCase:
    """Testes para o caso de uso de reativação de responsável"""

    @pytest.mark.asyncio
    async def test_reativar_responsavel_inativo(self):
        """Testa reativação de responsável inativo"""
        # Arrange
        repository_mock = AsyncMock()

        responsavel_inativo = Responsavel(
            id=1,
            nome="João Silva",
            cargo="Segurança",
            telefone="11999999999",
            ativo=False
        )

        responsavel_ativo = Responsavel(
            id=1,
            nome="João Silva",
            cargo="Segurança",
            telefone="11999999999",
            ativo=True
        )

        repository_mock.get_by_id.return_value = responsavel_inativo
        repository_mock.update.return_value = responsavel_ativo
        use_case = ReativarResponsavelUseCase(repository_mock)

        # Act
        resultado = await use_case.execute(1)

        # Assert
        assert resultado is not None
        repository_mock.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_reativar_responsavel_ja_ativo(self):
        """Testa que reativar responsável já ativo retorna sem erro"""
        # Arrange
        repository_mock = AsyncMock()

        responsavel_ativo = Responsavel(
            id=1,
            nome="João Silva",
            cargo="Segurança",
            telefone="11999999999",
            ativo=True
        )

        repository_mock.get_by_id.return_value = responsavel_ativo
        use_case = ReativarResponsavelUseCase(repository_mock)

        # Act
        resultado = await use_case.execute(1)

        # Assert
        assert resultado is not None
        assert resultado.ativo is True
        # Não deve chamar update, pois já estava ativo
        repository_mock.update.assert_not_called()

    @pytest.mark.asyncio
    async def test_reativar_responsavel_inexistente(self):
        """Testa que reativar responsável inexistente retorna None"""
        # Arrange
        repository_mock = AsyncMock()
        repository_mock.get_by_id.return_value = None
        use_case = ReativarResponsavelUseCase(repository_mock)

        # Act
        resultado = await use_case.execute(999)

        # Assert
        assert resultado is None
        repository_mock.update.assert_not_called()

    @pytest.mark.asyncio
    async def test_reativar_responsavel_com_id_invalido(self):
        """Testa que ID inválido causa erro"""
        # Arrange
        repository_mock = AsyncMock()
        use_case = ReativarResponsavelUseCase(repository_mock)

        # Act & Assert
        with pytest.raises(ValueError, match="ID do responsável deve ser maior que zero"):
            await use_case.execute(0)


class TestGetResponsaveisByAtivoUseCase:
    """Testes para o caso de uso de busca de responsáveis por status ativo"""

    @pytest.mark.asyncio
    async def test_buscar_responsaveis_ativos(self):
        """Testa busca de responsáveis ativos"""
        # Arrange
        repository_mock = AsyncMock()
        responsaveis_ativos = [
            Responsavel(id=1, nome="João", cargo="Segurança", telefone="11999999999", ativo=True),
            Responsavel(id=2, nome="Maria", cargo="Recepcionista", telefone="11988888888", ativo=True),
        ]

        repository_mock.get_by_ativo.return_value = responsaveis_ativos
        use_case = GetResponsaveisByAtivoUseCase(repository_mock)

        # Act
        resultado = await use_case.execute(True)

        # Assert
        assert len(resultado) == 2
        assert all(r.ativo is True for r in resultado)
        repository_mock.get_by_ativo.assert_called_once_with(True)

    @pytest.mark.asyncio
    async def test_buscar_responsaveis_inativos(self):
        """Testa busca de responsáveis inativos"""
        # Arrange
        repository_mock = AsyncMock()
        responsaveis_inativos = [
            Responsavel(id=3, nome="Carlos", cargo="Porteiro", telefone="11977777777", ativo=False),
        ]

        repository_mock.get_by_ativo.return_value = responsaveis_inativos
        use_case = GetResponsaveisByAtivoUseCase(repository_mock)

        # Act
        resultado = await use_case.execute(False)

        # Assert
        assert len(resultado) == 1
        assert all(r.ativo is False for r in resultado)
        repository_mock.get_by_ativo.assert_called_once_with(False)

    @pytest.mark.asyncio
    async def test_buscar_responsaveis_com_ativo_nao_booleano(self):
        """Testa que parâmetro ativo não booleano causa erro"""
        # Arrange
        repository_mock = AsyncMock()
        use_case = GetResponsaveisByAtivoUseCase(repository_mock)

        # Act & Assert
        with pytest.raises(ValueError, match="O parâmetro 'ativo' deve ser booleano"):
            await use_case.execute("sim")  # type: ignore

        repository_mock.get_by_ativo.assert_not_called()
