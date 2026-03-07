"""
Testes de integração para o repositório de Local
"""
import pytest
from local.src.domain.entities.local import Local
from local.src.infrastructure.repositories.local_repository_impl import LocalRepositoryImpl


@pytest.mark.asyncio
class TestLocalRepositoryImpl:
    """Testes de integração para LocalRepositoryImpl"""

    async def test_criar_local(self, test_session):
        """Testa criação de local no banco de dados"""
        # Arrange
        repository = LocalRepositoryImpl(test_session)

        local = Local(
            tipo="Metrô",
            descricao="Estação Sé - Plataforma Central",
            bairro="Centro"
        )

        # Act
        local_criado = await repository.create(local)

        # Assert
        assert local_criado.id is not None
        assert local_criado.tipo == "Metrô"
        assert local_criado.descricao == "Estação Sé - Plataforma Central"
        assert local_criado.bairro == "Centro"
        assert local_criado.created_at is not None

    async def test_buscar_local_por_id(self, test_session):
        """Testa busca de local por ID"""
        # Arrange
        repository = LocalRepositoryImpl(test_session)

        local = Local(
            tipo="Ônibus",
            descricao="Terminal Rodoviário Central",
            bairro="Brás"
        )

        local_criado = await repository.create(local)

        # Act
        local_encontrado = await repository.get_by_id(local_criado.id)

        # Assert
        assert local_encontrado is not None
        assert local_encontrado.id == local_criado.id
        assert local_encontrado.tipo == "Ônibus"
        assert local_encontrado.bairro == "Brás"

    async def test_buscar_local_por_id_inexistente(self, test_session):
        """Testa busca de local que não existe"""
        # Arrange
        repository = LocalRepositoryImpl(test_session)

        # Act
        local_encontrado = await repository.get_by_id(9999)

        # Assert
        assert local_encontrado is None

    async def test_listar_todos_locais(self, test_session):
        """Testa listagem de todos os locais"""
        # Arrange
        repository = LocalRepositoryImpl(test_session)

        locais_para_criar = [
            Local(tipo=f"Tipo {i}", descricao=f"Descrição {i}", bairro=f"Bairro {i}")
            for i in range(5)
        ]

        for local in locais_para_criar:
            await repository.create(local)

        # Act
        locais_listados = await repository.get_all()

        # Assert
        assert len(locais_listados) == 5
        assert all(l.id is not None for l in locais_listados)

    async def test_listar_locais_com_paginacao(self, test_session):
        """Testa listagem de locais com paginação"""
        # Arrange
        repository = LocalRepositoryImpl(test_session)

        for i in range(10):
            await repository.create(
                Local(tipo=f"Tipo {i}", descricao=f"Descrição {i}", bairro=f"Bairro {i}")
            )

        # Act
        primeira_pagina = await repository.get_all(skip=0, limit=5)
        segunda_pagina = await repository.get_all(skip=5, limit=5)

        # Assert
        assert len(primeira_pagina) == 5
        assert len(segunda_pagina) == 5
        assert primeira_pagina[0].id != segunda_pagina[0].id

    async def test_atualizar_local(self, test_session):
        """Testa atualização de local"""
        # Arrange
        repository = LocalRepositoryImpl(test_session)

        local = Local(
            tipo="Tipo Original",
            descricao="Descrição Original",
            bairro="Bairro Original"
        )

        local_criado = await repository.create(local)

        # Modifica o local
        local_criado.tipo = "Tipo Atualizado"
        local_criado.descricao = "Descrição Atualizada"
        local_criado.bairro = "Bairro Atualizado"

        # Act
        local_atualizado = await repository.update(local_criado.id, local_criado)

        # Assert
        assert local_atualizado is not None
        assert local_atualizado.id == local_criado.id
        assert local_atualizado.tipo == "Tipo Atualizado"
        assert local_atualizado.descricao == "Descrição Atualizada"
        assert local_atualizado.bairro == "Bairro Atualizado"

    async def test_atualizar_local_inexistente(self, test_session):
        """Testa atualização de local que não existe"""
        # Arrange
        repository = LocalRepositoryImpl(test_session)

        local = Local(
            tipo="Metrô",
            descricao="Descrição Teste",
            bairro="Centro"
        )

        # Act
        resultado = await repository.update(9999, local)

        # Assert
        assert resultado is None

    async def test_deletar_local(self, test_session):
        """Testa exclusão de local"""
        # Arrange
        repository = LocalRepositoryImpl(test_session)

        local = Local(
            tipo="Parque",
            descricao="Parque para deletar",
            bairro="Moema"
        )

        local_criado = await repository.create(local)
        local_id = local_criado.id

        # Act
        resultado = await repository.delete(local_id)
        local_apos_delete = await repository.get_by_id(local_id)

        # Assert
        assert resultado is True
        assert local_apos_delete is None

    async def test_deletar_local_inexistente(self, test_session):
        """Testa exclusão de local que não existe"""
        # Arrange
        repository = LocalRepositoryImpl(test_session)

        # Act
        resultado = await repository.delete(9999)

        # Assert
        assert resultado is False

    async def test_buscar_por_bairro(self, test_session):
        """Testa busca de locais por bairro"""
        # Arrange
        repository = LocalRepositoryImpl(test_session)

        await repository.create(Local(tipo="Metrô", descricao="Estação A", bairro="Centro"))
        await repository.create(Local(tipo="Ônibus", descricao="Terminal B", bairro="Centro"))
        await repository.create(Local(tipo="Parque", descricao="Parque C", bairro="Moema"))

        # Act
        locais_no_centro = await repository.get_by_bairro("Centro")
        locais_em_moema = await repository.get_by_bairro("Moema")

        # Assert
        assert len(locais_no_centro) == 2
        assert len(locais_em_moema) == 1
        assert all(l.bairro == "Centro" for l in locais_no_centro)

    async def test_contar_total_de_locais(self, test_session):
        """Testa método count do repositório"""
        # Arrange
        repository = LocalRepositoryImpl(test_session)

        for i in range(3):
            await repository.create(
                Local(tipo=f"Tipo {i}", descricao=f"Descrição {i}", bairro=f"Bairro {i}")
            )

        # Act
        total = await repository.count()

        # Assert
        assert total == 3

    async def test_conversao_model_to_entity(self, test_session):
        """Testa conversão correta de Model ORM para Entity de domínio"""
        # Arrange
        repository = LocalRepositoryImpl(test_session)

        local = Local(
            tipo="Shopping",
            descricao="Shopping Center Norte - Piso 2",
            bairro="Vila Guilherme"
        )

        # Act
        local_criado = await repository.create(local)

        # Assert - Verifica campos básicos da conversão
        assert isinstance(local_criado, Local)
        assert local_criado.id is not None
        assert local_criado.tipo == "Shopping"
        assert local_criado.descricao == "Shopping Center Norte - Piso 2"
        assert local_criado.bairro == "Vila Guilherme"
        assert local_criado.created_at is not None
