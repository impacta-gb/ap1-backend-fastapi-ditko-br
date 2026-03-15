from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from responsavel.src.application.schemas.responsavel_schema import (
    ResponsavelCreate,
    ResponsavelResponse,
    ResponsavelPatch,
    ResponsavelUpdate,
    ResponsavelStatusUpdate,
    ResponsavelListResponse
)
from responsavel.src.application.use_cases.responsavel_use_cases import (
    CreateResponsavelUseCase,
    GetResponsavelByIdUseCase,
    GetAllResponsaveisUseCase,
    UpdateResponsavelUseCase,
    DeleteResponsavelUseCase,
    GetResponsaveisByAtivoUseCase
)
from responsavel.src.domain.entities.responsavel import Responsavel
from responsavel.src.infrastructure.database.config import get_session
from responsavel.src.infrastructure.repositories.responsavel_repository_impl import ResponsavelRepositoryImpl


router = APIRouter(tags=["Responsáveis"])

@router.post("/", response_model=ResponsavelResponse, status_code=status.HTTP_201_CREATED)
async def create_responsavel(
    responsavel_data: ResponsavelCreate,
    session: AsyncSession = Depends(get_session)
):
    """Cria um novo responsável (ativo inicial sempre será True)"""
    repository = ResponsavelRepositoryImpl(session)
    use_case = CreateResponsavelUseCase(repository)

    try:
        responsavel = Responsavel(
            nome=responsavel_data.nome,
            cargo=responsavel_data.cargo,
            telefone=responsavel_data.telefone,
            ativo=True
        )

        created_responsavel = await use_case.execute(responsavel)
        return created_responsavel
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
@router.get("/", response_model=ResponsavelListResponse)
async def get_all_responsaveis(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_session)
):
    """Lista todos os responsáveis com paginação"""
    repository = ResponsavelRepositoryImpl(session)
    use_case = GetAllResponsaveisUseCase(repository)

    try:
        responsaveis = await use_case.execute(skip, limit)
        total = await repository.count()

        return ResponsavelListResponse(
            responsaveis=responsaveis,
            total=total,
            skip=skip,
            limit=limit
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/ativo/{ativo_value}", response_model=List[ResponsavelResponse])
async def get_responsaveis_by_ativo(
    ativo_value: bool,
    session: AsyncSession = Depends(get_session)
):
    """Busca responsáveis por status ativo"""
    repository = ResponsavelRepositoryImpl(session)
    use_case = GetResponsaveisByAtivoUseCase(repository)

    try:
        responsaveis = await use_case.execute(ativo_value)
        return responsaveis
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{responsavel_id}", response_model=ResponsavelResponse)
async def get_responsavel(
    responsavel_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Busca um responsável por ID"""
    repository = ResponsavelRepositoryImpl(session)
    use_case = GetResponsavelByIdUseCase(repository)

    try:
        responsavel = await use_case.execute(responsavel_id)

        if not responsavel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Responsável com ID {responsavel_id} não encontrado"
            )

        return responsavel
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/{responsavel_id}", response_model=ResponsavelResponse)
async def update_responsavel_full(
    responsavel_id: int,
    responsavel_data: ResponsavelUpdate,
    session: AsyncSession = Depends(get_session)
):
    """Atualiza um responsável existente (atualização completa - não altera status ativo)"""
    repository = ResponsavelRepositoryImpl(session)
    
    try:
        # Busca o responsável existente
        get_use_case = GetResponsavelByIdUseCase(repository)
        existing_responsavel = await get_use_case.execute(responsavel_id)
        
        if not existing_responsavel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Responsável com ID {responsavel_id} não encontrado"
            )
        
        # Cria nova entidade com os dados fornecidos, mantendo o status ativo atual
        updated_responsavel_entity = Responsavel(
            id=responsavel_id,
            nome=responsavel_data.nome,
            cargo=responsavel_data.cargo,
            telefone=responsavel_data.telefone,
            ativo=existing_responsavel.ativo  # Mantém o status ativo existente
        )
        
        # Executa a atualização
        update_use_case = UpdateResponsavelUseCase(repository)
        updated_responsavel = await update_use_case.execute(responsavel_id, updated_responsavel_entity)
        
        return updated_responsavel
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch("/{responsavel_id}", response_model=ResponsavelResponse)
async def update_responsavel_partial(
    responsavel_id: int,
    responsavel_data: ResponsavelPatch,
    session: AsyncSession = Depends(get_session)
):
    """Atualiza parcialmente um responsável existente (não altera status ativo)"""
    repository = ResponsavelRepositoryImpl(session)
    
    try:
        # Busca o responsável existente
        get_use_case = GetResponsavelByIdUseCase(repository)
        existing_responsavel = await get_use_case.execute(responsavel_id)
        
        if not existing_responsavel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Responsável com ID {responsavel_id} não encontrado"
            )
        
        # Cria entidade com os dados atualizados
        updated_responsavel_entity = Responsavel(
            id=responsavel_id,
            nome=responsavel_data.nome if responsavel_data.nome is not None else existing_responsavel.nome,
            cargo=responsavel_data.cargo if responsavel_data.cargo is not None else existing_responsavel.cargo,
            telefone=responsavel_data.telefone if responsavel_data.telefone is not None else existing_responsavel.telefone,
            ativo=existing_responsavel.ativo  # Mantém o status ativo existente
        )
        
        # Executa a atualização
        update_use_case = UpdateResponsavelUseCase(repository)
        updated_responsavel = await update_use_case.execute(responsavel_id, updated_responsavel_entity)
        
        return updated_responsavel
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch("/{responsavel_id}/status", response_model=ResponsavelResponse)
async def update_responsavel_status(
    responsavel_id: int,
    status_data: ResponsavelStatusUpdate,
    session: AsyncSession = Depends(get_session)
):
    """Altera o status ativo/inativo de um responsável (endpoint específico para regra de negócio)"""
    repository = ResponsavelRepositoryImpl(session)
    
    try:
        # Busca o responsável existente
        get_use_case = GetResponsavelByIdUseCase(repository)
        existing_responsavel = await get_use_case.execute(responsavel_id)
        
        if not existing_responsavel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Responsável com ID {responsavel_id} não encontrado"
            )
        
        # Cria entidade com o status atualizado
        updated_responsavel_entity = Responsavel(
            id=responsavel_id,
            nome=existing_responsavel.nome,
            cargo=existing_responsavel.cargo,
            telefone=existing_responsavel.telefone,
            ativo=status_data.ativo  # Atualiza apenas o status ativo
        )
        
        # Executa a atualização
        update_use_case = UpdateResponsavelUseCase(repository)
        updated_responsavel = await update_use_case.execute(responsavel_id, updated_responsavel_entity)
        
        return updated_responsavel
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{responsavel_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_responsavel(
    responsavel_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Remove um responsável"""
    repository = ResponsavelRepositoryImpl(session)
    use_case = DeleteResponsavelUseCase(repository)

    try:
        deleted = await use_case.execute(responsavel_id)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Responsável com ID {responsavel_id} não encontrado"
            )

        return None
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
