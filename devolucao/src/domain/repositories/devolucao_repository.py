from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional
from devolucao.src.domain.entities.devolucao import Devolucao

class DevolucaoRepository(ABC):
    """Interface do repositório de devoluções."""

    @abstractmethod
    async def create(self, devolucao: Devolucao) -> Devolucao:
        """Cria uma nova devolução no repositório"""
        pass

    @abstractmethod
    async def get_by_id(self, devolucao_id: int) -> Optional[Devolucao]:
        """Busca uma devolução pelo ID"""
        pass

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Devolucao]:
        """Lista todas as devoluções com paginação"""
        pass

    @abstractmethod
    async def update(self, devolucao_id: int, devolucao: Devolucao) -> Optional[Devolucao]:
        """Atualiza uma devolução existente"""
        pass

    @abstractmethod
    async def delete(self, devolucao_id: int) -> bool:
        """Remove uma devolução do repositório"""
        pass

    @abstractmethod
    async def get_by_data(self, data: datetime) -> List[Devolucao]:
        """Busca devoluções pela data"""
        pass

    @abstractmethod
    async def count(self) -> int:
        """Conta o número total de devoluções"""
        pass
