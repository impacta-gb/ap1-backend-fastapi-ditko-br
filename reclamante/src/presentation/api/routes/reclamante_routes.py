from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from reclamante.src.application.schemas.reclamante_schema import (
    ReclamanteCreate,
    ReclamanteResponse,
    ReclamanteUpdate,
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

router = APIRouter(tags=["Reclamantes"])

@router.post("/",
             response_model=ReclamanteResponse, status_code=status.HTTP_201_CREATED)
async def create_reclamante(
    reclamante_data: ReclamanteCreate,
    session: AsyncSession = Depends(get_session)
):
    """Cria um novo reclamante"""
    repository = ReclamanteRepositoryImpl(session)
    use_case = CreateReclamanteUseCase(repository)

    reclamante = Reclamante(
        nome=reclamante_data.nome,
        telefone=reclamante_data.telefone,
        documento=reclamante_data.documento
    )

    try:
        created_reclamante = await use_case.execute(reclamante)
        return created_reclamante
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
@router.get("/",
            response_model=ReclamanteListResponse)
async def get_all_reclamantes(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_session)
):
    """Lista todos os reclamantes com paginação"""
    repository = ReclamanteRepositoryImpl(session)
    use_case = GetAllReclamantesUseCase(repository)

    reclamantes = await use_case.execute(skip, limit)
    total = await repository.count()

    return ReclamanteListResponse(
        reclamantes=reclamantes,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/{reclamante_id}",
            response_model=ReclamanteResponse)
async def get_reclamante(
    reclamante_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Busca um reclamante por ID"""
    repository = ReclamanteRepositoryImpl(session)
    use_case = GetReclamanteByIdUseCase(repository)

    reclamante = await use_case.execute(reclamante_id)

    if not reclamante:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Reclamante com ID {reclamante_id} não encontrado'
        )
    
    return reclamante


@router.put("/{reclamante_id}", response_model=ReclamanteResponse)
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
        
        updated_reclamante_entity = Reclamante(id=reclamante_id,                      nome=reclamante_data.nome,            telefone=reclamante_data.telefone,            documento=reclamante_data.documento)

        update_use_case = UpdateReclamanteUseCase(repository)
        updated_reclamante = await update_use_case.execute(reclamante_id, updated_reclamante_entity)

        return updated_reclamante
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    

@router.delete("/{reclamante_id}", status_code=status.HTTP_204_NO_CONTENT)
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
    
    return None
