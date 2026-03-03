from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from local.src.domain.entities.local import Local
from local.src.domain.repositories.local_repository import LocalRepository
from local.src.infrastructure.database.models import LocalModel

class LocalRepositoryImpl(LocalRepository):
    """Implementação concreta do repositório de locais usando SQLAlchemy"""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _model_to_entity(self, model: LocalModel) -> Local:
        """Converte um modelo SQLAlchemy em entidade de dominio"""

        return Local(
            id = model.id,
            bairro = model.bairro,
            tipo = model.tipo
            descricao = model.tipo
        )
    def _entity_to_model(self, entity: Local) -> LocalModel:
        """Converte uma entidade de dominio em modelo SQLAlchemy"""

        return LocalModel(
            id=entity.id,
            bairro = entity.bairro,
            tipo = entity.tipo,
            descricao = entity.descricao
        )
    async def create(self, local: Local) -> Local:
        """Cria um novo local no banco de dados"""
        model = self._entity_to_model(local)
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return self._model_to_entity(model)

    async def get_by_id(self, local_id: int) -> Optional[Local]:
        """Busca um local por ID"""
        result = await self.session.execute(
            select(LocalModel).where(LocalModel.id == local_id)
        )
        model = result.scalar_one_or_none()
        return self._model_to_entity(model) if model else None

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Local]:
        """Lista todos os locais com paginação"""
        result = await self.session.execute(
            select(LocalModel).offset(skip).limit(limit)
        )
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]

    async def update(self, local_id: int, local: Local) -> Optional[Local]:
        """Atualiza um local existente"""
        result = await self.session.execute(
            select(LocalModel).where(LocalModel.id == local_id)
        )
        model = result.scalar_one_or_none()
        
        if not model:
            return None
        
        model.bairro = local.bairro
        model.tipo = local.tipo
        model.descricao = local.descricao
        
        await self.session.commit()
        await self.session.refresh(model)
        return self._model_to_entity(model)


    async def delete(self, local_id: int) -> bool:
        """Remove um local do banco de dados"""
        result = await self.session.execute(
            select(LocalModel).where(LocalModel.id == local_id)
        )
        model = result.scalar_one_or_none()
        
        if not model:
            return False
        
        await self.session.delete(model)
        await self.session.commit()
        return True


     async def get_by_bairro(self, bairro: str) -> List[Local]:
        """Busca Locais por bairro"""
        result = await self.session.execute(
            select(LocalModel).where(LocalModel.categoria == categoria)
        )
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]