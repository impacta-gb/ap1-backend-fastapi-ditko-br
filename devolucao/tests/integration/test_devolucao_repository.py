"""
Testes de integração para o repositório de Devolucao
"""
import pytest
from datetime import datetime, timedelta
from devolucao.src.domain.entities.devolucao import Devolucao
from devolucao.src.infrastructure.repositories.devolucao_repository_impl import DevolucaoRepositoryImpl


def criar_devolucao(**kwargs) -> Devolucao:
    """Helper para criar uma devolução para testes"""
    dados = {
        "reclamante_id": 1,
        "item_id": 2,
        "observacao": "Item devolvido ao proprietário",
        "data_devolucao": datetime.now() - timedelta(hours=1),
    }
    dados.update(kwargs)
    return Devolucao(**dados)


@pytest.mark.asyncio
class TestDevolucaoRepositoryImpl:
    """Testes de integração para DevolucaoRepositoryImpl"""

    async def test_criar_devolucao(self, test_session):
        """Testa criação de devolução no banco de dados"""
        # Arrange
        repository = DevolucaoRepositoryImpl(test_session)
        devolucao = criar_devolucao()

        # Act
        devolucao_criada = await repository.create(devolucao)

        # Assert
        assert devolucao_criada.id is not None
        assert devolucao_criada.reclamante_id == 1
        assert devolucao_criada.item_id == 2
        assert devolucao_criada.observacao == "Item devolvido ao proprietário"
        assert devolucao_criada.created_at is not None

    async def test_buscar_devolucao_por_id(self, test_session):
        """Testa busca de devolução por ID"""
        # Arrange
        repository = DevolucaoRepositoryImpl(test_session)
        devolucao = criar_devolucao(observacao="Encontrado na recepção")
        devolucao_criada = await repository.create(devolucao)

        # Act
        encontrada = await repository.get_by_id(devolucao_criada.id)

        # Assert
        assert encontrada is not None
        assert encontrada.id == devolucao_criada.id
        assert encontrada.observacao == "Encontrado na recepção"

    async def test_buscar_devolucao_por_id_inexistente(self, test_session):
        """Testa busca de devolução que não existe"""
        # Arrange
        repository = DevolucaoRepositoryImpl(test_session)

        # Act
        resultado = await repository.get_by_id(9999)

        # Assert
        assert resultado is None

    async def test_listar_todas_devolucoes(self, test_session):
        """Testa listagem de todas as devoluções"""
        # Arrange
        repository = DevolucaoRepositoryImpl(test_session)

        for i in range(5):
            await repository.create(
                criar_devolucao(
                    reclamante_id=i + 1,
                    item_id=i + 1,
                    observacao=f"Devolução {i + 1}"
                )
            )

        # Act
        devolucoes = await repository.get_all()

        # Assert
        assert len(devolucoes) == 5
        assert all(d.id is not None for d in devolucoes)

    async def test_listar_devolucoes_com_paginacao(self, test_session):
        """Testa listagem de devoluções com paginação"""
        # Arrange
        repository = DevolucaoRepositoryImpl(test_session)

        for i in range(10):
            await repository.create(
                criar_devolucao(
                    reclamante_id=i + 1,
                    item_id=i + 1,
                    observacao=f"Devolução {i + 1}"
                )
            )

        # Act
        primeira_pagina = await repository.get_all(skip=0, limit=5)
        segunda_pagina = await repository.get_all(skip=5, limit=5)

        # Assert
        assert len(primeira_pagina) == 5
        assert len(segunda_pagina) == 5
        assert primeira_pagina[0].id != segunda_pagina[0].id

    async def test_atualizar_devolucao(self, test_session):
        """Testa atualização de devolução"""
        # Arrange
        repository = DevolucaoRepositoryImpl(test_session)
        devolucao = criar_devolucao(observacao="Observação original")
        devolucao_criada = await repository.create(devolucao)

        # Cria entidade com dados atualizados
        devolucao_atualizada = criar_devolucao(observacao="Observação atualizada")

        # Act
        resultado = await repository.update(devolucao_criada.id, devolucao_atualizada)

        # Assert
        assert resultado is not None
        assert resultado.observacao == "Observação atualizada"
        assert resultado.id == devolucao_criada.id

    async def test_atualizar_devolucao_inexistente(self, test_session):
        """Testa atualização de devolução inexistente"""
        # Arrange
        repository = DevolucaoRepositoryImpl(test_session)
        devolucao = criar_devolucao()

        # Act
        resultado = await repository.update(9999, devolucao)

        # Assert
        assert resultado is None

    async def test_deletar_devolucao(self, test_session):
        """Testa deleção de devolução"""
        # Arrange
        repository = DevolucaoRepositoryImpl(test_session)
        devolucao = criar_devolucao()
        devolucao_criada = await repository.create(devolucao)

        # Act
        deletado = await repository.delete(devolucao_criada.id)
        buscado = await repository.get_by_id(devolucao_criada.id)

        # Assert
        assert deletado is True
        assert buscado is None

    async def test_deletar_devolucao_inexistente(self, test_session):
        """Testa deleção de devolução inexistente"""
        # Arrange
        repository = DevolucaoRepositoryImpl(test_session)

        # Act
        resultado = await repository.delete(9999)

        # Assert
        assert resultado is False

    async def test_buscar_por_data(self, test_session):
        """Testa busca de devoluções por data"""
        # Arrange
        repository = DevolucaoRepositoryImpl(test_session)
        data_alvo = datetime(2024, 6, 15, 10, 0, 0)
        data_outra = datetime(2024, 7, 20, 12, 0, 0)

        await repository.create(criar_devolucao(data_devolucao=data_alvo, observacao="D1"))
        await repository.create(criar_devolucao(data_devolucao=data_alvo, observacao="D2"))
        await repository.create(criar_devolucao(data_devolucao=data_outra, observacao="D3"))

        # Act
        resultado = await repository.get_by_data(data_alvo)

        # Assert
        assert len(resultado) == 2
        for d in resultado:
            assert d.data_devolucao.date() == data_alvo.date()

    async def test_contar_total_devolucoes(self, test_session):
        """Testa contagem total de devoluções"""
        # Arrange
        repository = DevolucaoRepositoryImpl(test_session)

        for i in range(4):
            await repository.create(criar_devolucao(reclamante_id=i + 1, item_id=i + 1))

        # Act
        total = await repository.count()

        # Assert
        assert total == 4

    async def test_remover_item_da_projecao(self, test_session):
        """Testa remoção de item da projeção de referência."""
        repository = DevolucaoRepositoryImpl(test_session)

        await repository.upsert_item_reference(
            item_id=42,
            local_id=1,
            responsavel_id=1,
            status="disponivel",
        )
        assert await repository.exists_item(42) is True

        await repository.delete_item_reference(42)

        assert await repository.exists_item(42) is False

    async def test_conversao_model_to_entity(self, test_session):
        """Testa que a conversão model→entity preserva todos os campos"""
        # Arrange
        repository = DevolucaoRepositoryImpl(test_session)
        data_especifica = datetime(2024, 3, 10, 14, 30, 0)
        devolucao = criar_devolucao(
            reclamante_id=7,
            item_id=13,
            observacao="Conversão completa",
            data_devolucao=data_especifica
        )

        # Act
        criada = await repository.create(devolucao)

        # Assert
        assert criada.reclamante_id == 7
        assert criada.item_id == 13
        assert criada.observacao == "Conversão completa"
        assert criada.data_devolucao == data_especifica
        assert criada.id is not None
        assert criada.created_at is not None
