from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.entities.item import Item
from src.domain.repositories.item_repository import ItemRepository
from src.infrastructure.database.models import ItemModel


class ItemRepositoryImpl(ItemRepository):
    """Implementação concreta do repositório de itens usando SQLAlchemy"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    def _model_to_entity(self, model: ItemModel) -> Item:
        """Converte um modelo SQLAlchemy para entidade de domínio"""
        return Item(
            id=model.id,
            nome=model.nome,
            categoria=model.categoria,
            data_encontro=model.data_encontro,
            descricao=model.descricao,
            status=model.status,
            local_id=model.local_id,
            responsavel_id=model.responsavel_id,
            created_at=model.created_at,
            updated_at=model.updated_at
        )
    
    def _entity_to_model(self, entity: Item) -> ItemModel:
        """Converte uma entidade de domínio para modelo SQLAlchemy"""
        return ItemModel(
            id=entity.id,
            nome=entity.nome,
            categoria=entity.categoria,
            data_encontro=entity.data_encontro,
            descricao=entity.descricao,
            status=entity.status,
            local_id=entity.local_id,
            responsavel_id=entity.responsavel_id,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )
    
    async def create(self, item: Item) -> Item:
        """Cria um novo item no banco de dados"""
        model = self._entity_to_model(item)
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return self._model_to_entity(model)
    
    async def get_by_id(self, item_id: int) -> Optional[Item]:
        """Busca um item por ID"""
        result = await self.session.execute(
            select(ItemModel).where(ItemModel.id == item_id)
        )
        model = result.scalar_one_or_none()
        return self._model_to_entity(model) if model else None
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Item]:
        """Lista todos os itens com paginação"""
        result = await self.session.execute(
            select(ItemModel).offset(skip).limit(limit)
        )
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]
    
    async def update(self, item_id: int, item: Item) -> Optional[Item]:
        """Atualiza um item existente"""
        result = await self.session.execute(
            select(ItemModel).where(ItemModel.id == item_id)
        )
        model = result.scalar_one_or_none()
        
        if not model:
            return None
        
        model.nome = item.nome
        model.categoria = item.categoria
        model.data_encontro = item.data_encontro
        model.descricao = item.descricao
        model.status = item.status
        model.local_id = item.local_id
        model.responsavel_id = item.responsavel_id
        
        await self.session.commit()
        await self.session.refresh(model)
        return self._model_to_entity(model)
    
    async def delete(self, item_id: int) -> bool:
        """Remove um item do banco de dados"""
        result = await self.session.execute(
            select(ItemModel).where(ItemModel.id == item_id)
        )
        model = result.scalar_one_or_none()
        
        if not model:
            return False
        
        await self.session.delete(model)
        await self.session.commit()
        return True
    
    async def get_by_categoria(self, categoria: str) -> List[Item]:
        """Busca itens por categoria"""
        result = await self.session.execute(
            select(ItemModel).where(ItemModel.categoria == categoria)
        )
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]
    
    async def get_by_status(self, status: str) -> List[Item]:
        """Busca itens por status"""
        # Normaliza o status de busca da mesma forma que na entidade
        normalized_status = status.lower().replace('í', 'i').replace('é', 'e').replace('á', 'a')
        
        result = await self.session.execute(
            select(ItemModel).where(ItemModel.status == normalized_status)
        )
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]
