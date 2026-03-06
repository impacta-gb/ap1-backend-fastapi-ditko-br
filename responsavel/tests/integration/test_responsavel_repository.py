"""
Testes de integração para o repositório de Responsavel
"""
import pytest
from responsavel.src.domain.entities.responsavel import Responsavel
from responsavel.src.infrastructure.repositories.responsavel_repository_impl import ResponsavelRepositoryImpl


@pytest.mark.asyncio
class TestResponsavelRepositoryImpl:
    """Testes de integração para ResponsavelRepositoryImpl"""

    async def test_criar_responsavel(self, test_session):
        """Testa criação de responsável no banco de dados"""
        # Arrange
        repository = ResponsavelRepositoryImpl(test_session)

        responsavel = Responsavel(
            nome="João Silva",
            cargo="Segurança",
            telefone="11999999999",
            ativo=True
        )

        # Act
        responsavel_criado = await repository.create(responsavel)

        # Assert
        assert responsavel_criado.id is not None
        assert responsavel_criado.nome == "João Silva"
        assert responsavel_criado.cargo == "Segurança"
        assert responsavel_criado.telefone == "11999999999"
        assert responsavel_criado.ativo is True

    async def test_buscar_responsavel_por_id(self, test_session):
        """Testa busca de responsável por ID"""
        # Arrange
        repository = ResponsavelRepositoryImpl(test_session)

        responsavel = Responsavel(
            nome="Maria Souza",
            cargo="Recepcionista",
            telefone="11988888888",
            ativo=True
        )

        responsavel_criado = await repository.create(responsavel)

        # Act
        responsavel_encontrado = await repository.get_by_id(responsavel_criado.id)

        # Assert
        assert responsavel_encontrado is not None
        assert responsavel_encontrado.id == responsavel_criado.id
        assert responsavel_encontrado.nome == "Maria Souza"
        assert responsavel_encontrado.cargo == "Recepcionista"

    async def test_buscar_responsavel_por_id_inexistente(self, test_session):
        """Testa busca de responsável que não existe"""
        # Arrange
        repository = ResponsavelRepositoryImpl(test_session)

        # Act
        responsavel_encontrado = await repository.get_by_id(9999)

        # Assert
        assert responsavel_encontrado is None

    async def test_listar_todos_responsaveis(self, test_session):
        """Testa listagem de todos os responsáveis"""
        # Arrange
        repository = ResponsavelRepositoryImpl(test_session)

        # Cria múltiplos responsáveis
        responsaveis_para_criar = [
            Responsavel(
                nome=f"Responsavel {i}",
                cargo="Cargo Teste",
                telefone=f"1199999{i:04d}",
                ativo=True
            )
            for i in range(5)
        ]

        for responsavel in responsaveis_para_criar:
            await repository.create(responsavel)

        # Act
        responsaveis_listados = await repository.get_all()

        # Assert
        assert len(responsaveis_listados) == 5
        assert all(r.id is not None for r in responsaveis_listados)

    async def test_listar_responsaveis_com_paginacao(self, test_session):
        """Testa listagem de responsáveis com paginação"""
        # Arrange
        repository = ResponsavelRepositoryImpl(test_session)

        # Cria 10 responsáveis
        for i in range(10):
            responsavel = Responsavel(
                nome=f"Responsavel {i}",
                cargo="Cargo Teste",
                telefone=f"1199999{i:04d}",
                ativo=True
            )
            await repository.create(responsavel)

        # Act
        primeira_pagina = await repository.get_all(skip=0, limit=5)
        segunda_pagina = await repository.get_all(skip=5, limit=5)

        # Assert
        assert len(primeira_pagina) == 5
        assert len(segunda_pagina) == 5
        assert primeira_pagina[0].id != segunda_pagina[0].id

    async def test_atualizar_responsavel(self, test_session):
        """Testa atualização de responsável"""
        # Arrange
        repository = ResponsavelRepositoryImpl(test_session)

        responsavel = Responsavel(
            nome="Nome Original",
            cargo="Cargo Original",
            telefone="11999999999",
            ativo=True
        )

        responsavel_criado = await repository.create(responsavel)

        # Modifica o responsável
        responsavel_criado.nome = "Nome Atualizado"
        responsavel_criado.cargo = "Cargo Atualizado"

        # Act
        responsavel_atualizado = await repository.update(responsavel_criado.id, responsavel_criado)

        # Assert
        assert responsavel_atualizado is not None
        assert responsavel_atualizado.id == responsavel_criado.id
        assert responsavel_atualizado.nome == "Nome Atualizado"
        assert responsavel_atualizado.cargo == "Cargo Atualizado"

    async def test_atualizar_responsavel_inexistente(self, test_session):
        """Testa atualização de responsável que não existe"""
        # Arrange
        repository = ResponsavelRepositoryImpl(test_session)

        responsavel = Responsavel(
            nome="Responsavel Teste",
            cargo="Cargo Teste",
            telefone="11999999999",
            ativo=True
        )

        # Act
        resultado = await repository.update(9999, responsavel)

        # Assert
        assert resultado is None

    async def test_deletar_responsavel(self, test_session):
        """Testa exclusão de responsável"""
        # Arrange
        repository = ResponsavelRepositoryImpl(test_session)

        responsavel = Responsavel(
            nome="Responsavel Para Deletar",
            cargo="Cargo Teste",
            telefone="11999999999",
            ativo=True
        )

        responsavel_criado = await repository.create(responsavel)
        responsavel_id = responsavel_criado.id

        # Act
        resultado = await repository.delete(responsavel_id)
        responsavel_deletado = await repository.get_by_id(responsavel_id)

        # Assert
        assert resultado is True
        assert responsavel_deletado is None

    async def test_deletar_responsavel_inexistente(self, test_session):
        """Testa exclusão de responsável que não existe"""
        # Arrange
        repository = ResponsavelRepositoryImpl(test_session)

        # Act
        resultado = await repository.delete(9999)

        # Assert
        assert resultado is False

    async def test_buscar_por_ativo_true(self, test_session):
        """Testa busca de responsáveis ativos"""
        # Arrange
        repository = ResponsavelRepositoryImpl(test_session)

        # Cria responsáveis ativos e inativos
        responsaveis_dados = [
            ("João", True),
            ("Maria", True),
            ("Carlos", False),
            ("Ana", True),
            ("Pedro", False),
        ]

        for nome, ativo in responsaveis_dados:
            responsavel = Responsavel(
                nome=nome,
                cargo="Cargo Teste",
                telefone="11999999999",
                ativo=ativo
            )
            await repository.create(responsavel)

        # Act
        ativos = await repository.get_by_ativo(True)
        inativos = await repository.get_by_ativo(False)

        # Assert
        assert len(ativos) == 3
        assert len(inativos) == 2
        assert all(r.ativo is True for r in ativos)
        assert all(r.ativo is False for r in inativos)

    async def test_contar_total_de_responsaveis(self, test_session):
        """Testa contagem total de responsáveis"""
        # Arrange
        repository = ResponsavelRepositoryImpl(test_session)

        # Cria 4 responsáveis
        for i in range(4):
            responsavel = Responsavel(
                nome=f"Responsavel {i}",
                cargo="Cargo Teste",
                telefone=f"1199999{i:04d}",
                ativo=True
            )
            await repository.create(responsavel)

        # Act
        total = await repository.count()

        # Assert
        assert total == 4

    async def test_conversao_model_to_entity(self, test_session):
        """Testa que a conversão de model para entity preserva todos os campos"""
        # Arrange
        repository = ResponsavelRepositoryImpl(test_session)

        responsavel = Responsavel(
            nome="Teste Conversão",
            cargo="Auditor",
            telefone="21988887777",
            ativo=True
        )

        # Act
        responsavel_criado = await repository.create(responsavel)
        responsavel_recuperado = await repository.get_by_id(responsavel_criado.id)

        # Assert
        assert responsavel_recuperado.nome == responsavel.nome
        assert responsavel_recuperado.cargo == responsavel.cargo
        assert responsavel_recuperado.telefone == responsavel.telefone
        assert responsavel_recuperado.ativo == responsavel.ativo

    async def test_desativar_responsavel_via_update(self, test_session):
        """Testa desativação de responsável via update"""
        # Arrange
        repository = ResponsavelRepositoryImpl(test_session)

        responsavel = Responsavel(
            nome="João Silva",
            cargo="Segurança",
            telefone="11999999999",
            ativo=True
        )

        responsavel_criado = await repository.create(responsavel)
        assert responsavel_criado.ativo is True

        # Desativa usando o método da entidade
        responsavel_criado.desativar_responsavel()
        responsavel_atualizado = await repository.update(responsavel_criado.id, responsavel_criado)

        # Act
        responsavel_recuperado = await repository.get_by_id(responsavel_criado.id)

        # Assert
        assert responsavel_atualizado.ativo is False
        assert responsavel_recuperado.ativo is False
