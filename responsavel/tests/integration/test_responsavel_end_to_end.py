"""
Testes de integração end-to-end para o fluxo completo de Responsavel
Testa a integração entre Use Cases, Repository e Database
"""
import pytest
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
from responsavel.src.infrastructure.repositories.responsavel_repository_impl import ResponsavelRepositoryImpl


@pytest.mark.asyncio
class TestResponsavelEndToEnd:
    """Testes end-to-end do fluxo completo de Responsavel"""

    async def test_fluxo_completo_criar_buscar_atualizar_deletar(self, test_session):
        """Testa o fluxo completo: criar -> buscar -> atualizar -> deletar"""
        # Arrange
        repository = ResponsavelRepositoryImpl(test_session)
        create_use_case = CreateResponsavelUseCase(repository)
        get_use_case = GetResponsavelByIdUseCase(repository)
        update_use_case = UpdateResponsavelUseCase(repository)
        delete_use_case = DeleteResponsavelUseCase(repository)

        # 1. CRIAR RESPONSÁVEL
        responsavel_para_criar = Responsavel(
            nome="João Silva",
            cargo="Segurança",
            telefone="11999999999",
            ativo=False  # Será mudado para True pelo use case
        )

        responsavel_criado = await create_use_case.execute(responsavel_para_criar)

        # Assert criar
        assert responsavel_criado.id is not None
        assert responsavel_criado.ativo is True  # Use case garante ativo=True
        assert responsavel_criado.nome == "João Silva"

        # 2. BUSCAR RESPONSÁVEL
        responsavel_encontrado = await get_use_case.execute(responsavel_criado.id)

        # Assert buscar
        assert responsavel_encontrado is not None
        assert responsavel_encontrado.id == responsavel_criado.id
        assert responsavel_encontrado.nome == "João Silva"

        # 3. ATUALIZAR RESPONSÁVEL
        responsavel_encontrado.nome = "João Santos"
        responsavel_encontrado.cargo = "Supervisor de Segurança"

        responsavel_atualizado = await update_use_case.execute(
            responsavel_encontrado.id, responsavel_encontrado
        )

        # Assert atualizar
        assert responsavel_atualizado is not None
        assert responsavel_atualizado.nome == "João Santos"
        assert responsavel_atualizado.cargo == "Supervisor de Segurança"

        # 4. DELETAR RESPONSÁVEL
        resultado_delete = await delete_use_case.execute(responsavel_atualizado.id)
        responsavel_deletado = await get_use_case.execute(responsavel_atualizado.id)

        # Assert deletar
        assert resultado_delete is True
        assert responsavel_deletado is None

    async def test_fluxo_desativar_e_reativar_responsavel(self, test_session):
        """Testa o fluxo de desativar e reativar um responsável"""
        # Arrange
        repository = ResponsavelRepositoryImpl(test_session)
        create_use_case = CreateResponsavelUseCase(repository)
        desativar_use_case = DesativarResponsavelUseCase(repository)
        reativar_use_case = ReativarResponsavelUseCase(repository)
        get_use_case = GetResponsavelByIdUseCase(repository)

        # 1. Cria responsável (sempre ativo)
        responsavel = Responsavel(
            nome="Maria Souza",
            cargo="Recepcionista",
            telefone="11988888888",
            ativo=True
        )

        responsavel_criado = await create_use_case.execute(responsavel)
        assert responsavel_criado.ativo is True

        # 2. Desativa
        responsavel_desativado = await desativar_use_case.execute(responsavel_criado.id)
        assert responsavel_desativado.ativo is False

        # Verifica no banco
        responsavel_do_banco = await get_use_case.execute(responsavel_criado.id)
        assert responsavel_do_banco.ativo is False

        # 3. Reativa
        responsavel_reativado = await reativar_use_case.execute(responsavel_criado.id)
        assert responsavel_reativado.ativo is True

        # Verifica no banco
        responsavel_do_banco = await get_use_case.execute(responsavel_criado.id)
        assert responsavel_do_banco.ativo is True

    async def test_fluxo_listar_com_paginacao(self, test_session):
        """Testa listagem com paginação"""
        # Arrange
        repository = ResponsavelRepositoryImpl(test_session)
        create_use_case = CreateResponsavelUseCase(repository)
        list_use_case = GetAllResponsaveisUseCase(repository)

        # Cria 15 responsáveis
        for i in range(15):
            responsavel = Responsavel(
                nome=f"Responsavel {i}",
                cargo="Cargo Teste",
                telefone=f"1199999{i:04d}",
                ativo=True
            )
            await create_use_case.execute(responsavel)

        # Act
        primeira_pagina = await list_use_case.execute(skip=0, limit=10)
        segunda_pagina = await list_use_case.execute(skip=10, limit=10)

        # Assert
        assert len(primeira_pagina) == 10
        assert len(segunda_pagina) == 5
        assert primeira_pagina[0].id != segunda_pagina[0].id

    async def test_fluxo_buscar_por_status_ativo(self, test_session):
        """Testa busca de responsáveis por status ativo"""
        # Arrange
        repository = ResponsavelRepositoryImpl(test_session)
        create_use_case = CreateResponsavelUseCase(repository)
        desativar_use_case = DesativarResponsavelUseCase(repository)
        buscar_ativo_use_case = GetResponsaveisByAtivoUseCase(repository)

        # Cria 5 responsáveis (todos começam ativos)
        responsaveis_criados = []
        for i in range(5):
            responsavel = Responsavel(
                nome=f"Responsavel {i}",
                cargo="Cargo Teste",
                telefone=f"1199999{i:04d}",
                ativo=True
            )
            responsavel_criado = await create_use_case.execute(responsavel)
            responsaveis_criados.append(responsavel_criado)

        # Desativa 2 responsáveis
        await desativar_use_case.execute(responsaveis_criados[1].id)
        await desativar_use_case.execute(responsaveis_criados[3].id)

        # Act
        ativos = await buscar_ativo_use_case.execute(True)
        inativos = await buscar_ativo_use_case.execute(False)

        # Assert
        assert len(ativos) == 3
        assert len(inativos) == 2
        assert all(r.ativo is True for r in ativos)
        assert all(r.ativo is False for r in inativos)

    async def test_fluxo_validacao_telefone_invalido_na_criacao(self, test_session):
        """Testa que não é possível criar responsável com telefone inválido"""
        # Arrange
        repository = ResponsavelRepositoryImpl(test_session)
        create_use_case = CreateResponsavelUseCase(repository)

        responsavel = Responsavel(
            nome="João Silva",
            cargo="Segurança",
            telefone="12345",  # Telefone inválido
            ativo=True
        )

        # Act & Assert
        with pytest.raises(ValueError, match="Telefone deve conter 10 ou 11 dígitos"):
            await create_use_case.execute(responsavel)

        # Verifica que nenhum responsável foi criado
        all_responsaveis = await repository.get_all()
        assert len(all_responsaveis) == 0

    async def test_fluxo_desativar_ja_inativo_sem_erro(self, test_session):
        """Testa que desativar responsável já inativo não causa erro"""
        # Arrange
        repository = ResponsavelRepositoryImpl(test_session)
        create_use_case = CreateResponsavelUseCase(repository)
        desativar_use_case = DesativarResponsavelUseCase(repository)

        responsavel = Responsavel(
            nome="João Silva",
            cargo="Segurança",
            telefone="11999999999",
            ativo=True
        )

        responsavel_criado = await create_use_case.execute(responsavel)

        # Desativa duas vezes (segunda não deve gerar erro)
        await desativar_use_case.execute(responsavel_criado.id)
        resultado = await desativar_use_case.execute(responsavel_criado.id)  # Segunda desativação

        # Assert
        assert resultado is not None
        assert resultado.ativo is False

    async def test_fluxo_reativar_ja_ativo_sem_erro(self, test_session):
        """Testa que reativar responsável já ativo não causa erro"""
        # Arrange
        repository = ResponsavelRepositoryImpl(test_session)
        create_use_case = CreateResponsavelUseCase(repository)
        reativar_use_case = ReativarResponsavelUseCase(repository)

        responsavel = Responsavel(
            nome="João Silva",
            cargo="Segurança",
            telefone="11999999999",
            ativo=True
        )

        responsavel_criado = await create_use_case.execute(responsavel)
        assert responsavel_criado.ativo is True

        # Tenta reativar um responsável já ativo
        resultado = await reativar_use_case.execute(responsavel_criado.id)

        # Assert
        assert resultado is not None
        assert resultado.ativo is True

    async def test_fluxo_contar_total_de_responsaveis(self, test_session):
        """Testa contagem total de responsáveis"""
        # Arrange
        repository = ResponsavelRepositoryImpl(test_session)
        create_use_case = CreateResponsavelUseCase(repository)

        # Cria 6 responsáveis
        for i in range(6):
            responsavel = Responsavel(
                nome=f"Responsavel {i}",
                cargo="Cargo Teste",
                telefone=f"1199999{i:04d}",
                ativo=True
            )
            await create_use_case.execute(responsavel)

        # Act
        total = await repository.count()

        # Assert
        assert total == 6

    async def test_fluxo_metodo_entidade_desativar_responsavel(self, test_session):
        """Testa o fluxo de desativar responsável usando método da entidade"""
        # Arrange
        repository = ResponsavelRepositoryImpl(test_session)
        create_use_case = CreateResponsavelUseCase(repository)
        get_use_case = GetResponsavelByIdUseCase(repository)

        # Cria responsável
        responsavel = Responsavel(
            nome="Ana Lima",
            cargo="Coordenadora",
            telefone="31966665555",
            ativo=True
        )

        responsavel_criado = await create_use_case.execute(responsavel)

        # Act - Busca responsável, desativa usando método da entidade e salva
        responsavel_para_desativar = await get_use_case.execute(responsavel_criado.id)
        assert responsavel_para_desativar.ativo is True

        responsavel_para_desativar.desativar_responsavel()
        await repository.update(responsavel_para_desativar.id, responsavel_para_desativar)

        # Verifica no banco
        responsavel_verificado = await get_use_case.execute(responsavel_criado.id)

        # Assert
        assert responsavel_verificado.ativo is False

    async def test_fluxo_validacao_id_invalido_nas_buscas(self, test_session):
        """Testa validação de IDs inválidos"""
        # Arrange
        repository = ResponsavelRepositoryImpl(test_session)
        get_use_case = GetResponsavelByIdUseCase(repository)
        delete_use_case = DeleteResponsavelUseCase(repository)

        # Testa get com ID zero
        with pytest.raises(ValueError, match="ID do responsável deve ser maior que zero"):
            await get_use_case.execute(0)

        # Testa delete com ID negativo
        with pytest.raises(ValueError, match="ID do responsável deve ser maior que zero"):
            await delete_use_case.execute(-1)
