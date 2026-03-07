from typing import List, Optional
from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from devolucao.src.domain.entities.devolucao import Devolucao
from devolucao.src.domain.repositories.devolucao_repository import DevolucaoRepository
from devolucao.src.infrastructure.database.models import DevolucaoModel


class DevolucaoRepositoryImpl(DevolucaoRepository):
    """Implementação concreta do repositório de devoluções usando SQLAlchemy"""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _model_to_entity(self, model: DevolucaoModel) -> Devolucao:
        """Converte um modelo SQLAlchemy para entidade de domínio"""
        return Devolucao(
            id=model.id,
            data_devolucao=model.data_devolucao,
            observacao=model.observacao,
            reclamante_id=model.reclamante_id,
            item_id=model.item_id,
            created_at=model.created_at,
            updated_at=model.updated_at
        )
    
    def _entity_to_model(self, entity: Devolucao) -> DevolucaoModel:
        """Converte uma entidade de domínio para um modelo SQLAlchemy"""
        return DevolucaoModel(
            id=entity.id,
            data_devolucao=entity.data_devolucao,
            observacao=entity.observacao,
            reclamante_id=entity.reclamante_id,
            item_id=entity.item_id,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )
    
    async def create(self, devolucao: Devolucao) -> Devolucao:
        """Cria uma nova devolução no banco de dados"""
        model = self._entity_to_model(devolucao)
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return self._model_to_entity(model)
    
    async def get_by_id(self, devolucao_id: int) -> Optional[Devolucao]:
        """Busca uma devolucao por ID"""
        result = await self.session.execute(
            select(DevolucaoModel).where(DevolucaoModel.id == devolucao_id)
        )
        model = result.scalar_one_or_none()
        return self._model_to_entity(model) if model else None
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Devolucao]:
        """Lista todas as devoluções com paginação"""
        result = await self.session.execute(
            select(DevolucaoModel).offset(skip).limit(limit)
        )
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]

    async def update(self, devolucao_id: int, devolucao: Devolucao) -> Optional[Devolucao]:
        """Atualiza uma devolução existente"""
        result = await self.session.execute(
            select(DevolucaoModel).where(DevolucaoModel.id == devolucao_id)
        )
        model = result.scalar_one_or_none()

        if not model:
            return None

        model.reclamante_id = devolucao.reclamante_id
        model.item_id = devolucao.item_id
        model.observacao = devolucao.observacao
        model.data_devolucao = devolucao.data_devolucao

        await self.session.commit()
        await self.session.refresh(model)
        return self._model_to_entity(model)

    async def delete(self, devolucao_id: int) -> bool:
        """Remove uma devolução do banco de dados"""
        result = await self.session.execute(
            select(DevolucaoModel).where(DevolucaoModel.id == devolucao_id)
        )
        model = result.scalar_one_or_none()

        if not model:
            return False

        await self.session.delete(model)
        await self.session.commit()
        return True

    async def get_by_data(self, data: datetime) -> List[Devolucao]:
        """Busca devoluções pela data"""
        result = await self.session.execute(
            select(DevolucaoModel).where(
                func.date(DevolucaoModel.data_devolucao) == func.date(data)
            )
        )
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]

    async def count(self) -> int:
        """Conta o total de devoluções no banco de dados"""
        result = await self.session.execute(select(func.count(DevolucaoModel.id)))
        return result.scalar()
