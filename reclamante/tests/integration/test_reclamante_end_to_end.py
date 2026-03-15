"""
Testes de integração end-to-end para o fluxo completo de Reclamante
Testa a integração entre Use Cases, Repository e Database
"""
import pytest
from reclamante.src.domain.entities.reclamante import Reclamante
from reclamante.src.application.use_cases.reclamante_use_cases import (
    CreateReclamanteUseCase,
    GetReclamanteByIdUseCase,
    GetAllReclamantesUseCase,
    UpdateReclamanteUseCase,
    DeleteReclamanteUseCase,
)
from reclamante.src.infrastructure.repositories.reclamante_repository_impl import ReclamanteRepositoryImpl


def criar_reclamante(**kwargs) -> Reclamante:
    """Helper para criar reclamante de teste"""
    dados = {
        "nome": "Reclamante Teste",
        "documento": "12345678900",
        "telefone": "11987654321",
    }
    dados.update(kwargs)
    return Reclamante(**dados)


@pytest.mark.asyncio
class TestReclamanteEndToEnd:
    """Testes end-to-end do fluxo completo de Reclamante"""

    async def test_fluxo_completo_criar_buscar_atualizar_deletar(self, test_session):
        """Testa o fluxo completo: criar -> buscar -> atualizar -> deletar"""
        # Arrange
        repository = ReclamanteRepositoryImpl(test_session)
        create_use_case = CreateReclamanteUseCase(repository)
        get_use_case = GetReclamanteByIdUseCase(repository)
        update_use_case = UpdateReclamanteUseCase(repository)
        delete_use_case = DeleteReclamanteUseCase(repository)

        # 1. Criar
        reclamante_criado = await create_use_case.execute(
            criar_reclamante(nome="Fluxo Completo", documento="12345678900")
        )

        # Assert criação
        assert reclamante_criado.id is not None
        assert reclamante_criado.nome == "Fluxo Completo"

        # 2. Buscar
        reclamante_encontrado = await get_use_case.execute(reclamante_criado.id)

        # Assert busca
        assert reclamante_encontrado is not None
        assert reclamante_encontrado.id == reclamante_criado.id

        # 3. Atualizar
        reclamante_para_atualizar = criar_reclamante(
            nome="Fluxo Atualizado",
            documento="12345678900",
            telefone="11999998888",
        )

        reclamante_atualizado = await update_use_case.execute(
            reclamante_criado.id,
            reclamante_para_atualizar,
        )

        # Assert atualização
        assert reclamante_atualizado is not None
        assert reclamante_atualizado.nome == "Fluxo Atualizado"
        assert reclamante_atualizado.telefone == "11999998888"

        # 4. Deletar
        resultado_delete = await delete_use_case.execute(reclamante_criado.id)
        reclamante_deletado = await get_use_case.execute(reclamante_criado.id)

        # Assert deleção
        assert resultado_delete is True
        assert reclamante_deletado is None

    async def test_fluxo_listar_com_paginacao(self, test_session):
        """Testa listagem de reclamantes com paginação"""
        # Arrange
        repository = ReclamanteRepositoryImpl(test_session)
        create_use_case = CreateReclamanteUseCase(repository)
        list_use_case = GetAllReclamantesUseCase(repository)

        for i in range(15):
            await create_use_case.execute(
                criar_reclamante(
                    nome=f"Paginacao {i}",
                    documento=f"DOC{i:03d}",
                    telefone=f"1199000{i:04d}",
                )
            )

        # Act
        primeira_pagina = await list_use_case.execute(skip=0, limit=10)
        segunda_pagina = await list_use_case.execute(skip=10, limit=10)

        # Assert
        assert len(primeira_pagina) == 10
        assert len(segunda_pagina) == 5
        assert primeira_pagina[0].id != segunda_pagina[0].id

    async def test_fluxo_validacao_id_invalido_na_busca(self, test_session):
        """Testa validação de ID inválido na busca por ID"""
        # Arrange
        repository = ReclamanteRepositoryImpl(test_session)
        get_use_case = GetReclamanteByIdUseCase(repository)

        # Act & Assert
        with pytest.raises(ValueError, match="ID de reclamante deve ser maior que zero"):
            await get_use_case.execute(0)

        with pytest.raises(ValueError, match="ID de reclamante deve ser maior que zero"):
            await get_use_case.execute(-3)

    async def test_fluxo_skip_negativo_na_listagem(self, test_session):
        """Testa validação de skip negativo na listagem"""
        # Arrange
        repository = ReclamanteRepositoryImpl(test_session)
        list_use_case = GetAllReclamantesUseCase(repository)

        # Act & Assert
        with pytest.raises(ValueError, match="Skip não pode ser negativo"):
            await list_use_case.execute(skip=-1)

    async def test_fluxo_limit_invalido_na_listagem(self, test_session):
        """Testa validação de limit inválido na listagem"""
        # Arrange
        repository = ReclamanteRepositoryImpl(test_session)
        list_use_case = GetAllReclamantesUseCase(repository)

        # Act & Assert
        with pytest.raises(ValueError, match="Limit deve estar entre 1 e 1000"):
            await list_use_case.execute(limit=0)

        with pytest.raises(ValueError, match="Limit deve estar entre 1 e 1000"):
            await list_use_case.execute(limit=1001)

    async def test_fluxo_buscar_reclamante_inexistente_retorna_none(self, test_session):
        """Testa busca de reclamante inexistente"""
        # Arrange
        repository = ReclamanteRepositoryImpl(test_session)
        get_use_case = GetReclamanteByIdUseCase(repository)

        # Act
        resultado = await get_use_case.execute(9999)

        # Assert
        assert resultado is None

    async def test_fluxo_atualizar_reclamante_inexistente_retorna_none(self, test_session):
        """Testa atualização de reclamante inexistente"""
        # Arrange
        repository = ReclamanteRepositoryImpl(test_session)
        update_use_case = UpdateReclamanteUseCase(repository)

        # Act
        resultado = await update_use_case.execute(9999, criar_reclamante(nome="Inexistente"))

        # Assert
        assert resultado is None

    async def test_fluxo_deletar_reclamante_inexistente_retorna_false(self, test_session):
        """Testa exclusão de reclamante inexistente"""
        # Arrange
        repository = ReclamanteRepositoryImpl(test_session)
        delete_use_case = DeleteReclamanteUseCase(repository)

        # Act
        resultado = await delete_use_case.execute(9999)

        # Assert
        assert resultado is False

    async def test_fluxo_contar_total_de_reclamantes(self, test_session):
        """Testa contagem total no fluxo de integração"""
        # Arrange
        repository = ReclamanteRepositoryImpl(test_session)
        create_use_case = CreateReclamanteUseCase(repository)

        for i in range(4):
            await create_use_case.execute(
                criar_reclamante(
                    nome=f"Count {i}",
                    documento=f"DOC{i}",
                    telefone=f"TEL{i}",
                )
            )

        # Act
        total = await repository.count()

        # Assert
        assert total == 4
