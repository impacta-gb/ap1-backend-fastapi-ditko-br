from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional, Set
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

    @abstractmethod
    async def exists_item(self, item_id: int) -> bool:
        """Verifica se um item existe na projeção"""
        pass

    @abstractmethod
    async def exists_item_not_devolvido(self, item_id: int) -> bool:
        """Verifica se um item existe e ainda não foi devolvido (status != 'devolvido')"""
        pass

    @abstractmethod
    async def exists_devolucao_for_item(self, item_id: int) -> bool:
        """Verifica se já existe uma devolução registrada para o item."""
        pass

    @abstractmethod
    async def exists_reclamante(self, reclamante_id: int) -> bool:
        """Verifica se um reclamante existe na projeção"""
        pass

    @abstractmethod
    async def upsert_item_reference(
        self, 
        item_id: int, 
        local_id: int, 
        responsavel_id: int, 
        status: str = "disponivel"
    ) -> None:
        """Sincroniza projeção de item via evento"""
        pass

    @abstractmethod
    async def delete_item_reference(self, item_id: int) -> None:
        """Remove item da projeção usada pelo módulo de devolução."""
        pass

    @abstractmethod
    async def get_all_item_reference_ids(self) -> Set[int]:
        """Retorna todos os IDs atualmente presentes na projeção de itens."""
        pass

    @abstractmethod
    async def upsert_reclamante_reference(
        self,
        reclamante_id: int,
        nome: str,
        documento: Optional[str] = None,
        telefone: Optional[str] = None
    ) -> None:
        """Sincroniza projeção de reclamante via evento"""
        pass

    @abstractmethod
    async def delete_reclamante_reference(self, reclamante_id: int) -> None:
        """Remove reclamante da projeção usada pelo módulo de devolução."""
        pass
