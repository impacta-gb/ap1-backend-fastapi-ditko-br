from typing import List, Optional
from reclamante.src.domain.entities.reclamante import Reclamante
from reclamante.src.domain.repositories.reclamante_repository import ReclamanteRepository


class CreateReclamanteUseCase:
    """Caso de uso para criar um reclamante"""

    def __init__(self, repository: ReclamanteRepository):
        self.repository = repository

    async def execute(self, reclamante: Reclamante) -> Reclamante:

        return await self.repository.create(reclamante)

class GetReclamanteByIdUseCase:
    """Caso de uso para buscar um reclamante por ID"""

    def __init__(self, repository: ReclamanteRepository):
        self.repository = repository

    async def execute(self, id: int) -> Optional[Reclamante]:
        """Executa a busca de local por ID"""
        if id <= 0:
            raise ValueError("ID de reclamante deve ser maior que zero")
        
        return await self.repository.get_by_id(id)
class GetAllReclamantesUseCase:
    """Caso de uso para listar todos os reclamantes"""
    
    def __init__(self, repository: ReclamanteRepository):
        self.repository = repository
    
    async def execute(self, skip: int = 0, limit: int = 100) -> List[Reclamante]:
        """Executa a listagem de todos os reclamantes com validação de paginação"""
        if skip < 0:
            raise ValueError("Skip não pode ser negativo")
        
        if limit <= 0 or limit > 1000:
            raise ValueError("Limit deve estar entre 1 e 1000")
        
        return await self.repository.get_all(skip, limit)

class UpdateReclamanteUseCase:
    """Caso de uso para atualizar um reclamante"""
    
    def __init__(self, repository: ReclamanteRepository):
        self.repository = repository
    
    async def execute(self, id: int, reclamante: Reclamante) -> Optional[Reclamante]:
        
        # Busca o reclamante atual para verificar existência
        existing_reclamante = await self.repository.get_by_id(id)
        
        if not existing_reclamante:
            return None
        
        return await self.repository.update(id, reclamante)

class DeleteReclamanteUseCase:
    """Caso de uso para deletar um Reclamante"""
    
    def __init__(self, repository: ReclamanteRepository):
        self.repository = repository
    
    async def execute(self, id: int) -> bool:
        
        # Busca o reclamante para verificar existência
        reclamante = await self.repository.get_by_id(id)
        
        if not reclamante:
            return False
        
        return await self.repository.delete(id)

