from abc import ABC, abstractmethod
from typing import List, Optional
from reclamante.src.domain.entities.reclamante import Reclamante


class ReclamanteRepository(ABC):
    """Interface do repositório de reclamantes (Port)"""
    
    @abstractmethod
    async def create(self, item: Reclamante) -> Reclamante:
        """Cria um novo reclamante no repositório"""
        pass
    
    @abstractmethod
    async def get_by_id(self, id: int) -> Optional[Reclamante]:
        """Busca um reclamante por ID"""
        pass
    
    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Reclamante]:
        """Lista todos os reclamantes com paginação"""
        pass
    
    @abstractmethod
    async def update(self, item_id: int, item: Reclamante) -> Optional[Reclamante]:
        """Atualiza um reclamante existente"""
        pass
    
    @abstractmethod
    async def delete(self, item_id: int) -> bool:
        """Remove um reclamante do repositório"""
        pass
    
    
    @abstractmethod
    async def count(self) -> int:
        """Conta o total de reclamantes no repositório"""
        pass
