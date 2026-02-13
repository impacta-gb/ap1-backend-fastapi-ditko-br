from typing import List, Optional
from src.domain.entities.item import Item
from src.domain.repositories.item_repository import ItemRepository


class CreateItemUseCase:
    """Caso de uso para criar um novo item"""
    
    def __init__(self, repository: ItemRepository):
        self.repository = repository
    
    async def execute(self, item: Item) -> Item:
        """Executa a criação de um novo item"""
        return await self.repository.create(item)


class GetItemByIdUseCase:
    """Caso de uso para buscar um item por ID"""
    
    def __init__(self, repository: ItemRepository):
        self.repository = repository
    
    async def execute(self, item_id: int) -> Optional[Item]:
        """Executa a busca de um item por ID"""
        return await self.repository.get_by_id(item_id)


class GetAllItemsUseCase:
    """Caso de uso para listar todos os itens"""
    
    def __init__(self, repository: ItemRepository):
        self.repository = repository
    
    async def execute(self, skip: int = 0, limit: int = 100) -> List[Item]:
        """Executa a listagem de todos os itens"""
        return await self.repository.get_all(skip, limit)


class UpdateItemUseCase:
    """Caso de uso para atualizar um item"""
    
    def __init__(self, repository: ItemRepository):
        self.repository = repository
    
    async def execute(self, item_id: int, item: Item) -> Optional[Item]:
        """Executa a atualização de um item"""
        return await self.repository.update(item_id, item)


class DeleteItemUseCase:
    """Caso de uso para deletar um item"""
    
    def __init__(self, repository: ItemRepository):
        self.repository = repository
    
    async def execute(self, item_id: int) -> bool:
        """Executa a remoção de um item"""
        return await self.repository.delete(item_id)


class GetItemsByCategoriaUseCase:
    """Caso de uso para buscar itens por categoria"""
    
    def __init__(self, repository: ItemRepository):
        self.repository = repository
    
    async def execute(self, categoria: str) -> List[Item]:
        """Executa a busca de itens por categoria"""
        return await self.repository.get_by_categoria(categoria)


class GetItemsByStatusUseCase:
    """Caso de uso para buscar itens por status"""
    
    def __init__(self, repository: ItemRepository):
        self.repository = repository
    
    async def execute(self, status: str) -> List[Item]:
        """Executa a busca de itens por status"""
        return await self.repository.get_by_status(status)
