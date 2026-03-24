import logging
from sqlalchemy import select
from local.src.infrastructure.database.config import async_session_maker as local_session_maker
from local.src.infrastructure.database.models import LocalModel
from item.src.infrastructure.database.config import async_session_maker as item_session_maker
from item.src.infrastructure.repositories.item_repository_impl import ItemRepositoryImpl


logger = logging.getLogger(__name__)


async def sync_local_projection_for_item() -> None:
    """Sincroniza os locais atuais na projeção usada pelo módulo de item."""
    logger.info("Iniciando sync de locais para item...")
    try:
        async with local_session_maker() as local_session:
            result = await local_session.execute(select(LocalModel))
            locais = result.scalars().all()

        if not locais:
            logger.info("Sync de locais para item: nenhum local para sincronizar")
            return

        async with item_session_maker() as item_session:
            item_repo = ItemRepositoryImpl(item_session)
            for local in locais:
                await item_repo.upsert_local_reference(
                    local_id=local.id,
                    tipo=local.tipo,
                    bairro=local.bairro,
                    descricao=local.descricao,
                )

        logger.info(f"Sync de locais para item finalizado: {len(locais)} local(is) sincronizado(s)")
    except Exception as e:
        logger.error(f"Erro ao sincronizar locais para item: {e}", exc_info=True)
