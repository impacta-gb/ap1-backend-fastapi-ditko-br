from typing import List, Optional
from datetime import datetime
from devolucao.src.domain.entities.devolucao import Devolucao
from devolucao.src.domain.repositories.devolucao_repository import DevolucaoRepository


class CreateDevolucaoUseCase:
    """Caso de uso para criar uma devolução"""

    def __init__(self, repository: DevolucaoRepository):
        self.repository = repository

    async def execute(self, devolucao: Devolucao) -> Devolucao:
        """
        Executa a criação de uma nova devolução com validações de negócio
        
        Regras de negócio:
        - Data da devolução não pode ser futura
        - IDs de reclamante e item devem ser válidos
        - Item deve existir no sistema
        - Item não pode ter sido devolvido
        - Reclamante deve existir no sistema
        """

        # Validação: data da devolução não pode ser futura
        if devolucao.data_devolucao > datetime.now():
            raise ValueError("Data da devolução não pode ser no futuro")
        
        # Validação: IDs devem ser positivos
        if devolucao.reclamante_id <= 0:
            raise ValueError("ID do reclamante deve ser maior que zero")
        
        if devolucao.item_id <= 0:
            raise ValueError("ID do item deve ser maior que zero")
        
        # Validação: Item deve existir
        if not await self.repository.exists_item(devolucao.item_id):
            raise ValueError(f"Item com ID {devolucao.item_id} não encontrado no sistema.")

        # Validação: Não pode existir devolução anterior para o mesmo item
        if await self.repository.exists_devolucao_for_item(devolucao.item_id):
            raise ValueError(f"Item com ID {devolucao.item_id} já possui devolução registrada.")
        
        # Validação: Item não pode ter sido devolvido
        if not await self.repository.exists_item_not_devolvido(devolucao.item_id):
            raise ValueError(f"Item com ID {devolucao.item_id} já foi devolvido anteriormente.")
        
        # Validação: Reclamante deve existir
        if not await self.repository.exists_reclamante(devolucao.reclamante_id):
            raise ValueError(f"Reclamante com ID {devolucao.reclamante_id} não encontrado no sistema.")
        
        return await self.repository.create(devolucao)
    

class GetDevolucaoByIdUseCase:
    """Caso de uso para buscar uma devolução por ID"""

    def __init__(self, repository: DevolucaoRepository):
        self.repository = repository

    async def execute(self, devolucao_id: int) -> Optional[Devolucao]:
        """Executa busca de uma devolução por ID"""
        if devolucao_id <= 0:
            raise ValueError("ID da devolução deve ser maior que zero")
        
        return await self.repository.get_by_id(devolucao_id)
    

class GetAllDevolucoesUseCase:
    """Caso de uso para listar todas as devoluções"""

    def __init__(self, repository: DevolucaoRepository):
        self.repository = repository

    async def execute(self, skip: int = 0, limit: int = 100) -> List[Devolucao]:
        """Executa a listagem de todas as devoluções com validação de paginação"""
        if skip < 0:
            raise ValueError("Skip não pode ser negativo")
        
        if limit <= 0 or limit > 1000:
            raise ValueError("Limit deve estar entre 1 e 1000")
        
        return await self.repository.get_all(skip, limit)
    

class UpdateDevolucaoUseCase:
    """Caso de uso para atualizar uma devolução existente"""

    def __init__(self, repository: DevolucaoRepository):
        self.repository = repository

    async def execute(self, devolucao_id: int, devolucao: Devolucao) -> Optional[Devolucao]:
        """
        Executa a atualização completa de uma devolução (PUT).
        
        Regras de negócio:
        - Devolução deve existir
        - Data da devolução não pode ser futura
        - IDs de reclamante e item devem ser válidos
        """

        existing_devolucao = await self.repository.get_by_id(devolucao_id)

        if not existing_devolucao:
            return None
        
        if devolucao.data_devolucao > datetime.now():
            raise ValueError("Data da devolução não pode ser no futuro")
        
        if devolucao.reclamante_id <= 0:
            raise ValueError("ID do reclamante deve ser maior que zero")
        
        if devolucao.item_id <= 0:
            raise ValueError("ID do item deve ser maior que zero")
        
        return await self.repository.update(devolucao_id, devolucao)
    

class DeleteDevolucaoUseCase:
    """Caso de uso para deletar uma devolução."""

    def __init__(self, repository: DevolucaoRepository):
        self.repository = repository

    async def execute(self, devolucao_id: int) -> bool:
        """
        Executa a remoção de uma devoução
        
        Validações:
        - ID deve ser positivo
        - Devolução deve existir
        """

        if devolucao_id <= 0:
            raise ValueError("ID da devolução deve ser maior que zero")
        
        devolucao = await self.repository.get_by_id(devolucao_id)

        if not devolucao:
            return False
        
        return await self.repository.delete(devolucao_id)


class GetDevolucoesByDataUseCase:
    """Caso de uso para buscar devoluções por data"""

    def __init__(self, repository: DevolucaoRepository):
        self.repository = repository

    async def execute(self, data: datetime) -> List[Devolucao]:
        """Busca devoluções pela data"""
        if not data:
            raise ValueError("Data não pode ser nula")
        
        return await self.repository.get_by_data(data)


class CountDevolucoesUseCase:
    """Caso de uso para contar o total de devoluções"""

    def __init__(self, repository: DevolucaoRepository):
        self.repository = repository

    async def execute(self) -> int:
        """Retorna o número total de devoluções registradas"""
        return await self.repository.count()
