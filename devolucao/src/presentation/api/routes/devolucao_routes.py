from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from devolucao.src.application.schemas.devolucao_schema import (
    DevolucaoCreate,
    DevolucaoResponse,
    DevolucaoUpdate,
    DevolucaoPatch,
    DevolucaoListResponse
)
from devolucao.src.application.use_cases.devolucao_use_cases import (
    CreateDevolucaoUseCase,
    GetDevolucaoByIdUseCase,
    GetAllDevolucoesUseCase,
    UpdateDevolucaoUseCase,
    DeleteDevolucaoUseCase,
    GetDevolucoesByDataUseCase,
    CountDevolucoesUseCase
)
from devolucao.src.domain.entities.devolucao import Devolucao
from devolucao.src.infrastructure.database.config import get_session
from devolucao.src.infrastructure.repositories.devolucao_repository_impl import DevolucaoRepositoryImpl
from devolucao.src.infrastructure.messaging.producer import DevolucaoKafkaProducer


router = APIRouter(tags=["Devoluções"])


@router.post("/", response_model=DevolucaoResponse, status_code=status.HTTP_201_CREATED)
async def create_devolucao(
    devolucao_data: DevolucaoCreate,
    session: AsyncSession = Depends(get_session)
):
    """Cria uma nova devolução"""
    repository = DevolucaoRepositoryImpl(session)
    use_case = CreateDevolucaoUseCase(repository)

    try:
        devolucao = Devolucao(
            reclamante_id=devolucao_data.reclamante_id,
            item_id=devolucao_data.item_id,
            observacao=devolucao_data.observacao,
            data_devolucao=devolucao_data.data_devolucao
        )
        created = await use_case.execute(devolucao)

        # Publica evento para atualizar os módulos interessados (ex.: item).
        producer = DevolucaoKafkaProducer()
        await producer.publish_devolucao_criada(
            devolucao_id=created.id,
            item_id=created.item_id,
            reclamante_id=created.reclamante_id,
        )

        return created
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=DevolucaoListResponse)
async def get_all_devolucoes(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_session)
):
    """Lista todas as devoluções com paginação"""
    repository = DevolucaoRepositoryImpl(session)
    use_case = GetAllDevolucoesUseCase(repository)

    try:
        devolucoes = await use_case.execute(skip, limit)
        total = await CountDevolucoesUseCase(repository).execute()
        return DevolucaoListResponse(
            devolucoes=devolucoes,
            total=total,
            skip=skip,
            limit=limit
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/data/{data}", response_model=List[DevolucaoResponse])
async def get_devolucoes_by_data(
    data: datetime,
    session: AsyncSession = Depends(get_session)
):
    """Busca devoluções por data"""
    repository = DevolucaoRepositoryImpl(session)
    use_case = GetDevolucoesByDataUseCase(repository)

    try:
        return await use_case.execute(data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{devolucao_id}", response_model=DevolucaoResponse)
async def get_devolucao(
    devolucao_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Busca uma devolução por ID"""
    repository = DevolucaoRepositoryImpl(session)
    use_case = GetDevolucaoByIdUseCase(repository)

    try:
        devolucao = await use_case.execute(devolucao_id)

        if not devolucao:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Devolução com ID {devolucao_id} não encontrada"
            )

        return devolucao
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/{devolucao_id}", response_model=DevolucaoResponse)
async def update_devolucao_full(
    devolucao_id: int,
    devolucao_data: DevolucaoUpdate,
    session: AsyncSession = Depends(get_session)
):
    """Atualiza uma devolução existente (atualização completa)"""
    repository = DevolucaoRepositoryImpl(session)

    try:
        get_use_case = GetDevolucaoByIdUseCase(repository)
        existing = await get_use_case.execute(devolucao_id)

        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Devolução com ID {devolucao_id} não encontrada"
            )

        updated_entity = Devolucao(
            id=devolucao_id,
            reclamante_id=devolucao_data.reclamante_id,
            item_id=devolucao_data.item_id,
            observacao=devolucao_data.observacao,
            data_devolucao=devolucao_data.data_devolucao
        )

        update_use_case = UpdateDevolucaoUseCase(repository)
        updated = await update_use_case.execute(devolucao_id, updated_entity)

        producer = DevolucaoKafkaProducer()
        await producer.publish_devolucao_atualizada(
            devolucao_id=updated.id,
            item_id=updated.item_id,
            reclamante_id=updated.reclamante_id,
        )

        return updated

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch("/{devolucao_id}", response_model=DevolucaoResponse)
async def update_devolucao_partial(
    devolucao_id: int,
    devolucao_data: DevolucaoPatch,
    session: AsyncSession = Depends(get_session)
):
    """Atualiza parcialmente uma devolução existente"""
    repository = DevolucaoRepositoryImpl(session)

    try:
        get_use_case = GetDevolucaoByIdUseCase(repository)
        existing = await get_use_case.execute(devolucao_id)

        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Devolução com ID {devolucao_id} não encontrada"
            )

        updated_entity = Devolucao(
            id=devolucao_id,
            reclamante_id=devolucao_data.reclamante_id if devolucao_data.reclamante_id is not None else existing.reclamante_id,
            item_id=devolucao_data.item_id if devolucao_data.item_id is not None else existing.item_id,
            observacao=devolucao_data.observacao if devolucao_data.observacao is not None else existing.observacao,
            data_devolucao=devolucao_data.data_devolucao if devolucao_data.data_devolucao is not None else existing.data_devolucao
        )

        update_use_case = UpdateDevolucaoUseCase(repository)
        updated = await update_use_case.execute(devolucao_id, updated_entity)

        producer = DevolucaoKafkaProducer()
        await producer.publish_devolucao_atualizada(
            devolucao_id=updated.id,
            item_id=updated.item_id,
            reclamante_id=updated.reclamante_id,
        )

        return updated

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{devolucao_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_devolucao(
    devolucao_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Remove uma devolução"""
    repository = DevolucaoRepositoryImpl(session)
    use_case = DeleteDevolucaoUseCase(repository)

    try:
        existing = await GetDevolucaoByIdUseCase(repository).execute(devolucao_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Devolução com ID {devolucao_id} não encontrada"
            )

        deleted = await use_case.execute(devolucao_id)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Devolução com ID {devolucao_id} não encontrada"
            )

        producer = DevolucaoKafkaProducer()
        await producer.publish_devolucao_deletada(
            devolucao_id=devolucao_id,
            item_id=existing.item_id,
            reclamante_id=existing.reclamante_id,
        )

        return None
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
