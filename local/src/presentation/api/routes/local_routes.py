from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from local.src.application.schemas.local_schema import (
    LocalCreate,
    LocalResponse,
    LocalUpdate,
    LocalListResponse,
)
from local.src.application.use_cases.local_use_cases import (
    CreateLocalUseCase,
    GetLocalByIdUseCase,
    GetAllLocalsUseCase,
    UpdateLocalUseCase,
    DeleteLocalUseCase,
    GetLocalsByBairroUseCase
)
from local.src.domain.entities.local import Local
from local.src.infrastructure.database.config import get_session
from local.src.infrastructure.repositories.local_repository_impl import LocalRepositoryImpl

router = APIRouter(tags=["Locais"])

@router.post("/", response_model=LocalResponse, status_code=status.HTTP_201_CREATED)
async def create_item(
    local_data: LocalCreate,
    session: AsyncSession = Depends(get_session)
):
    """Cria um novo local"""
    repository = LocalRepositoryImpl(session)
    use_case = CreateLocalUseCase(repository)
    
    local = Local(
        tipo=local_data.tipo,
        bairro=local_data.bairro,
        descricao=local_data.descricao
        
    )
    
    try:
        created_local = await use_case.execute(local)
        return created_local
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/", response_model=LocalListResponse)
async def get_all_locals(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_session)
):
    """Lista todos os locais com paginação"""
    repository = LocalRepositoryImpl(session)
    use_case = GetAllLocalsUseCase(repository)
    
    locals = await use_case.execute(skip, limit)
    total = await repository.count()
    
    return LocalListResponse(
        locals=locals,
        total=total,
        skip=skip,
        limit=limit
    )

@router.get("/bairro/{bairro}", response_model=List[LocalResponse])
async def get_locals_by_categoria(
    bairro: str,
    session: AsyncSession = Depends(get_session)
):
    """Busca local por bairro"""
    repository = LocalRepositoryImpl(session)
    use_case = GetLocalsByBairroUseCase(repository)
    
    locals = await use_case.execute(bairro)
    return locals

@router.get("/{local_id}", response_model=LocalResponse)
async def get_item(
    local_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Busca um local por ID"""
    repository = LocalRepositoryImpl(session)
    use_case = GetLocalByIdUseCase(repository)
    
    local = await use_case.execute(local_id)
    
    if not local:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"local com ID {local_id} não encontrado"
        )
    
    return local

@router.put("/{local_id}", response_model=LocalResponse)
async def update_local(
    local_id: int,
    local_data: LocalUpdate,
    session: AsyncSession = Depends(get_session)
):
    """Atualiza um local existente"""
    repository = LocalRepositoryImpl(session)
    
    try:
        # Busca o item existente
        get_use_case = GetLocalByIdUseCase(repository)
        existing_local = await get_use_case.execute(local_id)
        
        if not existing_local:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Local com ID {local_id} não encontrado"
            )
        
        # Atualiza apenas os campos fornecidos
        update_data = local_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(existing_local, field, value)
        
        # Revalida a entidade após as modificações
        existing_local.__post_init__()
        
        # Executa a atualização
        update_use_case = UpdateLocalUseCase(repository)
        updated_local = await update_use_case.execute(local_id, existing_local)
        
        return updated_local
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
@router.delete("/{local_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_local(
    local_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Remove um local"""
    repository = LocalRepositoryImpl(session)
    use_case = DeleteLocalUseCase(repository)
    
    deleted = await use_case.execute(local_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"local com ID {local_id} não encontrado"
        )
    
    return None