"""
Testes de integração para o repositório de Reclamante
"""
import pytest
from reclamante.src.domain.entities.reclamante import Reclamante
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
class TestReclamanteRepositoryImpl:
    """Testes de integração para ReclamanteRepositoryImpl"""

    async def test_criar_reclamante(self, test_session):
        """Testa criação de reclamante no banco de dados"""
        # Arrange
        repository = ReclamanteRepositoryImpl(test_session)

        # Act
        reclamante_criado = await repository.create(
            criar_reclamante(nome="Repo Test", documento="555", telefone="444")
        )

        # Assert
        assert reclamante_criado.id is not None
        assert reclamante_criado.nome == "Repo Test"
        assert reclamante_criado.documento == "555"
        assert reclamante_criado.telefone == "444"

    async def test_buscar_reclamante_por_id(self, test_session):
        """Testa busca de reclamante por ID"""
        # Arrange
        repository = ReclamanteRepositoryImpl(test_session)
        reclamante_criado = await repository.create(
            criar_reclamante(nome="Get Test", documento="666", telefone="333")
        )

        # Act
        encontrado = await repository.get_by_id(reclamante_criado.id)

        # Assert
        assert encontrado is not None
        assert encontrado.id == reclamante_criado.id
        assert encontrado.nome == "Get Test"
        assert encontrado.documento == "666"

    async def test_buscar_reclamante_por_id_inexistente(self, test_session):
        """Testa busca por ID inexistente"""
        # Arrange
        repository = ReclamanteRepositoryImpl(test_session)

        # Act
        encontrado = await repository.get_by_id(9999)

        # Assert
        assert encontrado is None

    async def test_listar_todos_reclamantes(self, test_session):
        """Testa listagem de todos os reclamantes"""
        # Arrange
        repository = ReclamanteRepositoryImpl(test_session)
        await repository.create(criar_reclamante(nome="List Test 1", documento="777", telefone="222"))
        await repository.create(criar_reclamante(nome="List Test 2", documento="888", telefone="111"))

        # Act
        reclamantes = await repository.get_all(0, 10)

        # Assert
        assert len(reclamantes) == 2
        assert reclamantes[0].nome == "List Test 1"
        assert reclamantes[1].nome == "List Test 2"

    async def test_listar_reclamantes_com_paginacao(self, test_session):
        """Testa listagem com paginação"""
        # Arrange
        repository = ReclamanteRepositoryImpl(test_session)

        for i in range(6):
            await repository.create(
                criar_reclamante(
                    nome=f"Pag {i}",
                    documento=f"D{i}",
                    telefone=f"11{i}",
                )
            )

        # Act
        primeira_pagina = await repository.get_all(skip=0, limit=3)
        segunda_pagina = await repository.get_all(skip=3, limit=3)

        # Assert
        assert len(primeira_pagina) == 3
        assert len(segunda_pagina) == 3
        assert primeira_pagina[0].id != segunda_pagina[0].id

    async def test_atualizar_reclamante(self, test_session):
        """Testa atualização de reclamante"""
        # Arrange
        repository = ReclamanteRepositoryImpl(test_session)
        reclamante_criado = await repository.create(
            criar_reclamante(nome="Update Old", documento="999", telefone="000")
        )

        reclamante_atualizado = criar_reclamante(
            nome="Update New",
            documento="999",
            telefone="123",
        )

        # Act
        resultado = await repository.update(reclamante_criado.id, reclamante_atualizado)

        # Assert
        assert resultado is not None
        assert resultado.nome == "Update New"
        assert resultado.telefone == "123"

    async def test_atualizar_reclamante_inexistente(self, test_session):
        """Testa atualização de reclamante inexistente"""
        # Arrange
        repository = ReclamanteRepositoryImpl(test_session)

        # Act
        resultado = await repository.update(9999, criar_reclamante(nome="X"))

        # Assert
        assert resultado is None

    async def test_deletar_reclamante(self, test_session):
        """Testa exclusão de reclamante"""
        # Arrange
        repository = ReclamanteRepositoryImpl(test_session)
        reclamante_criado = await repository.create(
            criar_reclamante(nome="Delete Test", documento="101", telefone="212")
        )

        # Act
        deletado = await repository.delete(reclamante_criado.id)
        buscado = await repository.get_by_id(reclamante_criado.id)

        # Assert
        assert deletado is True
        assert buscado is None

    async def test_deletar_reclamante_inexistente(self, test_session):
        """Testa exclusão de reclamante inexistente"""
        # Arrange
        repository = ReclamanteRepositoryImpl(test_session)

        # Act
        resultado = await repository.delete(9999)

        # Assert
        assert resultado is False

    async def test_contar_total_de_reclamantes(self, test_session):
        """Testa contagem total de reclamantes"""
        # Arrange
        repository = ReclamanteRepositoryImpl(test_session)
        for i in range(4):
            await repository.create(
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

    async def test_contagem_reflete_delete(self, test_session):
        """Testa que a contagem é atualizada após exclusão"""
        # Arrange
        repository = ReclamanteRepositoryImpl(test_session)
        primeiro = await repository.create(criar_reclamante(nome="A", documento="A", telefone="A"))
        await repository.create(criar_reclamante(nome="B", documento="B", telefone="B"))

        # Act
        total_antes = await repository.count()
        await repository.delete(primeiro.id)
        total_depois = await repository.count()

        # Assert
        assert total_antes == 2
        assert total_depois == 1

    async def test_conversao_model_para_entidade_preserva_campos(self, test_session):
        """Testa conversão model->entidade de forma indireta"""
        # Arrange
        repository = ReclamanteRepositoryImpl(test_session)
        criado = await repository.create(
            criar_reclamante(nome="Conversao", documento="DOC-1", telefone="11912345678")
        )

        # Act
        encontrado = await repository.get_by_id(criado.id)

        # Assert
        assert encontrado is not None
        assert encontrado.id == criado.id
        assert encontrado.nome == "Conversao"
        assert encontrado.documento == "DOC-1"
        assert encontrado.telefone == "11912345678"
