from typing import List, Optional
from datetime import datetime
from local.src.domain.entities.local import Local
from local.src.domain.repositories.local_repository import LocalRepository


class CreateLocalUseCase:
    """Caso de uso para criar um local"""

    def __init__(self, repository: LocalRepository):
        self.repository = repository

    async def execute(self, local: Local) -> Local:

        return await self.repository.create(local)

class GetLocalByIdUseCase:
    """Caso de uso para buscar um local por ID"""

    def __init__(self, repository: LocalRepository):
        self.repository = repository

    async def execute(self, local_id: int) -> Optional[Local]:
        """Executa a busca de local por ID"""
        if local_id <= 0:
            raise ValueError("ID de local deve ser maior que zero")
        
        return await self.repository.get_by_id(local_id)
class GetAllLocalsUseCase:
    """Caso de uso para listar todos os Locais"""
    
    def __init__(self, repository: LocalRepository):
        self.repository = repository
    
    async def execute(self, skip: int = 0, limit: int = 100) -> List[Local]:
        """Executa a listagem de todos os locaís com validação de paginação"""
        if skip < 0:
            raise ValueError("Skip não pode ser negativo")
        
        if limit <= 0 or limit > 1000:
            raise ValueError("Limit deve estar entre 1 e 1000")
        
        return await self.repository.get_all(skip, limit)

class UpdateLocalUseCase:
    """Caso de uso para atualizar um local"""
    
    def __init__(self, repository: LocalRepository):
        self.repository = repository
    
    async def execute(self, local_id: int, local: Local) -> Optional[Local]:
        
        # Busca o local atual para verificar existência
        existing_local = await self.repository.get_by_id(local_id)
        
        if not existing_local:
            return None
        
        return await self.repository.update(local_id, local)

class DeleteLocalUseCase:
    """Caso de uso para deletar um local"""
    
    def __init__(self, repository: LocalRepository):
        self.repository = repository
    
    async def execute(self, local_id: int) -> bool:
        
        # Busca o local para verificar existência
        local = await self.repository.get_by_id(local_id)
        
        if not local:
            return False
        
        return await self.repository.delete(local_id)

class GetLocalsByBairroUseCase:
    """Caso de uso para buscar locais por bairro"""
    
    def __init__(self, repository: LocalRepository):
        self.repository = repository
    
    async def execute(self, bairro: str) -> List[Local]:
        """Executa a busca de locais por bairro"""
        if not bairro or len(bairro.strip()) == 0:
            raise ValueError("Bairro não pode estar vazio")
        
        return await self.repository.get_by_bairro(bairro)
