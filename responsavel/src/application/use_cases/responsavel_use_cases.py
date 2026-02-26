from typing import List, Optional
from responsavel.src.domain.entities.responsavel import Responsavel
from responsavel.src.domain.repositories.responsavel_repository import ResponsavelRepository


class CreateResponsavelUseCase:
    """Caso de uso para criar um novo responsável."""

    def __init__(self, repository: ResponsavelRepository):
        self.repository = repository

    async def execute(self, responsavel: Responsavel) -> Responsavel:
        """
        Executa a criação de um novo responsável com validações de negócio.
        
        Regras de negócio:
        - Responsável sempre inicia como ativo
        - Nome, cargo e telefone são obrigatórios
        - Validação de formato de telefone
        """
        # Garante que novo responsável sempre começa ativo
        responsavel.ativo = True
        
        # Validação adicional: formato de telefone brasileiro
        telefone_limpo = responsavel.telefone.replace("(", "").replace(")", "").replace("-", "").replace(" ", "")
        if not telefone_limpo.isdigit() or len(telefone_limpo) < 10 or len(telefone_limpo) > 11:
            raise ValueError("Telefone deve conter 10 ou 11 dígitos (DDD + número)")
        
        # TODO: Quando precisar, adicionar validação de duplicidade por nome ou telefone
        
        return await self.repository.create(responsavel)


class GetResponsavelByIdUseCase:
    """Caso de uso para buscar um responsável pelo ID."""

    def __init__(self, repository: ResponsavelRepository):
        self.repository = repository

    async def execute(self, responsavel_id: int) -> Optional[Responsavel]:
        """Executa a busca de um responsável por ID."""
        if responsavel_id <= 0:
            raise ValueError("ID do responsável deve ser maior que zero")
        
        return await self.repository.get_by_id(responsavel_id)


class GetAllResponsaveisUseCase:
    """Caso de uso para listar todos os responsáveis."""

    def __init__(self, repository: ResponsavelRepository):
        self.repository = repository

    async def execute(self, skip: int = 0, limit: int = 100) -> List[Responsavel]:
        """Executa a listagem de responsáveis com validação de paginação."""
        if skip < 0:
            raise ValueError("Skip não pode ser negativo")
        
        if limit <= 0 or limit > 1000:
            raise ValueError("Limit deve estar entre 1 e 1000")

        return await self.repository.get_all(skip, limit)


class UpdateResponsavelUseCase:
    """Caso de uso para atualizar um responsável existente."""

    def __init__(self, repository: ResponsavelRepository):
        self.repository = repository

    async def execute(self, responsavel_id: int, responsavel: Responsavel) -> Optional[Responsavel]:
        """
        Executa a atualização completa de um responsável (PUT).
        
        Regras de negócio:
        - Responsável deve existir
        - Validação de formato de telefone se alterado
        
        Nota: Para ativar/desativar use os endpoints PATCH específicos
        """
        # Busca o responsável existente
        existing_responsavel = await self.repository.get_by_id(responsavel_id)

        if not existing_responsavel:
            return None
        
        # Validação de telefone se foi alterado
        if responsavel.telefone != existing_responsavel.telefone:
            telefone_limpo = responsavel.telefone.replace("(", "").replace(")", "").replace("-", "").replace(" ", "")
            if not telefone_limpo.isdigit() or len(telefone_limpo) < 10 or len(telefone_limpo) > 11:
                raise ValueError("Telefone deve conter 10 ou 11 dígitos (DDD + número)")
        
        return await self.repository.update(responsavel_id, responsavel)


class DeleteResponsavelUseCase:
    """Caso de uso para deletar um responsável."""

    def __init__(self, repository: ResponsavelRepository):
        self.repository = repository

    async def execute(self, responsavel_id: int) -> bool:
        """
        Executa a remoção permanente de um responsável.
        
        Validações:
        - ID deve ser positivo
        - Responsável deve existir
        
        Nota: Para soft delete, use DesativarResponsavelUseCase
        """
        if responsavel_id <= 0:
            raise ValueError("ID do responsável deve ser maior que zero")
        
        # Busca o responsável para confirmar existência
        responsavel = await self.repository.get_by_id(responsavel_id)
        
        if not responsavel:
            return False
        
        # TODO: Quando implementar relacionamentos, validar se tem itens associados
        # e impedir deleção ou aplicar cascata conforme necessário
        
        return await self.repository.delete(responsavel_id)


class DesativarResponsavelUseCase:
    """Caso de uso para desativar um responsável."""

    def __init__(self, repository: ResponsavelRepository):
        self.repository = repository

    async def execute(self, responsavel_id: int) -> Optional[Responsavel]:
        """
        Desativa um responsável (soft delete).
        
        Regras de negócio:
        - Responsável deve existir
        - Já inativo não precisa ser desativado novamente
        """
        if responsavel_id <= 0:
            raise ValueError("ID do responsável deve ser maior que zero")
        
        # Busca o responsável
        responsavel = await self.repository.get_by_id(responsavel_id)
        
        if not responsavel:
            return None
        
        # Se já está inativo, retorna sem erro
        if not responsavel.ativo:
            return responsavel
        
        # Desativa o responsável
        responsavel.desativar_responsavel()
        
        # Atualiza no repositório
        return await self.repository.update(responsavel_id, responsavel)


class ReativarResponsavelUseCase:
    """Caso de uso para reativar um responsável."""

    def __init__(self, repository: ResponsavelRepository):
        self.repository = repository

    async def execute(self, responsavel_id: int) -> Optional[Responsavel]:
        """
        Reativa um responsável desativado.
        
        Regras de negócio:
        - Responsável deve existir
        - Deve estar inativo para ser reativado
        """
        if responsavel_id <= 0:
            raise ValueError("ID do responsável deve ser maior que zero")
        
        # Busca o responsável
        responsavel = await self.repository.get_by_id(responsavel_id)
        
        if not responsavel:
            return None
        
        # Se já está ativo, retorna sem erro
        if responsavel.ativo:
            return responsavel
        
        # Reativa o responsável
        responsavel.ativo = True
        
        # Atualiza no repositório
        return await self.repository.update(responsavel_id, responsavel)


class GetResponsaveisByAtivoUseCase:
    """Caso de uso para buscar responsáveis por status de ativo."""

    def __init__(self, repository: ResponsavelRepository):
        self.repository = repository

    async def execute(self, ativo: bool) -> List[Responsavel]:
        """Busca responsáveis pelo status de ativo/inativo."""
        if not isinstance(ativo, bool):
            raise ValueError("O parâmetro 'ativo' deve ser booleano")
        
        return await self.repository.get_by_ativo(ativo)
    