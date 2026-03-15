"""
Testes unitários para os casos de uso de Item
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock
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


class TestCreateItemUseCase:
    """Testes para o caso de uso de criação de item"""
    
    @pytest.mark.asyncio
    async def test_criar_item_com_sucesso(self):
        """Testa criação de item com dados válidos"""
        # Arrange
        repository_mock = AsyncMock()
        data_encontro = datetime.now() - timedelta(days=1)
        
        item = Item(
            nome="Celular Samsung",
            categoria="Eletrônicos",
            data_encontro=data_encontro,
            descricao="Celular Samsung Galaxy preto",
            status="disponivel",
            local_id=1,
            responsavel_id=1
        )
        
        item_criado = Item(
            id=1,
            nome="Celular Samsung",
            categoria="Eletrônicos",
            data_encontro=data_encontro,
            descricao="Celular Samsung Galaxy preto",
            status="disponivel",
            local_id=1,
            responsavel_id=1,
            created_at=datetime.now()
        )
        
        repository_mock.create.return_value = item_criado
        use_case = CreateItemUseCase(repository_mock)
        
        # Act
        resultado = await use_case.execute(item)
        
        # Assert
        assert resultado.id == 1
        assert resultado.status == "disponivel"
        repository_mock.create.assert_called_once_with(item)
    
    @pytest.mark.asyncio
    async def test_criar_item_com_data_futura(self):
        """Testa que não é possível criar item com data de encontro futura"""
        # Arrange
        repository_mock = AsyncMock()
        data_futura = datetime.now() + timedelta(days=1)
        
        item = Item(
            nome="Item teste",
            categoria="Teste",
            data_encontro=data_futura,
            descricao="Descrição teste",
            status="disponivel",
            local_id=1,
            responsavel_id=1
        )
        
        use_case = CreateItemUseCase(repository_mock)
        
        # Act & Assert
        with pytest.raises(ValueError, match="Data de encontro não pode ser no futuro"):
            await use_case.execute(item)
        
        repository_mock.create.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_criar_item_com_local_id_invalido(self):
        """Testa que não é possível criar item com local_id <= 0"""
        # Arrange
        repository_mock = AsyncMock()
        
        item = Item(
            nome="Item teste",
            categoria="Teste",
            data_encontro=datetime.now(),
            descricao="Descrição teste",
            status="disponivel",
            local_id=0,  # ID inválido
            responsavel_id=1
        )
        
        use_case = CreateItemUseCase(repository_mock)
        
        # Act & Assert
        with pytest.raises(ValueError, match="ID do local deve ser maior que zero"):
            await use_case.execute(item)
        
        repository_mock.create.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_criar_item_com_responsavel_id_invalido(self):
        """Testa que não é possível criar item com responsavel_id <= 0"""
        # Arrange
        repository_mock = AsyncMock()
        
        item = Item(
            nome="Item teste",
            categoria="Teste",
            data_encontro=datetime.now(),
            descricao="Descrição teste",
            status="disponivel",
            local_id=1,
            responsavel_id=-1  # ID inválido
        )
        
        use_case = CreateItemUseCase(repository_mock)
        
        # Act & Assert
        with pytest.raises(ValueError, match="ID do responsável deve ser maior que zero"):
            await use_case.execute(item)
        
        repository_mock.create.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_criar_item_sempre_define_status_como_disponivel(self):
        """Testa que o use case sempre define status como 'disponivel'"""
        # Arrange
        repository_mock = AsyncMock()
        
        # Tentar criar item com status diferente
        item = Item(
            nome="Item teste",
            categoria="Teste",
            data_encontro=datetime.now() - timedelta(days=1),
            descricao="Descrição teste",
            status="em_analise",  # Tento passar status diferente
            local_id=1,
            responsavel_id=1
        )
        
        item_criado = Item(
            id=1,
            nome="Item teste",
            categoria="Teste",
            data_encontro=datetime.now() - timedelta(days=1),
            descricao="Descrição teste",
            status="disponivel",
            local_id=1,
            responsavel_id=1,
            created_at=datetime.now()
        )
        
        repository_mock.create.return_value = item_criado
        use_case = CreateItemUseCase(repository_mock)
        
        # Act
        resultado = await use_case.execute(item)
        
        # Assert - O use case deve ter mudado o status para disponivel
        assert item.status == "disponivel"
        assert resultado.status == "disponivel"


class TestGetItemByIdUseCase:
    """Testes para o caso de uso de busca de item por ID"""
    
    @pytest.mark.asyncio
    async def test_buscar_item_existente(self):
        """Testa busca de item que existe"""
        # Arrange
        repository_mock = AsyncMock()
        item = Item(
            id=1,
            nome="Item teste",
            categoria="Teste",
            data_encontro=datetime.now(),
            descricao="Descrição teste",
            status="disponivel",
            local_id=1,
            responsavel_id=1
        )
        
        repository_mock.get_by_id.return_value = item
        use_case = GetItemByIdUseCase(repository_mock)
        
        # Act
        resultado = await use_case.execute(1)
        
        # Assert
        assert resultado is not None
        assert resultado.id == 1
        repository_mock.get_by_id.assert_called_once_with(1)
    
    @pytest.mark.asyncio
    async def test_buscar_item_inexistente(self):
        """Testa busca de item que não existe"""
        # Arrange
        repository_mock = AsyncMock()
        repository_mock.get_by_id.return_value = None
        use_case = GetItemByIdUseCase(repository_mock)
        
        # Act
        resultado = await use_case.execute(999)
        
        # Assert
        assert resultado is None
        repository_mock.get_by_id.assert_called_once_with(999)
    
    @pytest.mark.asyncio
    async def test_buscar_item_com_id_invalido(self):
        """Testa que não é possível buscar item com ID <= 0"""
        # Arrange
        repository_mock = AsyncMock()
        use_case = GetItemByIdUseCase(repository_mock)
        
        # Act & Assert
        with pytest.raises(ValueError, match="ID do item deve ser maior que zero"):
            await use_case.execute(0)
        
        repository_mock.get_by_id.assert_not_called()


class TestGetAllItemsUseCase:
    """Testes para o caso de uso de listagem de todos os itens"""
    
    @pytest.mark.asyncio
    async def test_listar_todos_itens(self):
        """Testa listagem de itens com paginação padrão"""
        # Arrange
        repository_mock = AsyncMock()
        items = [
            Item(id=1, nome="Item 1", categoria="Cat1", data_encontro=datetime.now(),
                 descricao="Desc 1", status="disponivel", local_id=1, responsavel_id=1),
            Item(id=2, nome="Item 2", categoria="Cat2", data_encontro=datetime.now(),
                 descricao="Desc 2", status="disponivel", local_id=1, responsavel_id=1),
        ]
        
        repository_mock.get_all.return_value = items
        use_case = GetAllItemsUseCase(repository_mock)
        
        # Act
        resultado = await use_case.execute()
        
        # Assert
        assert len(resultado) == 2
        repository_mock.get_all.assert_called_once_with(0, 100)
    
    @pytest.mark.asyncio
    async def test_listar_itens_com_paginacao_customizada(self):
        """Testa listagem de itens com paginação customizada"""
        # Arrange
        repository_mock = AsyncMock()
        repository_mock.get_all.return_value = []
        use_case = GetAllItemsUseCase(repository_mock)
        
        # Act
        await use_case.execute(skip=10, limit=50)
        
        # Assert
        repository_mock.get_all.assert_called_once_with(10, 50)
    
    @pytest.mark.asyncio
    async def test_listar_itens_com_skip_negativo(self):
        """Testa que não é possível usar skip negativo"""
        # Arrange
        repository_mock = AsyncMock()
        use_case = GetAllItemsUseCase(repository_mock)
        
        # Act & Assert
        with pytest.raises(ValueError, match="Skip não pode ser negativo"):
            await use_case.execute(skip=-1)
        
        repository_mock.get_all.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_listar_itens_com_limit_zero(self):
        """Testa que não é possível usar limit <= 0"""
        # Arrange
        repository_mock = AsyncMock()
        use_case = GetAllItemsUseCase(repository_mock)
        
        # Act & Assert
        with pytest.raises(ValueError, match="Limit deve estar entre 1 e 1000"):
            await use_case.execute(limit=0)
        
        repository_mock.get_all.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_listar_itens_com_limit_maior_que_1000(self):
        """Testa que não é possível usar limit > 1000"""
        # Arrange
        repository_mock = AsyncMock()
        use_case = GetAllItemsUseCase(repository_mock)
        
        # Act & Assert
        with pytest.raises(ValueError, match="Limit deve estar entre 1 e 1000"):
            await use_case.execute(limit=1001)
        
        repository_mock.get_all.assert_not_called()


class TestUpdateItemUseCase:
    """Testes para o caso de uso de atualização de item"""
    
    @pytest.mark.asyncio
    async def test_atualizar_item_com_sucesso(self):
        """Testa atualização de item com dados válidos"""
        # Arrange
        repository_mock = AsyncMock()
        
        item_existente = Item(
            id=1,
            nome="Item original",
            categoria="Categoria original",
            data_encontro=datetime.now() - timedelta(days=2),
            descricao="Descrição original",
            status="disponivel",
            local_id=1,
            responsavel_id=1
        )
        
        item_atualizado = Item(
            nome="Item atualizado",
            categoria="Nova categoria",
            data_encontro=datetime.now() - timedelta(days=1),
            descricao="Nova descrição",
            status="disponivel",
            local_id=1,
            responsavel_id=1
        )
        
        repository_mock.get_by_id.return_value = item_existente
        repository_mock.update.return_value = item_atualizado
        use_case = UpdateItemUseCase(repository_mock)
        
        # Act
        resultado = await use_case.execute(1, item_atualizado)
        
        # Assert
        assert resultado is not None
        repository_mock.get_by_id.assert_called_once_with(1)
        repository_mock.update.assert_called_once_with(1, item_atualizado)
    
    @pytest.mark.asyncio
    async def test_atualizar_item_inexistente(self):
        """Testa atualização de item que não existe"""
        # Arrange
        repository_mock = AsyncMock()
        repository_mock.get_by_id.return_value = None
        use_case = UpdateItemUseCase(repository_mock)
        
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
        resultado = await use_case.execute(999, item)
        
        # Assert
        assert resultado is None
        repository_mock.update.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_atualizar_item_nao_pode_marcar_como_devolvido_diretamente(self):
        """Testa que não é possível marcar item como devolvido pelo update"""
        # Arrange
        repository_mock = AsyncMock()
        
        item_existente = Item(
            id=1,
            nome="Item teste",
            categoria="Teste",
            data_encontro=datetime.now(),
            descricao="Descrição teste",
            status="disponivel",  # Status atual: disponivel
            local_id=1,
            responsavel_id=1
        )
        
        item_para_atualizar = Item(
            nome="Item teste",
            categoria="Teste",
            data_encontro=datetime.now(),
            descricao="Descrição teste",
            status="devolvido",  # Tentando mudar para devolvido
            local_id=1,
            responsavel_id=1
        )
        
        repository_mock.get_by_id.return_value = item_existente
        use_case = UpdateItemUseCase(repository_mock)
        
        # Act & Assert
        with pytest.raises(ValueError, match="Para marcar um item como devolvido"):
            await use_case.execute(1, item_para_atualizar)
        
        repository_mock.update.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_atualizar_item_com_data_futura(self):
        """Testa que não é possível atualizar item com data futura"""
        # Arrange
        repository_mock = AsyncMock()
        
        item_existente = Item(
            id=1,
            nome="Item teste",
            categoria="Teste",
            data_encontro=datetime.now() - timedelta(days=1),
            descricao="Descrição teste",
            status="disponivel",
            local_id=1,
            responsavel_id=1
        )
        
        item_para_atualizar = Item(
            nome="Item teste",
            categoria="Teste",
            data_encontro=datetime.now() + timedelta(days=1),  # Data futura
            descricao="Descrição teste",
            status="disponivel",
            local_id=1,
            responsavel_id=1
        )
        
        repository_mock.get_by_id.return_value = item_existente
        use_case = UpdateItemUseCase(repository_mock)
        
        # Act & Assert
        with pytest.raises(ValueError, match="Data de encontro não pode ser no futuro"):
            await use_case.execute(1, item_para_atualizar)
        
        repository_mock.update.assert_not_called()


class TestDeleteItemUseCase:
    """Testes para o caso de uso de exclusão de item"""
    
    @pytest.mark.asyncio
    async def test_deletar_item_disponivel(self):
        """Testa exclusão de item com status disponivel"""
        # Arrange
        repository_mock = AsyncMock()
        
        item = Item(
            id=1,
            nome="Item teste",
            categoria="Teste",
            data_encontro=datetime.now(),
            descricao="Descrição teste",
            status="disponivel",
            local_id=1,
            responsavel_id=1
        )
        
        repository_mock.get_by_id.return_value = item
        repository_mock.delete.return_value = True
        use_case = DeleteItemUseCase(repository_mock)
        
        # Act
        resultado = await use_case.execute(1)
        
        # Assert
        assert resultado is True
        repository_mock.delete.assert_called_once_with(1)
    
    @pytest.mark.asyncio
    async def test_deletar_item_inexistente(self):
        """Testa exclusão de item que não existe"""
        # Arrange
        repository_mock = AsyncMock()
        repository_mock.get_by_id.return_value = None
        use_case = DeleteItemUseCase(repository_mock)
        
        # Act
        resultado = await use_case.execute(999)
        
        # Assert
        assert resultado is False
        repository_mock.delete.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_deletar_item_devolvido_nao_permitido(self):
        """Testa que não é possível deletar item já devolvido"""
        # Arrange
        repository_mock = AsyncMock()
        
        item = Item(
            id=1,
            nome="Item teste",
            categoria="Teste",
            data_encontro=datetime.now(),
            descricao="Descrição teste",
            status="devolvido",  # Item já devolvido
            local_id=1,
            responsavel_id=1
        )
        
        repository_mock.get_by_id.return_value = item
        use_case = DeleteItemUseCase(repository_mock)
        
        # Act & Assert
        with pytest.raises(ValueError, match="Não é permitido deletar itens já devolvidos"):
            await use_case.execute(1)
        
        repository_mock.delete.assert_not_called()


class TestGetItemsByCategoriaUseCase:
    """Testes para o caso de uso de busca de itens por categoria"""
    
    @pytest.mark.asyncio
    async def test_buscar_por_categoria(self):
        """Testa busca de itens por categoria"""
        # Arrange
        repository_mock = AsyncMock()
        items = [
            Item(id=1, nome="Item 1", categoria="Eletrônicos", data_encontro=datetime.now(),
                 descricao="Desc 1", status="disponivel", local_id=1, responsavel_id=1),
            Item(id=2, nome="Item 2", categoria="Eletrônicos", data_encontro=datetime.now(),
                 descricao="Desc 2", status="disponivel", local_id=1, responsavel_id=1),
        ]
        
        repository_mock.get_by_categoria.return_value = items
        use_case = GetItemsByCategoriaUseCase(repository_mock)
        
        # Act
        resultado = await use_case.execute("Eletrônicos")
        
        # Assert
        assert len(resultado) == 2
        repository_mock.get_by_categoria.assert_called_once_with("Eletrônicos")
    
    @pytest.mark.asyncio
    async def test_buscar_por_categoria_vazia(self):
        """Testa que não é possível buscar por categoria vazia"""
        # Arrange
        repository_mock = AsyncMock()
        use_case = GetItemsByCategoriaUseCase(repository_mock)
        
        # Act & Assert
        with pytest.raises(ValueError, match="Categoria não pode estar vazia"):
            await use_case.execute("")
        
        repository_mock.get_by_categoria.assert_not_called()


class TestGetItemsByStatusUseCase:
    """Testes para o caso de uso de busca de itens por status"""
    
    @pytest.mark.asyncio
    async def test_buscar_por_status_disponivel(self):
        """Testa busca de itens por status disponivel"""
        # Arrange
        repository_mock = AsyncMock()
        items = [
            Item(id=1, nome="Item 1", categoria="Cat1", data_encontro=datetime.now(),
                 descricao="Desc 1", status="disponivel", local_id=1, responsavel_id=1),
        ]
        
        repository_mock.get_by_status.return_value = items
        use_case = GetItemsByStatusUseCase(repository_mock)
        
        # Act
        resultado = await use_case.execute("disponivel")
        
        # Assert
        assert len(resultado) == 1
        repository_mock.get_by_status.assert_called_once_with("disponivel")
    
    @pytest.mark.asyncio
    async def test_buscar_por_status_invalido(self):
        """Testa que não é possível buscar por status inválido"""
        # Arrange
        repository_mock = AsyncMock()
        use_case = GetItemsByStatusUseCase(repository_mock)
        
        # Act & Assert
        with pytest.raises(ValueError, match="Status .* inválido"):
            await use_case.execute("status_invalido")
        
        repository_mock.get_by_status.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_buscar_por_status_com_acento_normalizado(self):
        """Testa busca de status com acentuação sendo normalizada"""
        # Arrange
        repository_mock = AsyncMock()
        repository_mock.get_by_status.return_value = []
        use_case = GetItemsByStatusUseCase(repository_mock)
        
        # Act
        await use_case.execute("disponível")  # Com acento
        
        # Assert - O use case deve normalizar antes de validar
        repository_mock.get_by_status.assert_called_once()
