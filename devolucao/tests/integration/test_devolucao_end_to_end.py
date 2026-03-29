"""
Testes de integração end-to-end para o fluxo completo de Devolucao
Testa a integração entre Use Cases, Repository e Database
"""
import pytest
from datetime import datetime, timedelta
from devolucao.src.domain.entities.devolucao import Devolucao
from devolucao.src.application.use_cases.devolucao_use_cases import (
    CreateDevolucaoUseCase,
    GetDevolucaoByIdUseCase,
    GetAllDevolucoesUseCase,
    UpdateDevolucaoUseCase,
    DeleteDevolucaoUseCase,
    GetDevolucoesByDataUseCase,
    CountDevolucoesUseCase,
)
from devolucao.src.infrastructure.repositories.devolucao_repository_impl import DevolucaoRepositoryImpl


def criar_devolucao(**kwargs) -> Devolucao:
    """Helper para criar devolucao de teste"""
    dados = {
        "reclamante_id": 1,
        "item_id": 2,
        "observacao": "Item devolvido ao proprietário",
        "data_devolucao": datetime.now() - timedelta(hours=1),
    }
    dados.update(kwargs)
    return Devolucao(**dados)


@pytest.mark.asyncio
class TestDevolucaoEndToEnd:
    """Testes end-to-end do fluxo completo de Devolucao"""

    async def test_fluxo_completo_criar_buscar_atualizar_deletar(self, test_session):
        """Testa o fluxo completo: criar -> buscar -> atualizar -> deletar"""
        # Arrange
        repository = DevolucaoRepositoryImpl(test_session)
        create_use_case = CreateDevolucaoUseCase(repository)
        get_use_case = GetDevolucaoByIdUseCase(repository)
        update_use_case = UpdateDevolucaoUseCase(repository)
        delete_use_case = DeleteDevolucaoUseCase(repository)

        # 1. CRIAR DEVOLUÇÃO
        devolucao = criar_devolucao(
            observacao="Encontrado na portaria e devolvido",
            reclamante_id=5,
            item_id=10
        )

        devolucao_criada = await create_use_case.execute(devolucao)

        # Assert criar
        assert devolucao_criada.id is not None
        assert devolucao_criada.reclamante_id == 5
        assert devolucao_criada.item_id == 10
        assert devolucao_criada.observacao == "Encontrado na portaria e devolvido"

        # 2. BUSCAR DEVOLUÇÃO
        devolucao_encontrada = await get_use_case.execute(devolucao_criada.id)

        # Assert buscar
        assert devolucao_encontrada is not None
        assert devolucao_encontrada.id == devolucao_criada.id
        assert devolucao_encontrada.reclamante_id == 5

        # 3. ATUALIZAR DEVOLUÇÃO
        devolucao_para_atualizar = criar_devolucao(
            reclamante_id=5,
            item_id=10,
            observacao="Observação atualizada após revisão"
        )

        devolucao_atualizada = await update_use_case.execute(
            devolucao_criada.id, devolucao_para_atualizar
        )

        # Assert atualizar
        assert devolucao_atualizada is not None
        assert devolucao_atualizada.observacao == "Observação atualizada após revisão"
        assert devolucao_atualizada.id == devolucao_criada.id

        # 4. DELETAR DEVOLUÇÃO
        resultado_delete = await delete_use_case.execute(devolucao_atualizada.id)
        devolucao_deletada = await get_use_case.execute(devolucao_atualizada.id)

        # Assert deletar
        assert resultado_delete is True
        assert devolucao_deletada is None

    async def test_fluxo_listar_com_paginacao(self, test_session):
        """Testa listagem com paginação"""
        # Arrange
        repository = DevolucaoRepositoryImpl(test_session)
        create_use_case = CreateDevolucaoUseCase(repository)
        list_use_case = GetAllDevolucoesUseCase(repository)

        # Cria 15 devoluções
        for i in range(15):
            await create_use_case.execute(
                criar_devolucao(
                    reclamante_id=i + 1,
                    item_id=i + 1,
                    observacao=f"Devolução {i + 1}"
                )
            )

        # Act
        primeira_pagina = await list_use_case.execute(skip=0, limit=10)
        segunda_pagina = await list_use_case.execute(skip=10, limit=10)

        # Assert
        assert len(primeira_pagina) == 10
        assert len(segunda_pagina) == 5
        assert primeira_pagina[0].id != segunda_pagina[0].id

    async def test_fluxo_buscar_por_data(self, test_session):
        """Testa busca de devoluções por data"""
        # Arrange
        repository = DevolucaoRepositoryImpl(test_session)
        create_use_case = CreateDevolucaoUseCase(repository)
        buscar_data_use_case = GetDevolucoesByDataUseCase(repository)

        data_alvo = datetime(2024, 5, 20, 10, 0, 0)
        data_outra = datetime(2024, 9, 10, 15, 0, 0)

        await create_use_case.execute(criar_devolucao(data_devolucao=data_alvo, observacao="D1", item_id=1, reclamante_id=1))
        await create_use_case.execute(criar_devolucao(data_devolucao=data_alvo, observacao="D2", item_id=4, reclamante_id=2))
        await create_use_case.execute(criar_devolucao(data_devolucao=data_outra, observacao="D3", item_id=5, reclamante_id=3))

        # Act
        resultado = await buscar_data_use_case.execute(data_alvo)

        # Assert
        assert len(resultado) == 2
        assert all(d.data_devolucao.date() == data_alvo.date() for d in resultado)

    async def test_fluxo_validacao_data_nula_na_busca(self, test_session):
        """Testa que busca com data nula lança erro"""
        # Arrange
        repository = DevolucaoRepositoryImpl(test_session)
        buscar_data_use_case = GetDevolucoesByDataUseCase(repository)

        # Act & Assert
        with pytest.raises(ValueError, match="Data não pode ser nula"):
            await buscar_data_use_case.execute(None)

    async def test_fluxo_validacao_id_invalido_nas_buscas(self, test_session):
        """Testa que busca com ID inválido lança erro"""
        # Arrange
        repository = DevolucaoRepositoryImpl(test_session)
        get_use_case = GetDevolucaoByIdUseCase(repository)

        # Act & Assert
        with pytest.raises(ValueError, match="ID da devolução deve ser maior que zero"):
            await get_use_case.execute(0)

        with pytest.raises(ValueError, match="ID da devolução deve ser maior que zero"):
            await get_use_case.execute(-3)

    async def test_fluxo_skip_negativo_na_listagem(self, test_session):
        """Testa que skip negativo lança erro na listagem"""
        # Arrange
        repository = DevolucaoRepositoryImpl(test_session)
        list_use_case = GetAllDevolucoesUseCase(repository)

        # Act & Assert
        with pytest.raises(ValueError, match="Skip não pode ser negativo"):
            await list_use_case.execute(skip=-1)

    async def test_fluxo_limit_invalido_na_listagem(self, test_session):
        """Testa que limit inválido lança erro na listagem"""
        # Arrange
        repository = DevolucaoRepositoryImpl(test_session)
        list_use_case = GetAllDevolucoesUseCase(repository)

        # Act & Assert — limit = 0
        with pytest.raises(ValueError, match="Limit deve estar entre 1 e 1000"):
            await list_use_case.execute(limit=0)

        # Act & Assert — limit > 1000
        with pytest.raises(ValueError, match="Limit deve estar entre 1 e 1000"):
            await list_use_case.execute(limit=1001)

    async def test_fluxo_metodo_entidade_atualizar_observacao(self, test_session):
        """Testa o método de domínio atualizar_observacao através do fluxo completo"""
        # Arrange
        repository = DevolucaoRepositoryImpl(test_session)
        create_use_case = CreateDevolucaoUseCase(repository)
        get_use_case = GetDevolucaoByIdUseCase(repository)
        update_use_case = UpdateDevolucaoUseCase(repository)

        devolucao = criar_devolucao(observacao="Observação original do item")
        devolucao_criada = await create_use_case.execute(devolucao)

        # Usa o método de domínio
        devolucao_criada.atualizar_observacao("Nova observação após verificação")
        assert devolucao_criada.observacao == "Nova observação após verificação"

        # Persiste a atualização
        devolucao_atualizada = await update_use_case.execute(devolucao_criada.id, devolucao_criada)

        # Verifica no banco
        devolucao_do_banco = await get_use_case.execute(devolucao_criada.id)

        # Assert
        assert devolucao_atualizada.observacao == "Nova observação após verificação"
        assert devolucao_do_banco.observacao == "Nova observação após verificação"

    async def test_fluxo_contar_total_de_devolucoes(self, test_session):
        """Testa contagem de devoluções através do fluxo completo"""
        # Arrange
        repository = DevolucaoRepositoryImpl(test_session)
        create_use_case = CreateDevolucaoUseCase(repository)
        count_use_case = CountDevolucoesUseCase(repository)

        for i in range(4):
            await create_use_case.execute(
                criar_devolucao(reclamante_id=i + 1, item_id=i + 1, observacao=f"Devolução {i}")
            )

        # Act
        total = await count_use_case.execute()

        # Assert
        assert total == 4

    async def test_fluxo_buscar_devolucao_inexistente_retorna_none(self, test_session):
        """Testa que buscar devolução inexistente retorna None no fluxo completo"""
        # Arrange
        repository = DevolucaoRepositoryImpl(test_session)
        get_use_case = GetDevolucaoByIdUseCase(repository)

        # Act
        resultado = await get_use_case.execute(9999)

        # Assert
        assert resultado is None

    async def test_fluxo_deletar_devolucao_inexistente(self, test_session):
        """Testa que deletar devolução inexistente retorna False"""
        # Arrange
        repository = DevolucaoRepositoryImpl(test_session)
        delete_use_case = DeleteDevolucaoUseCase(repository)

        # Act
        resultado = await delete_use_case.execute(9999)

        # Assert
        assert resultado is False

    async def test_fluxo_data_futura_ao_criar_falha(self, test_session):
        """Testa que criar devolução com data futura falha"""
        # Arrange
        repository = DevolucaoRepositoryImpl(test_session)
        create_use_case = CreateDevolucaoUseCase(repository)

        devolucao_futura = criar_devolucao(
            data_devolucao=datetime.now() + timedelta(days=2),
            observacao="Tentativa inválida"
        )

        # Act & Assert
        with pytest.raises(ValueError, match="Data da devolução não pode ser no futuro"):
            await create_use_case.execute(devolucao_futura)
