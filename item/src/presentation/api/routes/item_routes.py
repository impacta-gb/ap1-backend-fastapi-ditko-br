from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from item.src.application.schemas.item_schema import (
    ItemCreate,
    ItemResponse,
    ItemUpdate,
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


@router.post("/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
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
            descricao=created_item.descricao,
            status=created_item.status,
            local_id=created_item.local_id,
            responsavel_id=created_item.responsavel_id
        )
        
        return created_item
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=ItemListResponse)
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

        return ItemListResponse(
            items=items,
            total=total,
            skip=skip,
            limit=limit
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/categoria/{categoria}", response_model=List[ItemResponse])
async def get_items_by_categoria(
    categoria: str,
    session: AsyncSession = Depends(get_session)
):
    """Busca itens por categoria"""
    repository = ItemRepositoryImpl(session)
    use_case = GetItemsByCategoriaUseCase(repository)

    try:
        items = await use_case.execute(categoria)
        return items
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/status/{status_value}", response_model=List[ItemResponse])
async def get_items_by_status(
    status_value: str,
    session: AsyncSession = Depends(get_session)
):
    """Busca itens por status"""
    repository = ItemRepositoryImpl(session)
    use_case = GetItemsByStatusUseCase(repository)

    try:
        items = await use_case.execute(status_value)
        return items
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{item_id}", response_model=ItemResponse)
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

        return item
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/{item_id}", response_model=ItemResponse)
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
        
        # Atualiza apenas os campos fornecidos
        update_data = item_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(existing_item, field, value)
        
        # Revalida a entidade após as modificações
        existing_item.__post_init__()
        
        # Executa a atualização
        update_use_case = UpdateItemUseCase(repository)
        updated_item = await update_use_case.execute(item_id, existing_item)
        
        # Publicar evento de item atualizado
        producer = ItemKafkaProducer()
        await producer.publish_item_atualizado(
            item_id=updated_item.id,
            descricao=updated_item.descricao,
            status=updated_item.status,
            local_id=updated_item.local_id,
            responsavel_id=updated_item.responsavel_id
        )
        
        return updated_item
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
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

        return None
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
