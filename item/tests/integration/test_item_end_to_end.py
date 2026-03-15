"""
Testes de integração end-to-end para o fluxo completo de Item
Testa a integração entre Use Cases, Repository e Database
"""
import pytest
from datetime import datetime, timedelta
from item.src.domain.entities.item import Item
from item.src.application.use_cases.item_use_cases import (
    CreateItemUseCase,
    GetItemByIdUseCase,
    GetAllItemsUseCase,
    UpdateItemUseCase,
    DeleteItemUseCase,
    GetItemsByCategoriaUseCase,
    GetItemsByStatusUseCase
)
from item.src.infrastructure.repositories.item_repository_impl import ItemRepositoryImpl


@pytest.mark.asyncio
class TestItemEndToEnd:
    """Testes end-to-end do fluxo completo de Item"""
    
    async def test_fluxo_completo_criar_buscar_atualizar_deletar(self, test_session):
        """Testa o fluxo completo: criar -> buscar -> atualizar -> deletar"""
        # Arrange
        repository = ItemRepositoryImpl(test_session)
        create_use_case = CreateItemUseCase(repository)
        get_use_case = GetItemByIdUseCase(repository)
        update_use_case = UpdateItemUseCase(repository)
        delete_use_case = DeleteItemUseCase(repository)
        
        # 1. CRIAR ITEM
        item_para_criar = Item(
            nome="Notebook Dell",
            categoria="Eletrônicos",
            data_encontro=datetime.now() - timedelta(days=1),
            descricao="Notebook Dell Inspiron 15 preto",
            status="em_analise",  # Será mudado para disponivel pelo use case
            local_id=1,
            responsavel_id=1
        )
        
        item_criado = await create_use_case.execute(item_para_criar)
        
        # Assert criar
        assert item_criado.id is not None
        assert item_criado.status == "disponivel"  # Use case garante status inicial
        assert item_criado.nome == "Notebook Dell"
        
        # 2. BUSCAR ITEM
        item_encontrado = await get_use_case.execute(item_criado.id)
        
        # Assert buscar
        assert item_encontrado is not None
        assert item_encontrado.id == item_criado.id
        assert item_encontrado.nome == "Notebook Dell"
        
        # 3. ATUALIZAR ITEM
        item_encontrado.descricao = "Notebook Dell Inspiron 15 preto - COM CARREGADOR"
        item_encontrado.status = "em_analise"
        
        item_atualizado = await update_use_case.execute(item_encontrado.id, item_encontrado)
        
        # Assert atualizar
        assert item_atualizado is not None
        assert item_atualizado.descricao == "Notebook Dell Inspiron 15 preto - COM CARREGADOR"
        assert item_atualizado.status == "em_analise"
        
        # 4. DELETAR ITEM
        resultado_delete = await delete_use_case.execute(item_atualizado.id)
        item_deletado = await get_use_case.execute(item_atualizado.id)
        
        # Assert deletar
        assert resultado_delete is True
        assert item_deletado is None
    
    async def test_fluxo_nao_pode_deletar_item_devolvido(self, test_session):
        """Testa que não é possível deletar item já devolvido"""
        # Arrange
        repository = ItemRepositoryImpl(test_session)
        
        item = Item(
            nome="Item teste",
            categoria="Teste",
            data_encontro=datetime.now() - timedelta(days=1),
            descricao="Item que será devolvido",
            status="disponivel",
            local_id=1,
            responsavel_id=1
        )
        
        item_criado = await repository.create(item)
        
        # Marca como devolvido através da entidade
        item_criado.marcar_como_devolvido()
        await repository.update(item_criado.id, item_criado)
        
        # Act & Assert
        delete_use_case = DeleteItemUseCase(repository)
        
        with pytest.raises(ValueError, match="Não é permitido deletar itens já devolvidos"):
            await delete_use_case.execute(item_criado.id)
    
    async def test_fluxo_listar_com_paginacao(self, test_session):
        """Testa listagem com paginação"""
        # Arrange
        repository = ItemRepositoryImpl(test_session)
        create_use_case = CreateItemUseCase(repository)
        list_use_case = GetAllItemsUseCase(repository)
        
        # Cria 15 itens
        for i in range(15):
            item = Item(
                nome=f"Item {i}",
                categoria="Teste",
                data_encontro=datetime.now() - timedelta(days=1),
                descricao=f"Descrição do item {i}",
                status="disponivel",
                local_id=1,
                responsavel_id=1
            )
            await create_use_case.execute(item)
        
        # Act
        primeira_pagina = await list_use_case.execute(skip=0, limit=10)
        segunda_pagina = await list_use_case.execute(skip=10, limit=10)
        
        # Assert
        assert len(primeira_pagina) == 10
        assert len(segunda_pagina) == 5
        assert primeira_pagina[0].id != segunda_pagina[0].id
    
    async def test_fluxo_buscar_por_categoria(self, test_session):
        """Testa busca de itens por categoria"""
        # Arrange
        repository = ItemRepositoryImpl(test_session)
        create_use_case = CreateItemUseCase(repository)
        buscar_categoria_use_case = GetItemsByCategoriaUseCase(repository)
        
        # Cria itens de diferentes categorias
        categorias_itens = [
            ("Celular Samsung", "Eletrônicos"),
            ("Notebook HP", "Eletrônicos"),
            ("Carteira", "Documentos"),
            ("Mochila", "Vestuário"),
            ("Tablet Apple", "Eletrônicos"),
        ]
        
        for nome, categoria in categorias_itens:
            item = Item(
                nome=nome,
                categoria=categoria,
                data_encontro=datetime.now() - timedelta(days=1),
                descricao=f"Descrição de {nome}",
                status="disponivel",
                local_id=1,
                responsavel_id=1
            )
            await create_use_case.execute(item)
        
        # Act
        itens_eletronicos = await buscar_categoria_use_case.execute("Eletrônicos")
        itens_documentos = await buscar_categoria_use_case.execute("Documentos")
        itens_vestuario = await buscar_categoria_use_case.execute("Vestuário")
        
        # Assert
        assert len(itens_eletronicos) == 3
        assert len(itens_documentos) == 1
        assert len(itens_vestuario) == 1
        assert all(item.categoria == "Eletrônicos" for item in itens_eletronicos)
    
    async def test_fluxo_buscar_por_status(self, test_session):
        """Testa busca de itens por status"""
        # Arrange
        repository = ItemRepositoryImpl(test_session)
        create_use_case = CreateItemUseCase(repository)
        update_use_case = UpdateItemUseCase(repository)
        buscar_status_use_case = GetItemsByStatusUseCase(repository)
        
        # Cria 5 itens (todos começam como disponivel)
        items_criados = []
        for i in range(5):
            item = Item(
                nome=f"Item {i}",
                categoria="Teste",
                data_encontro=datetime.now() - timedelta(days=1),
                descricao=f"Descrição {i}",
                status="disponivel",
                local_id=1,
                responsavel_id=1
            )
            item_criado = await create_use_case.execute(item)
            items_criados.append(item_criado)
        
        # Atualiza alguns itens para diferentes status
        items_criados[1].status = "em_analise"
        await update_use_case.execute(items_criados[1].id, items_criados[1])
        
        items_criados[3].status = "em_analise"
        await update_use_case.execute(items_criados[3].id, items_criados[3])
        
        # Marca um como devolvido usando o método da entidade
        items_criados[4].marcar_como_devolvido()
        await repository.update(items_criados[4].id, items_criados[4])
        
        # Act
        itens_disponiveis = await buscar_status_use_case.execute("disponivel")
        itens_em_analise = await buscar_status_use_case.execute("em_analise")
        itens_devolvidos = await buscar_status_use_case.execute("devolvido")
        
        # Assert
        assert len(itens_disponiveis) == 2  # Items 0 e 2
        assert len(itens_em_analise) == 2   # Items 1 e 3
        assert len(itens_devolvidos) == 1   # Item 4
    
    async def test_fluxo_validacao_data_futura_na_criacao(self, test_session):
        """Testa que não é possível criar item com data futura"""
        # Arrange
        repository = ItemRepositoryImpl(test_session)
        create_use_case = CreateItemUseCase(repository)
        
        item = Item(
            nome="Item teste",
            categoria="Teste",
            data_encontro=datetime.now() + timedelta(days=1),  # Data futura
            descricao="Item com data futura",
            status="disponivel",
            local_id=1,
            responsavel_id=1
        )
        
        # Act & Assert
        with pytest.raises(ValueError, match="Data de encontro não pode ser no futuro"):
            await create_use_case.execute(item)
        
        # Verifica que nenhum item foi criado
        all_items = await repository.get_all()
        assert len(all_items) == 0
    
    async def test_fluxo_validacao_ids_invalidos(self, test_session):
        """Testa validação de IDs de local e responsável"""
        # Arrange
        repository = ItemRepositoryImpl(test_session)
        create_use_case = CreateItemUseCase(repository)
        
        # Testa local_id inválido
        item_local_invalido = Item(
            nome="Item teste",
            categoria="Teste",
            data_encontro=datetime.now() - timedelta(days=1),
            descricao="Item com local_id inválido",
            status="disponivel",
            local_id=0,  # ID inválido
            responsavel_id=1
        )
        
        with pytest.raises(ValueError, match="ID do local deve ser maior que zero"):
            await create_use_case.execute(item_local_invalido)
        
        # Testa responsavel_id inválido
        item_responsavel_invalido = Item(
            nome="Item teste",
            categoria="Teste",
            data_encontro=datetime.now() - timedelta(days=1),
            descricao="Item com responsavel_id inválido",
            status="disponivel",
            local_id=1,
            responsavel_id=-5  # ID inválido
        )
        
        with pytest.raises(ValueError, match="ID do responsável deve ser maior que zero"):
            await create_use_case.execute(item_responsavel_invalido)
    
    async def test_fluxo_metodo_entidade_marcar_como_devolvido(self, test_session):
        """Testa o fluxo de marcar item como devolvido usando método da entidade"""
        # Arrange
        repository = ItemRepositoryImpl(test_session)
        create_use_case = CreateItemUseCase(repository)
        get_use_case = GetItemByIdUseCase(repository)
        
        # Cria item
        item = Item(
            nome="Item para devolução",
            categoria="Teste",
            data_encontro=datetime.now() - timedelta(days=1),
            descricao="Item que será devolvido",
            status="disponivel",
            local_id=1,
            responsavel_id=1
        )
        
        item_criado = await create_use_case.execute(item)
        
        # Act - Busca item, marca como devolvido e salva
        item_para_devolver = await get_use_case.execute(item_criado.id)
        assert item_para_devolver.status == "disponivel"
        
        item_para_devolver.marcar_como_devolvido()
        await repository.update(item_para_devolver.id, item_para_devolver)
        
        # Busca novamente para confirmar
        item_devolvido = await get_use_case.execute(item_criado.id)
        
        # Assert
        assert item_devolvido.status == "devolvido"
    
    async def test_fluxo_metodo_entidade_atualizar_descricao(self, test_session):
        """Testa o fluxo de atualizar descrição usando método da entidade"""
        # Arrange
        repository = ItemRepositoryImpl(test_session)
        create_use_case = CreateItemUseCase(repository)
        get_use_case = GetItemByIdUseCase(repository)
        
        # Cria item
        item = Item(
            nome="Item teste",
            categoria="Teste",
            data_encontro=datetime.now() - timedelta(days=1),
            descricao="Descrição original",
            status="disponivel",
            local_id=1,
            responsavel_id=1
        )
        
        item_criado = await create_use_case.execute(item)
        
        # Act - Busca item, atualiza descrição e salva
        item_para_atualizar = await get_use_case.execute(item_criado.id)
        nova_descricao = "Descrição atualizada com mais detalhes"
        item_para_atualizar.atualizar_descricao(nova_descricao)
        
        await repository.update(item_para_atualizar.id, item_para_atualizar)
        
        # Busca novamente para confirmar
        item_atualizado = await get_use_case.execute(item_criado.id)
        
        # Assert
        assert item_atualizado.descricao == nova_descricao
    
    async def test_fluxo_contar_total_de_itens(self, test_session):
        """Testa contagem total após várias operações"""
        # Arrange
        repository = ItemRepositoryImpl(test_session)
        create_use_case = CreateItemUseCase(repository)
        delete_use_case = DeleteItemUseCase(repository)
        
        # Cria 10 itens
        items_criados = []
        for i in range(10):
            item = Item(
                nome=f"Item {i}",
                categoria="Teste",
                data_encontro=datetime.now() - timedelta(days=1),
                descricao=f"Descrição {i}",
                status="disponivel",
                local_id=1,
                responsavel_id=1
            )
            item_criado = await create_use_case.execute(item)
            items_criados.append(item_criado)
        
        # Verifica contagem inicial
        total = await repository.count()
        assert total == 10
        
        # Deleta 3 itens
        await delete_use_case.execute(items_criados[0].id)
        await delete_use_case.execute(items_criados[1].id)
        await delete_use_case.execute(items_criados[2].id)
        
        # Verifica contagem final
        total_final = await repository.count()
        assert total_final == 7
