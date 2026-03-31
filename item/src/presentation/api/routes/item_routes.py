from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from item.src.application.schemas.item_schema import (
    ItemCreate,
    ItemResponse,
    ItemUpdate,
    ItemPatch,
    ItemListResponse
)
from item.src.application.use_cases.item_use_cases import (
    CreateItemUseCase,
    GetItemByIdUseCase,
    GetAllItemsUseCase,
    UpdateItemUseCase,
    DeleteItemUseCase,
    GetItemsByCategoriaUseCase,
    GetItemsByStatusUseCase
)
from item.src.domain.entities.item import Item
from item.src.infrastructure.database.config import get_session
from item.src.infrastructure.repositories.item_repository_impl import ItemRepositoryImpl
from item.src.infrastructure.messaging.producer import ItemKafkaProducer

router = APIRouter(tags=["Items"])


def success_response(message: str, data: Any):
    return {"message": message, "data": data}


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_item(
    item_data: ItemCreate,
    session: AsyncSession = Depends(get_session)
):
    """Cria um novo item (status inicial sempre será 'disponivel')"""
    repository = ItemRepositoryImpl(session)
    use_case = CreateItemUseCase(repository)

    try:
        item = Item(
            nome=item_data.nome,
            categoria=item_data.categoria,
            data_encontro=item_data.data_encontro,
            descricao=item_data.descricao,
            status="disponivel",  # Use case garante que seja sempre disponivel
            local_id=item_data.local_id,
            responsavel_id=item_data.responsavel_id
        )

        created_item = await use_case.execute(item)
        
        # Publicar evento de item criado
        producer = ItemKafkaProducer()
        await producer.publish_item_criado(
            item_id=created_item.id,
            nome=created_item.nome,
            descricao=created_item.descricao,
            status=created_item.status,
            local_id=created_item.local_id,
            responsavel_id=created_item.responsavel_id
        )
        
        return success_response("Item criado com sucesso", created_item)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=dict)
async def get_all_items(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_session)
):
    """Lista todos os itens com paginação"""
    repository = ItemRepositoryImpl(session)
    use_case = GetAllItemsUseCase(repository)

    try:
        items = await use_case.execute(skip, limit)
        total = await repository.count()

        payload = ItemListResponse(
            items=items,
            total=total,
            skip=skip,
            limit=limit
        )
        # Mensagem dinâmica baseada na quantidade de itens
        if total == 0:
            message = "Nenhum item encontrado"
        elif total == 1:
            message = "1 item encontrado"
        else:
            message = f"{total} itens encontrados"
        return success_response(message, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/categoria/{categoria}", response_model=dict)
async def get_items_by_categoria(
    categoria: str,
    session: AsyncSession = Depends(get_session)
):
    """Busca itens por categoria"""
    repository = ItemRepositoryImpl(session)
    use_case = GetItemsByCategoriaUseCase(repository)

    try:
        items = await use_case.execute(categoria)
        # Mensagem dinâmica baseada na quantidade de itens
        if len(items) == 0:
            message = f"Nenhum item encontrado por categoria '{categoria}'"
        elif len(items) == 1:
            message = f"1 item encontrado por categoria '{categoria}'"
        else:
            message = f"{len(items)} itens encontrados por categoria '{categoria}'"
        return success_response(message, items)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/status/{status_value}", response_model=dict)
async def get_items_by_status(
    status_value: str,
    session: AsyncSession = Depends(get_session)
):
    """Busca itens por status"""
    repository = ItemRepositoryImpl(session)
    use_case = GetItemsByStatusUseCase(repository)

    try:
        items = await use_case.execute(status_value)
        # Mensagem dinâmica baseada na quantidade de itens
        if len(items) == 0:
            message = f"Nenhum item encontrado com status '{status_value}'"
        elif len(items) == 1:
            message = f"1 item encontrado com status '{status_value}'"
        else:
            message = f"{len(items)} itens encontrados com status '{status_value}'"
        return success_response(message, items)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{item_id}", response_model=dict)
async def get_item(
    item_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Busca um item por ID"""
    repository = ItemRepositoryImpl(session)
    use_case = GetItemByIdUseCase(repository)

    try:
        item = await use_case.execute(item_id)

        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Item com ID {item_id} não encontrado"
            )

        return success_response("Item encontrado com sucesso", item)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/{item_id}", response_model=dict)
async def update_item(
    item_id: int,
    item_data: ItemUpdate,
    session: AsyncSession = Depends(get_session)
):
    """Atualiza um item existente"""
    repository = ItemRepositoryImpl(session)
    
    try:
        # Busca o item existente
        get_use_case = GetItemByIdUseCase(repository)
        existing_item = await get_use_case.execute(item_id)
        
        if not existing_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Item com ID {item_id} não encontrado"
            )
        
        updated_entity = Item(
            id=item_id,
            nome=item_data.nome,
            categoria=item_data.categoria,
            data_encontro=item_data.data_encontro,
            descricao=item_data.descricao,
            status=item_data.status,
            local_id=item_data.local_id,
            responsavel_id=item_data.responsavel_id,
            created_at=existing_item.created_at,
            updated_at=existing_item.updated_at,
        )
        
        # Executa a atualização
        update_use_case = UpdateItemUseCase(repository)
        updated_item = await update_use_case.execute(item_id, updated_entity)
        
        # Publicar evento de item atualizado
        producer = ItemKafkaProducer()
        await producer.publish_item_atualizado(
            item_id=updated_item.id,
            nome=updated_item.nome,
            descricao=updated_item.descricao,
            status=updated_item.status,
            local_id=updated_item.local_id,
            responsavel_id=updated_item.responsavel_id
        )
        
        return success_response("Item atualizado com sucesso", updated_item)
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch("/{item_id}", response_model=dict)
async def patch_item(
    item_id: int,
    item_data: ItemPatch,
    session: AsyncSession = Depends(get_session)
):
    """Atualiza parcialmente um item existente"""
    repository = ItemRepositoryImpl(session)

    try:
        get_use_case = GetItemByIdUseCase(repository)
        existing_item = await get_use_case.execute(item_id)

        if not existing_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Item com ID {item_id} não encontrado"
            )

        patch_data = item_data.model_dump(exclude_unset=True)
        if not patch_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Informe ao menos um campo para atualização parcial"
            )

        for field, value in patch_data.items():
            setattr(existing_item, field, value)

        existing_item.__post_init__()

        update_use_case = UpdateItemUseCase(repository)
        updated_item = await update_use_case.execute(item_id, existing_item)

        producer = ItemKafkaProducer()
        await producer.publish_item_atualizado(
            item_id=updated_item.id,
            nome=updated_item.nome,
            descricao=updated_item.descricao,
            status=updated_item.status,
            local_id=updated_item.local_id,
            responsavel_id=updated_item.responsavel_id
        )

        return success_response("Item atualizado com sucesso", updated_item)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{item_id}", response_model=dict, status_code=status.HTTP_200_OK)
async def delete_item(
    item_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Remove um item"""
    repository = ItemRepositoryImpl(session)
    use_case = DeleteItemUseCase(repository)

    try:
        deleted = await use_case.execute(item_id)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Item com ID {item_id} não encontrado"
            )

        # Publicar evento de item deletado para manter projeções sincronizadas.
        producer = ItemKafkaProducer()
        await producer.publish_item_deletado(item_id=item_id)

        return success_response("Item deletado com sucesso", {"id": item_id})
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
