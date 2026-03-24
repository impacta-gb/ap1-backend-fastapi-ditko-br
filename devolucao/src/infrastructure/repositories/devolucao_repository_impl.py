from typing import List, Optional, Set
from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from devolucao.src.domain.entities.devolucao import Devolucao
from devolucao.src.domain.repositories.devolucao_repository import DevolucaoRepository
from devolucao.src.infrastructure.database.models import (
    DevolucaoModel,
    ItemReferenceModel,
    ReclamanteReferenceModel
)


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

        # Mantem a projeção consistente imediatamente após registrar a devolução.
        item_ref_result = await self.session.execute(
            select(ItemReferenceModel).where(ItemReferenceModel.id == devolucao.item_id)
        )
        item_ref = item_ref_result.scalar_one_or_none()
        if item_ref:
            item_ref.status = "devolvido"
            item_ref.updated_at = datetime.now()

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

    async def exists_item(self, item_id: int) -> bool:
        """Verifica se um item existe na projeção"""
        result = await self.session.execute(
            select(ItemReferenceModel).where(ItemReferenceModel.id == item_id)
        )
        return result.scalar_one_or_none() is not None

    async def exists_item_not_devolvido(self, item_id: int) -> bool:
        """Verifica se um item existe e ainda não foi devolvido"""
        result = await self.session.execute(
            select(ItemReferenceModel).where(
                (ItemReferenceModel.id == item_id) & 
                (ItemReferenceModel.status != "devolvido")
            )
        )
        return result.scalar_one_or_none() is not None

    async def exists_devolucao_for_item(self, item_id: int) -> bool:
        """Verifica se já existe devolução registrada para o item."""
        result = await self.session.execute(
            select(DevolucaoModel).where(DevolucaoModel.item_id == item_id)
        )
        return result.scalar_one_or_none() is not None

    async def exists_reclamante(self, reclamante_id: int) -> bool:
        """Verifica se um reclamante existe na projeção"""
        result = await self.session.execute(
            select(ReclamanteReferenceModel).where(ReclamanteReferenceModel.id == reclamante_id)
        )
        return result.scalar_one_or_none() is not None

    async def upsert_item_reference(
        self,
        item_id: int,
        local_id: int,
        responsavel_id: int,
        status: str = "disponivel"
    ) -> None:
        """Sincroniza projeção de item via evento"""
        result = await self.session.execute(
            select(ItemReferenceModel).where(ItemReferenceModel.id == item_id)
        )
        item_ref = result.scalar_one_or_none()

        if item_ref:
            item_ref.local_id = local_id
            item_ref.responsavel_id = responsavel_id
            item_ref.status = status
        else:
            item_ref = ItemReferenceModel(
                id=item_id,
                local_id=local_id,
                responsavel_id=responsavel_id,
                status=status,
                updated_at=datetime.now()
            )
            self.session.add(item_ref)

        await self.session.commit()

    async def delete_item_reference(self, item_id: int) -> None:
        """Remove um item da projeção local de devolução."""
        result = await self.session.execute(
            select(ItemReferenceModel).where(ItemReferenceModel.id == item_id)
        )
        item_ref = result.scalar_one_or_none()

        if item_ref:
            await self.session.delete(item_ref)
            await self.session.commit()

    async def get_all_item_reference_ids(self) -> Set[int]:
        """Lista os IDs presentes na projeção de itens."""
        result = await self.session.execute(select(ItemReferenceModel.id))
        return {row[0] for row in result.all()}

    async def upsert_reclamante_reference(
        self,
        reclamante_id: int,
        nome: str,
        documento: Optional[str] = None,
        telefone: Optional[str] = None
    ) -> None:
        """Sincroniza projeção de reclamante via evento"""
        result = await self.session.execute(
            select(ReclamanteReferenceModel).where(ReclamanteReferenceModel.id == reclamante_id)
        )
        reclamante_ref = result.scalar_one_or_none()

        if reclamante_ref:
            reclamante_ref.nome = nome
            reclamante_ref.documento = documento
            reclamante_ref.telefone = telefone
        else:
            reclamante_ref = ReclamanteReferenceModel(
                id=reclamante_id,
                nome=nome,
                documento=documento,
                telefone=telefone,
                updated_at=datetime.now()
            )
            self.session.add(reclamante_ref)

        await self.session.commit()

    async def delete_reclamante_reference(self, reclamante_id: int) -> None:
        """Remove um reclamante da projeção local de devolução."""
        result = await self.session.execute(
            select(ReclamanteReferenceModel).where(ReclamanteReferenceModel.id == reclamante_id)
        )
        reclamante_ref = result.scalar_one_or_none()

        if reclamante_ref:
            await self.session.delete(reclamante_ref)
            await self.session.commit()
