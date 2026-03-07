"""
Testes de integração end-to-end para o fluxo completo de Local
Testa a integração entre Use Cases, Repository e Database
"""
import pytest
from local.src.domain.entities.local import Local
from local.src.application.use_cases.local_use_cases import (
    CreateLocalUseCase,
    GetLocalByIdUseCase,
    GetAllLocalsUseCase,
    UpdateLocalUseCase,
    DeleteLocalUseCase,
    GetLocalsByBairroUseCase,
)
from local.src.infrastructure.repositories.local_repository_impl import LocalRepositoryImpl


@pytest.mark.asyncio
class TestLocalEndToEnd:
    """Testes end-to-end do fluxo completo de Local"""

    async def test_fluxo_completo_criar_buscar_atualizar_deletar(self, test_session):
        """Testa o fluxo completo: criar -> buscar -> atualizar -> deletar"""
        # Arrange
        repository = LocalRepositoryImpl(test_session)
        create_use_case = CreateLocalUseCase(repository)
        get_use_case = GetLocalByIdUseCase(repository)
        update_use_case = UpdateLocalUseCase(repository)
        delete_use_case = DeleteLocalUseCase(repository)

        # 1. CRIAR LOCAL
        local_para_criar = Local(
            tipo="Metrô",
            descricao="Estação Sé - Plataforma Central",
            bairro="Centro"
        )

        local_criado = await create_use_case.execute(local_para_criar)

        # Assert criar
        assert local_criado.id is not None
        assert local_criado.tipo == "Metrô"
        assert local_criado.bairro == "Centro"

        # 2. BUSCAR LOCAL
        local_encontrado = await get_use_case.execute(local_criado.id)

        # Assert buscar
        assert local_encontrado is not None
        assert local_encontrado.id == local_criado.id
        assert local_encontrado.tipo == "Metrô"

        # 3. ATUALIZAR LOCAL
        local_encontrado.tipo = "Metrô Linha 3"
        local_encontrado.descricao = "Estação Sé - Plataforma Atualizada"

        local_atualizado = await update_use_case.execute(
            local_encontrado.id, local_encontrado
        )

        # Assert atualizar
        assert local_atualizado is not None
        assert local_atualizado.tipo == "Metrô Linha 3"
        assert local_atualizado.descricao == "Estação Sé - Plataforma Atualizada"

        # 4. DELETAR LOCAL
        resultado_delete = await delete_use_case.execute(local_atualizado.id)
        local_deletado = await get_use_case.execute(local_atualizado.id)

        # Assert deletar
        assert resultado_delete is True
        assert local_deletado is None

    async def test_fluxo_listar_com_paginacao(self, test_session):
        """Testa listagem com paginação"""
        # Arrange
        repository = LocalRepositoryImpl(test_session)
        create_use_case = CreateLocalUseCase(repository)
        list_use_case = GetAllLocalsUseCase(repository)

        # Cria 15 locais
        for i in range(15):
            local = Local(
                tipo=f"Tipo {i}",
                descricao=f"Descrição {i}",
                bairro=f"Bairro {i}"
            )
            await create_use_case.execute(local)

        # Act
        primeira_pagina = await list_use_case.execute(skip=0, limit=10)
        segunda_pagina = await list_use_case.execute(skip=10, limit=10)

        # Assert
        assert len(primeira_pagina) == 10
        assert len(segunda_pagina) == 5
        assert primeira_pagina[0].id != segunda_pagina[0].id

    async def test_fluxo_buscar_por_bairro(self, test_session):
        """Testa busca de locais por bairro"""
        # Arrange
        repository = LocalRepositoryImpl(test_session)
        create_use_case = CreateLocalUseCase(repository)
        buscar_bairro_use_case = GetLocalsByBairroUseCase(repository)

        # Cria locais em bairros diferentes
        await create_use_case.execute(Local(tipo="Metrô", descricao="Estação A", bairro="Centro"))
        await create_use_case.execute(Local(tipo="Ônibus", descricao="Terminal B", bairro="Centro"))
        await create_use_case.execute(Local(tipo="Parque", descricao="Parque C", bairro="Moema"))
        await create_use_case.execute(Local(tipo="Shopping", descricao="Shopping D", bairro="Pinheiros"))

        # Act
        locais_centro = await buscar_bairro_use_case.execute("Centro")
        locais_moema = await buscar_bairro_use_case.execute("Moema")

        # Assert
        assert len(locais_centro) == 2
        assert len(locais_moema) == 1
        assert all(l.bairro == "Centro" for l in locais_centro)

    async def test_fluxo_validacao_bairro_vazio_na_busca(self, test_session):
        """Testa que busca com bairro vazio lança erro"""
        # Arrange
        repository = LocalRepositoryImpl(test_session)
        buscar_bairro_use_case = GetLocalsByBairroUseCase(repository)

        # Act & Assert
        with pytest.raises(ValueError, match="Bairro não pode estar vazio"):
            await buscar_bairro_use_case.execute("")

    async def test_fluxo_validacao_id_invalido_nas_buscas(self, test_session):
        """Testa que busca com ID inválido lança erro"""
        # Arrange
        repository = LocalRepositoryImpl(test_session)
        get_use_case = GetLocalByIdUseCase(repository)
        delete_use_case = DeleteLocalUseCase(repository)

        # Act & Assert - GetById
        with pytest.raises(ValueError, match="ID de local deve ser maior que zero"):
            await get_use_case.execute(0)

        with pytest.raises(ValueError, match="ID de local deve ser maior que zero"):
            await get_use_case.execute(-5)

    async def test_fluxo_skip_negativo_na_listagem(self, test_session):
        """Testa que skip negativo lança erro na listagem"""
        # Arrange
        repository = LocalRepositoryImpl(test_session)
        list_use_case = GetAllLocalsUseCase(repository)

        # Act & Assert
        with pytest.raises(ValueError, match="Skip não pode ser negativo"):
            await list_use_case.execute(skip=-1)

    async def test_fluxo_limit_invalido_na_listagem(self, test_session):
        """Testa que limit inválido lança erro na listagem"""
        # Arrange
        repository = LocalRepositoryImpl(test_session)
        list_use_case = GetAllLocalsUseCase(repository)

        # Act & Assert - limit = 0
        with pytest.raises(ValueError, match="Limit deve estar entre 1 e 1000"):
            await list_use_case.execute(limit=0)

        # Act & Assert - limit > 1000
        with pytest.raises(ValueError, match="Limit deve estar entre 1 e 1000"):
            await list_use_case.execute(limit=1001)

    async def test_fluxo_metodo_entidade_atualizar_descricao(self, test_session):
        """Testa o método de domínio atualizar_descricao através do fluxo completo"""
        # Arrange
        repository = LocalRepositoryImpl(test_session)
        create_use_case = CreateLocalUseCase(repository)
        get_use_case = GetLocalByIdUseCase(repository)
        update_use_case = UpdateLocalUseCase(repository)

        local = Local(
            tipo="Parque",
            descricao="Descrição Original do Parque",
            bairro="Moema"
        )

        local_criado = await create_use_case.execute(local)

        # Usa o método de domínio
        local_criado.atualizar_descricao("Nova descrição do parque atualizada")
        assert local_criado.descricao == "Nova descrição do parque atualizada"

        # Persiste a atualização
        local_atualizado = await update_use_case.execute(local_criado.id, local_criado)

        # Verifica no banco
        local_do_banco = await get_use_case.execute(local_criado.id)

        # Assert
        assert local_atualizado.descricao == "Nova descrição do parque atualizada"
        assert local_do_banco.descricao == "Nova descrição do parque atualizada"

    async def test_fluxo_contar_total_de_locais(self, test_session):
        """Testa contagem de locais através do fluxo completo"""
        # Arrange
        repository = LocalRepositoryImpl(test_session)
        create_use_case = CreateLocalUseCase(repository)

        # Cria 4 locais
        for i in range(4):
            await create_use_case.execute(
                Local(tipo=f"Tipo {i}", descricao=f"Descrição {i}", bairro=f"Bairro {i}")
            )

        # Act
        total = await repository.count()

        # Assert
        assert total == 4

    async def test_fluxo_buscar_local_inexistente_retorna_none(self, test_session):
        """Testa que buscar local inexistente retorna None no fluxo completo"""
        # Arrange
        repository = LocalRepositoryImpl(test_session)
        get_use_case = GetLocalByIdUseCase(repository)

        # Act
        resultado = await get_use_case.execute(9999)

        # Assert
        assert resultado is None

    async def test_fluxo_deletar_local_inexistente(self, test_session):
        """Testa que deletar local inexistente retorna False"""
        # Arrange
        repository = LocalRepositoryImpl(test_session)
        delete_use_case = DeleteLocalUseCase(repository)

        # Act
        resultado = await delete_use_case.execute(9999)

        # Assert
        assert resultado is False
