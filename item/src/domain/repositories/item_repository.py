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

    @abstractmethod
    async def exists_local(self, local_id: int) -> bool:
        """Verifica se o Local existe na projeção local do módulo Item."""
        pass

    @abstractmethod
    async def exists_responsavel(self, responsavel_id: int) -> bool:
        """Verifica se o Responsável existe na projeção local do módulo Item."""
        pass

    @abstractmethod
    async def exists_responsavel_ativo(self, responsavel_id: int) -> bool:
        """Verifica se o Responsável existe e está ativo na projeção local do módulo Item."""
        pass

    @abstractmethod
    async def upsert_local_reference(self, local_id: int, tipo: str, bairro: str, descricao: str) -> None:
        """Cria/atualiza projeção local de Local via evento."""
        pass

    @abstractmethod
    async def delete_local_reference(self, local_id: int) -> None:
        """Remove Local da projeção local de Item via evento."""
        pass

    @abstractmethod
    async def upsert_responsavel_reference(self, responsavel_id: int, nome: str, cargo: str, telefone: str, ativo: bool = True) -> None:
        """Cria/atualiza projeção local de Responsável via evento."""
        pass

    @abstractmethod
    async def delete_responsavel_reference(self, responsavel_id: int) -> None:
        """Remove Responsável da projeção local de Item via evento."""
        pass
