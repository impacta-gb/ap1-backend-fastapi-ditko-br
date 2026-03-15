"""
Testes de integração para o repositório de Item
"""
import pytest
from datetime import datetime, timedelta
from item.src.domain.entities.item import Item
from item.src.infrastructure.repositories.item_repository_impl import ItemRepositoryImpl


@pytest.mark.asyncio
class TestItemRepositoryImpl:
    """Testes de integração para ItemRepositoryImpl"""
    
    async def test_criar_item(self, test_session):
        """Testa criação de item no banco de dados"""
        # Arrange
        repository = ItemRepositoryImpl(test_session)
        data_encontro = datetime.now() - timedelta(days=1)
        
        item = Item(
            nome="Celular iPhone",
            categoria="Eletrônicos",
            data_encontro=data_encontro,
            descricao="iPhone 12 Pro azul",
            status="disponivel",
            local_id=1,
            responsavel_id=1
        )
        
        # Act
        item_criado = await repository.create(item)
        
        # Assert
        assert item_criado.id is not None
        assert item_criado.nome == "Celular iPhone"
        assert item_criado.categoria == "Eletrônicos"
        assert item_criado.status == "disponivel"
        assert item_criado.created_at is not None
    
    async def test_buscar_item_por_id(self, test_session):
        """Testa busca de item por ID"""
        # Arrange
        repository = ItemRepositoryImpl(test_session)
        
        item = Item(
            nome="Carteira",
            categoria="Documentos",
            data_encontro=datetime.now(),
            descricao="Carteira de couro preta",
            status="disponivel",
            local_id=1,
            responsavel_id=1
        )
        
        item_criado = await repository.create(item)
        
        # Act
        item_encontrado = await repository.get_by_id(item_criado.id)
        
        # Assert
        assert item_encontrado is not None
        assert item_encontrado.id == item_criado.id
        assert item_encontrado.nome == "Carteira"
        assert item_encontrado.categoria == "Documentos"
    
    async def test_buscar_item_por_id_inexistente(self, test_session):
        """Testa busca de item que não existe"""
        # Arrange
        repository = ItemRepositoryImpl(test_session)
        
        # Act
        item_encontrado = await repository.get_by_id(9999)
        
        # Assert
        assert item_encontrado is None
    
    async def test_listar_todos_itens(self, test_session):
        """Testa listagem de todos os itens"""
        # Arrange
        repository = ItemRepositoryImpl(test_session)
        
        # Cria múltiplos itens
        items_para_criar = [
            Item(
                nome=f"Item {i}",
                categoria="Teste",
                data_encontro=datetime.now(),
                descricao=f"Descrição item {i}",
                status="disponivel",
                local_id=1,
                responsavel_id=1
            )
            for i in range(5)
        ]
        
        for item in items_para_criar:
            await repository.create(item)
        
        # Act
        items_listados = await repository.get_all()
        
        # Assert
        assert len(items_listados) == 5
        assert all(item.id is not None for item in items_listados)
    
    async def test_listar_itens_com_paginacao(self, test_session):
        """Testa listagem de itens com paginação"""
        # Arrange
        repository = ItemRepositoryImpl(test_session)
        
        # Cria 10 itens
        for i in range(10):
            item = Item(
                nome=f"Item {i}",
                categoria="Teste",
                data_encontro=datetime.now(),
                descricao=f"Descrição item {i}",
                status="disponivel",
                local_id=1,
                responsavel_id=1
            )
            await repository.create(item)
        
        # Act
        primeira_pagina = await repository.get_all(skip=0, limit=5)
        segunda_pagina = await repository.get_all(skip=5, limit=5)
        
        # Assert
        assert len(primeira_pagina) == 5
        assert len(segunda_pagina) == 5
        assert primeira_pagina[0].id != segunda_pagina[0].id
    
    async def test_atualizar_item(self, test_session):
        """Testa atualização de item"""
        # Arrange
        repository = ItemRepositoryImpl(test_session)
        
        item = Item(
            nome="Nome original",
            categoria="Categoria original",
            data_encontro=datetime.now(),
            descricao="Descrição original",
            status="disponivel",
            local_id=1,
            responsavel_id=1
        )
        
        item_criado = await repository.create(item)
        
        # Modifica o item
        item_criado.nome = "Nome atualizado"
        item_criado.descricao = "Descrição atualizada"
        item_criado.status = "em_analise"
        
        # Act
        item_atualizado = await repository.update(item_criado.id, item_criado)
        
        # Assert
        assert item_atualizado is not None
        assert item_atualizado.id == item_criado.id
        assert item_atualizado.nome == "Nome atualizado"
        assert item_atualizado.descricao == "Descrição atualizada"
        assert item_atualizado.status == "em_analise"
        assert item_atualizado.updated_at is not None
    
    async def test_atualizar_item_inexistente(self, test_session):
        """Testa atualização de item que não existe"""
        # Arrange
        repository = ItemRepositoryImpl(test_session)
        
        item = Item(
            nome="Item teste",
            categoria="Teste",
            data_encontro=datetime.now(),
            descricao="Descrição teste",
            status="disponivel",
            local_id=1,
            responsavel_id=1
        )
        
        # Act
        resultado = await repository.update(9999, item)
        
        # Assert
        assert resultado is None
    
    async def test_deletar_item(self, test_session):
        """Testa exclusão de item"""
        # Arrange
        repository = ItemRepositoryImpl(test_session)
        
        item = Item(
            nome="Item para deletar",
            categoria="Teste",
            data_encontro=datetime.now(),
            descricao="Este item será deletado",
            status="disponivel",
            local_id=1,
            responsavel_id=1
        )
        
        item_criado = await repository.create(item)
        item_id = item_criado.id
        
        # Act
        resultado = await repository.delete(item_id)
        item_deletado = await repository.get_by_id(item_id)
        
        # Assert
        assert resultado is True
        assert item_deletado is None
    
    async def test_deletar_item_inexistente(self, test_session):
        """Testa exclusão de item que não existe"""
        # Arrange
        repository = ItemRepositoryImpl(test_session)
        
        # Act
        resultado = await repository.delete(9999)
        
        # Assert
        assert resultado is False
    
    async def test_buscar_por_categoria(self, test_session):
        """Testa busca de itens por categoria"""
        # Arrange
        repository = ItemRepositoryImpl(test_session)
        
        # Cria itens de diferentes categorias
        categorias = ["Eletrônicos", "Documentos", "Eletrônicos", "Vestuário", "Eletrônicos"]
        
        for i, categoria in enumerate(categorias):
            item = Item(
                nome=f"Item {i}",
                categoria=categoria,
                data_encontro=datetime.now(),
                descricao=f"Descrição {i}",
                status="disponivel",
                local_id=1,
                responsavel_id=1
            )
            await repository.create(item)
        
        # Act
        itens_eletronicos = await repository.get_by_categoria("Eletrônicos")
        itens_documentos = await repository.get_by_categoria("Documentos")
        
        # Assert
        assert len(itens_eletronicos) == 3
        assert len(itens_documentos) == 1
        assert all(item.categoria == "Eletrônicos" for item in itens_eletronicos)
        assert all(item.categoria == "Documentos" for item in itens_documentos)
    
    async def test_buscar_por_status(self, test_session):
        """Testa busca de itens por status"""
        # Arrange
        repository = ItemRepositoryImpl(test_session)
        
        # Cria itens com diferentes status
        status_list = ["disponivel", "devolvido", "disponivel", "em_analise", "disponivel"]
        
        for i, status in enumerate(status_list):
            item = Item(
                nome=f"Item {i}",
                categoria="Teste",
                data_encontro=datetime.now(),
                descricao=f"Descrição {i}",
                status=status,
                local_id=1,
                responsavel_id=1
            )
            await repository.create(item)
        
        # Act
        itens_disponiveis = await repository.get_by_status("disponivel")
        itens_devolvidos = await repository.get_by_status("devolvido")
        itens_em_analise = await repository.get_by_status("em_analise")
        
        # Assert
        assert len(itens_disponiveis) == 3
        assert len(itens_devolvidos) == 1
        assert len(itens_em_analise) == 1
        assert all(item.status == "disponivel" for item in itens_disponiveis)
    
    async def test_contar_total_de_itens(self, test_session):
        """Testa contagem total de itens"""
        # Arrange
        repository = ItemRepositoryImpl(test_session)
        
        # Cria 7 itens
        for i in range(7):
            item = Item(
                nome=f"Item {i}",
                categoria="Teste",
                data_encontro=datetime.now(),
                descricao=f"Descrição {i}",
                status="disponivel",
                local_id=1,
                responsavel_id=1
            )
            await repository.create(item)
        
        # Act
        total = await repository.count()
        
        # Assert
        assert total == 7
    
    async def test_conversao_model_to_entity(self, test_session):
        """Testa que a conversão de model para entity preserva todos os campos"""
        # Arrange
        repository = ItemRepositoryImpl(test_session)
        data_encontro = datetime.now() - timedelta(days=2)
        
        item = Item(
            nome="Teste conversão",
            categoria="Teste",
            data_encontro=data_encontro,
            descricao="Testando conversão de tipos",
            status="disponivel",
            local_id=5,
            responsavel_id=10
        )
        
        # Act
        item_criado = await repository.create(item)
        item_recuperado = await repository.get_by_id(item_criado.id)
        
        # Assert
        assert item_recuperado.nome == item.nome
        assert item_recuperado.categoria == item.categoria
        assert item_recuperado.descricao == item.descricao
        assert item_recuperado.status == item.status
        assert item_recuperado.local_id == item.local_id
        assert item_recuperado.responsavel_id == item.responsavel_id
        # Timestamps devem existir
        assert item_recuperado.created_at is not None
