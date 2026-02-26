from abc import ABC, abstractmethod
from typing import List, Optional
from responsavel.src.domain.entities.responsavel import Responsavel

class ResponsavelRepository(ABC):
    """Interface abstrata para repositórios de responsáveis."""

    @abstractmethod
    async def create(self, responsavel: Responsavel) -> Responsavel:
        """Cria um novo responsável no repositório."""
        pass

    @abstractmethod
    async def get_by_id(self, responsavel_id: int) -> Optional[Responsavel]:
        """Busca um responsável pelo ID."""
        pass

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Responsavel]:
        """Lista todos os responsáveis com paginação."""
        pass

    @abstractmethod
    async def update(self, responsavel_id: int, responsavel: Responsavel) -> Optional[Responsavel]:
        """Atualiza um responsável existente no repositório."""
        pass

    @abstractmethod
    async def delete(self, responsavel_id: int) -> bool:
        """Remove um responsável do repositório."""
        pass

    @abstractmethod
    async def get_by_ativo(self, ativo: bool) -> List[Responsavel]:
        """Busca responsáveis pelo status de ativo."""
        pass

    @abstractmethod
    async def count(self) -> int:
        """Retorna a contagem total de responsáveis no repositório."""
        pass

