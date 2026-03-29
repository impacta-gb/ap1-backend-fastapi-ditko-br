from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from reclamante.src.application.schemas.reclamante_schema import (
    ReclamanteCreate,
    ReclamanteResponse,
    ReclamanteUpdate,
    ReclamantePatch,
    ReclamanteListResponse
)
from reclamante.src.application.use_cases.reclamante_use_cases import (
    CreateReclamanteUseCase,
    GetReclamanteByIdUseCase,
    GetAllReclamantesUseCase,
    UpdateReclamanteUseCase,
    DeleteReclamanteUseCase,
)
from reclamante.src.domain.entities.reclamante import Reclamante
from reclamante.src.infrastructure.database.config import get_session
from reclamante.src.infrastructure.repositories.reclamante_repository_impl import ReclamanteRepositoryImpl
from reclamante.src.infrastructure.messaging.producer import ReclamanteKafkaProducer

router = APIRouter(tags=["Reclamantes"])


def success_response(message: str, data: Any):
    return {"message": message, "data": data}

@router.post("/",
             response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_reclamante(
    reclamante_data: ReclamanteCreate,
    session: AsyncSession = Depends(get_session)
):
    """Cria um novo reclamante"""
    repository = ReclamanteRepositoryImpl(session)
    use_case = CreateReclamanteUseCase(repository)

    try:
        reclamante = Reclamante(
            nome=reclamante_data.nome,
            telefone=reclamante_data.telefone,
            documento=reclamante_data.documento
        )
        created_reclamante = await use_case.execute(reclamante)
        
        # Publicar evento de reclamante criado
        producer = ReclamanteKafkaProducer()
        await producer.publish_reclamante_criado(
            reclamante_id=created_reclamante.id,
            nome=created_reclamante.nome,
            documento=created_reclamante.documento,
            telefone=created_reclamante.telefone
        )
        
        return success_response("Reclamante criado com sucesso", created_reclamante)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
@router.get("/",
            response_model=dict)
async def get_all_reclamantes(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_session)
):
    """Lista todos os reclamantes com paginação"""
    repository = ReclamanteRepositoryImpl(session)
    use_case = GetAllReclamantesUseCase(repository)

    try:
        reclamantes = await use_case.execute(skip, limit)
        total = await repository.count()

        payload = ReclamanteListResponse(
            reclamantes=reclamantes,
            total=total,
            skip=skip,
            limit=limit
        )
        # Mensagem dinâmica baseada na quantidade de reclamantes
        if total == 0:
            message = "Nenhum reclamante encontrado"
        elif total == 1:
            message = "1 reclamante encontrado"
        else:
            message = f"{total} reclamantes encontrados"
        return success_response(message, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{reclamante_id}",
            response_model=dict)
async def get_reclamante(
    reclamante_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Busca um reclamante por ID"""
    repository = ReclamanteRepositoryImpl(session)
    use_case = GetReclamanteByIdUseCase(repository)

    try:
        reclamante = await use_case.execute(reclamante_id)

        if not reclamante:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Reclamante com ID {reclamante_id} não encontrado'
            )

        return success_response("Reclamante encontrado com sucesso", reclamante)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/{reclamante_id}", response_model=dict)
async def update_reclamante(
    reclamante_id: int,
    reclamante_data: ReclamanteUpdate,
    session: AsyncSession = Depends(get_session)
):
    """Atualiza um reclamante existente"""
    repository = ReclamanteRepositoryImpl(session)

    try:
        get_use_case = GetReclamanteByIdUseCase(repository)
        existing_reclamante = await get_use_case.execute(reclamante_id)

        if not existing_reclamante:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Reclamante com ID {reclamante_id} não encontrado'
            )
        
        updated_reclamante_entity = Reclamante(id=reclamante_id,
                      nome=reclamante_data.nome,
            telefone=reclamante_data.telefone,
            documento=reclamante_data.documento)

        update_use_case = UpdateReclamanteUseCase(repository)
        updated_reclamante = await update_use_case.execute(reclamante_id, updated_reclamante_entity)

        # Publicar evento de reclamante atualizado
        producer = ReclamanteKafkaProducer()
        await producer.publish_reclamante_atualizado(
            reclamante_id=updated_reclamante.id,
            nome=updated_reclamante.nome,
            documento=updated_reclamante.documento,
            telefone=updated_reclamante.telefone
        )

        return success_response("Reclamante atualizado com sucesso", updated_reclamante)
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch("/{reclamante_id}", response_model=dict)
async def patch_reclamante(
    reclamante_id: int,
    reclamante_data: ReclamantePatch,
    session: AsyncSession = Depends(get_session)
):
    """Atualiza parcialmente um reclamante existente"""
    repository = ReclamanteRepositoryImpl(session)

    try:
        get_use_case = GetReclamanteByIdUseCase(repository)
        existing_reclamante = await get_use_case.execute(reclamante_id)

        if not existing_reclamante:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Reclamante com ID {reclamante_id} não encontrado'
            )

        patch_data = reclamante_data.model_dump(exclude_unset=True)
        if not patch_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Informe ao menos um campo para atualização parcial"
            )

        updated_reclamante_entity = Reclamante(
            id=reclamante_id,
            nome=patch_data.get("nome", existing_reclamante.nome),
            telefone=patch_data.get("telefone", existing_reclamante.telefone),
            documento=patch_data.get("documento", existing_reclamante.documento),
        )

        update_use_case = UpdateReclamanteUseCase(repository)
        updated_reclamante = await update_use_case.execute(reclamante_id, updated_reclamante_entity)

        producer = ReclamanteKafkaProducer()
        await producer.publish_reclamante_atualizado(
            reclamante_id=updated_reclamante.id,
            nome=updated_reclamante.nome,
            documento=updated_reclamante.documento,
            telefone=updated_reclamante.telefone
        )

        return success_response("Reclamante atualizado com sucesso", updated_reclamante)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    

@router.delete("/{reclamante_id}", response_model=dict, status_code=status.HTTP_200_OK)
async def delete_reclamante(
    reclamante_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Remove um reclamante"""

    repositoy = ReclamanteRepositoryImpl(session)
    use_case = DeleteReclamanteUseCase(repositoy)

    deleted = await use_case.execute(reclamante_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Reclamante com ID {reclamante_id} não encontrado'
        )

    producer = ReclamanteKafkaProducer()
    await producer.publish_reclamante_deletado(reclamante_id=reclamante_id)
    
    return success_response("Reclamante deletado com sucesso", {"id": reclamante_id})
