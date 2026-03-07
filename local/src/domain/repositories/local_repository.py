from abc import ABC, abstractmethod
from typing import List, Optional
from local.src.domain.entities.local import Local

class LocalRepository(ABC):
    """Interface do repositório de locais (Port)"""

    @abstractmethod
    async def create(self, local: Local) -> Local:
        """Cria um novo local no repositório"""
        pass
    @abstractmethod
    async def get_by_id(self, local_id: int) -> Optional[Local]:
        """Busca um local por ID"""
        pass
    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Local]:
        """Lista todos os locais com paginação"""
        pass
    @abstractmethod
    async def update(self, local_id: int, local:Local) -> Optional[Local]:
        """Atualiza um local existente"""
        pass
    @abstractmethod
    async def delete(self, local_id: int) -> bool:
        """Remove um local do repositório"""
        pass
    @abstractmethod
    async def get_by_bairro(self, bairro: str) -> List[Local]:
        """Busca Locais por bairro"""
        self
    @abstractmethod
    async def count(self) -> int:
        """Conta o total de locais no repositório"""
        pass
