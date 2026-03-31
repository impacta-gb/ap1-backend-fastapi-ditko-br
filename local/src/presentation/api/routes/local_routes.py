from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from local.src.application.schemas.local_schema import (
    LocalCreate,
    LocalResponse,
    LocalUpdate,
    LocalPatch,
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
from local.src.infrastructure.messaging.producer import LocalKafkaProducer

router = APIRouter(tags=["Locais"])


def success_response(message: str, data: Any):
    return {"message": message, "data": data}

@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_local(
    local_data: LocalCreate,
    session: AsyncSession = Depends(get_session)
):
    """Cria um novo local"""
    repository = LocalRepositoryImpl(session)
    use_case = CreateLocalUseCase(repository)

    try:
        local = Local(
            tipo=local_data.tipo,
            bairro=local_data.bairro,
            descricao=local_data.descricao
        )

        created_local = await use_case.execute(local)

        producer = LocalKafkaProducer()
        await producer.publish_local_criado(
            local_id=created_local.id,
            tipo=created_local.tipo,
            bairro=created_local.bairro,
            descricao=created_local.descricao,
        )

        return success_response("Local criado com sucesso", created_local)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/", response_model=dict)
async def get_all_locals(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_session)
):
    """Lista todos os locais com paginação"""
    repository = LocalRepositoryImpl(session)
    use_case = GetAllLocalsUseCase(repository)

    try:
        locals = await use_case.execute(skip, limit)
        total = await repository.count()

        payload = LocalListResponse(
            locals=locals,
            total=total,
            skip=skip,
            limit=limit
        )
        # Mensagem dinâmica baseada na quantidade de locais
        if total == 0:
            message = "Nenhum local encontrado"
        elif total == 1:
            message = "1 local encontrado"
        else:
            message = f"{total} locais encontrados"
        return success_response(message, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/bairro/{bairro}", response_model=dict)
async def get_locals_by_bairro(
    bairro: str,
    session: AsyncSession = Depends(get_session)
):
    """Busca local por bairro"""
    repository = LocalRepositoryImpl(session)
    use_case = GetLocalsByBairroUseCase(repository)

    try:
        locals = await use_case.execute(bairro)
        # Mensagem dinâmica baseada na quantidade de locais
        if len(locals) == 0:
            message = f"Nenhum local encontrado no bairro '{bairro}'"
        elif len(locals) == 1:
            message = f"1 local encontrado no bairro '{bairro}'"
        else:
            message = f"{len(locals)} locais encontrados no bairro '{bairro}'"
        return success_response(message, locals)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/{local_id}", response_model=dict)
async def get_local(
    local_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Busca um local por ID"""
    repository = LocalRepositoryImpl(session)
    use_case = GetLocalByIdUseCase(repository)

    try:
        local = await use_case.execute(local_id)

        if not local:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"local com ID {local_id} não encontrado"
            )

        return success_response("Local encontrado com sucesso", local)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.put("/{local_id}", response_model=dict)
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
        
        updated_local_entity = Local(
            id=local_id,
            tipo=local_data.tipo,
            descricao=local_data.descricao,
            bairro=local_data.bairro,
            created_at=existing_local.created_at,
            updated_at=existing_local.updated_at,
        )
        
        # Executa a atualização
        update_use_case = UpdateLocalUseCase(repository)
        updated_local = await update_use_case.execute(local_id, updated_local_entity)

        producer = LocalKafkaProducer()
        await producer.publish_local_atualizado(
            local_id=updated_local.id,
            tipo=updated_local.tipo,
            bairro=updated_local.bairro,
            descricao=updated_local.descricao,
        )
        
        return success_response("Local atualizado com sucesso", updated_local)
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch("/{local_id}", response_model=dict)
async def patch_local(
    local_id: int,
    local_data: LocalPatch,
    session: AsyncSession = Depends(get_session)
):
    """Atualiza parcialmente um local existente"""
    repository = LocalRepositoryImpl(session)

    try:
        get_use_case = GetLocalByIdUseCase(repository)
        existing_local = await get_use_case.execute(local_id)

        if not existing_local:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Local com ID {local_id} não encontrado"
            )

        patch_data = local_data.model_dump(exclude_unset=True)
        if not patch_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Informe ao menos um campo para atualização parcial"
            )

        for field, value in patch_data.items():
            setattr(existing_local, field, value)

        existing_local.__post_init__()

        update_use_case = UpdateLocalUseCase(repository)
        updated_local = await update_use_case.execute(local_id, existing_local)

        producer = LocalKafkaProducer()
        await producer.publish_local_atualizado(
            local_id=updated_local.id,
            tipo=updated_local.tipo,
            bairro=updated_local.bairro,
            descricao=updated_local.descricao,
        )

        return success_response("Local atualizado com sucesso", updated_local)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
@router.delete("/{local_id}", response_model=dict, status_code=status.HTTP_200_OK)
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

    producer = LocalKafkaProducer()
    await producer.publish_local_deletado(local_id=local_id)
    
    return success_response("Local deletado com sucesso", {"id": local_id})