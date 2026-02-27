from abc import ABC, abstractmethod
from typing import List, Optional
from item.src.domain.entities.item import Item


class ItemRepository(ABC):
    """Interface do repositório de itens (Port)"""
    
    @abstractmethod
    async def create(self, item: Item) -> Item:
        """Cria um novo item no repositório"""
        pass
    
    @abstractmethod
    async def get_by_id(self, item_id: int) -> Optional[Item]:
        """Busca um item por ID"""
        pass
    
    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Item]:
        """Lista todos os itens com paginação"""
        pass
    
    @abstractmethod
    async def update(self, item_id: int, item: Item) -> Optional[Item]:
        """Atualiza um item existente"""
        pass
    
    @abstractmethod
    async def delete(self, item_id: int) -> bool:
        """Remove um item do repositório"""
        pass
    
    @abstractmethod
    async def get_by_categoria(self, categoria: str) -> List[Item]:
        """Busca itens por categoria"""
        pass
    
    @abstractmethod
    async def get_by_status(self, status: str) -> List[Item]:
        """Busca itens por status"""
        pass
    
    @abstractmethod
    async def count(self) -> int:
        """Conta o total de itens no repositório"""
        pass
