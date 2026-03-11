from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from reclamante.src.domain.entities.reclamante import Reclamante
from reclamante.src.domain.repositories.reclamantel_repository import ReclamanteRepository
from reclamante.src.infrastructure.database.models import ReclamanteModel

class LocalRepositoryImpl(LocalRepository):
    """Implementação concreta do repositório de locais usando SQLAlchemy"""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _model_to_entity(self, model: ReclamanteModel) -> Reclamante:
        """Converte um modelo SQLAlchemy em entidade de dominio"""

        return Local(
            id=model.id,
            nome=model.nome,
            documento=model.documento,
            telefone=model.telefone,
            
        )
    def _entity_to_model(self, entity: Reclamante) -> ReclamanteModel:
        """Converte uma entidade de dominio em modelo SQLAlchemy"""

        return LocalModel(
            id=entity.id,
            nome = entity.nome,
            documento = entity.documento,
            telefone = entity.telefone
        )
    async def create(self, reclamante: Reclamante) -> Reclamante:
        """Cria um novo reclamante no banco de dados"""
        model = self._entity_to_model(reclamante)
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return self._model_to_entity(model)

    async def get_by_id(self, id: int) -> Optional[Reclamante]:
        """Busca um reclamante por ID"""
        result = await self.session.execute(
            select(ReclamanteModel).where(ReclamanteModel.id == id)
        )
        model = result.scalar_one_or_none()
        return self._model_to_entity(model) if model else None

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Reclamante]:
        """Lista todos os reclamantes com paginação"""
        result = await self.session.execute(
            select(ReclamanteModel).offset(skip).limit(limit)
        )
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]

    async def update(self, id: int, reclamante: Reclamante) -> Optional[Reclamante]:
        """Atualiza um reclamante existente"""
        result = await self.session.execute(
            select(ReclamanteModel).where(ReclamanteModel.id == id)
        )
        model = result.scalar_one_or_none()
        
        if not model:
            return None
        
        model.nome = reclamante.nome
        model.documento = reclamante.documento
        model.telefone = reclamante.telefone
        
        await self.session.commit()
        await self.session.refresh(model)
        return self._model_to_entity(model)


    async def delete(self, id: int) -> bool:
        """Remove um reclamante do banco de dados"""
        result = await self.session.execute(
            select(ReclamanteModel).where(ReclamanteModel.id == id)
        )
        model = result.scalar_one_or_none()
        
        if not model:
            return False
        
        await self.session.delete(model)
        await self.session.commit()
        return True
