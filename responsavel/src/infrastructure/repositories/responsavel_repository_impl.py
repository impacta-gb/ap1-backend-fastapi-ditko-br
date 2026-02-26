from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.entities.responsavel import Responsavel
from src.domain.repositories.responsavel_repository import ResponsavelRepository
from src.infrastructure.database.models import ResponsavelModel

class ResponsavelRepositoryImpl(ResponsavelRepository):
    """Implementação concreta do repositório de responsaveis usando SQLAlchemy"""

    def __init__(self, session: AsyncSession):
        self.session = session

    def model_to_entity(self, model: ResponsavelModel) -> Responsavel:
        """Converte um modelo SQLAlchemy para entidade de domínio"""
        return Responsavel(
            id=model.id,
            nome=model.nome,
            cargo=model.cargo,
            telefone=model.telefone,
            ativo=model.ativo
        )
    
    def entity_to_model(self, entity: Responsavel) -> ResponsavelModel:
        """Converte uma entidade de domínio para um modelo SQLAlchemy"""
        return ResponsavelModel(
            id=entity.id,
            nome=entity.nome,
            cargo=entity.cargo,
            telefone=entity.telefone,
            ativo=entity.ativo
        )
    
    async def create(self, responsavel: Responsavel) -> Responsavel:
        model = self.entity_to_model(responsavel)
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return self.model_to_entity(model)
    
    async def get_by_id(self, responsavel_id: int) -> Optional[Responsavel]:
        """Busca um responsavel pelo ID"""
        result = await self.session.execute(
            select(ResponsavelModel).where(ResponsavelModel.id == responsavel_id)
        )
        model = result.scalar_one_or_none()
        return self.model_to_entity(model) if model else None
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Responsavel]:
        """Lista todos os responsaveis com paginação"""
        result = await self.session.execute(
            select(ResponsavelModel).offset(skip).limit(limit)
        )
        models = result.scalars().all()
        return [self.model_to_entity(model) for model in models]
    
    async def update(self, responsavel_id: int, responsavel: Responsavel) -> Optional[Responsavel]:
        """Atualiza um responsavel existente"""
        result = await self.session.execute(
            select(ResponsavelModel).where(ResponsavelModel.id == responsavel_id)
        )
        model = result.scalar_one_or_none()
        
        if not model:
            return None
        
        model.nome = responsavel.nome
        model.cargo = responsavel.cargo
        model.telefone = responsavel.telefone
        model.ativo = responsavel.ativo
        
        await self.session.commit()
        await self.session.refresh(model)
        return self.model_to_entity(model)
    
    async def delete(self, responsavel_id: int) -> bool:
        """Remove um responsavel do repositório"""
        result = await self.session.execute(
            select(ResponsavelModel).where(ResponsavelModel.id == responsavel_id)
        )
        model = result.scalar_one_or_none()
        
        if not model:
            return False
        
        await self.session.delete(model)
        await self.session.commit()
        return True
    
    async def get_by_ativo(self, ativo: bool) -> List[Responsavel]:
        """Busca responsáveis pelo status de ativo"""
        result = await self.session.execute(
            select(ResponsavelModel).where(ResponsavelModel.ativo == ativo)
        )
        models = result.scalars().all()
        return [self.model_to_entity(model) for model in models]
    
    async def count(self) -> int:
        """Retorna a contagem total de responsáveis no repositório"""
        result = await self.session.execute(select(func.count(ResponsavelModel.id)))
        return result.scalar()
            