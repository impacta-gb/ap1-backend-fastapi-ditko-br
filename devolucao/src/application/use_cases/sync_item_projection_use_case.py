import logging
from sqlalchemy import select
from item.src.infrastructure.database.config import async_session_maker as item_session_maker
from item.src.infrastructure.database.models import ItemModel
from devolucao.src.infrastructure.database.config import async_session_maker as devolucao_session_maker
from devolucao.src.infrastructure.repositories.devolucao_repository_impl import DevolucaoRepositoryImpl


logger = logging.getLogger(__name__)


async def sync_item_projection_for_devolucao() -> None:
    """Sincroniza os itens atuais na projeção usada pelo módulo de devolução."""
    logger.info("Iniciando sync de itens para devolução...")
    try:
        async with item_session_maker() as item_session:
            result = await item_session.execute(select(ItemModel))
            items = result.scalars().all()

        if not items:
            logger.info("Sync de itens para devolução: nenhum item para sincronizar")
            return

        async with devolucao_session_maker() as devolucao_session:
            devolucao_repo = DevolucaoRepositoryImpl(devolucao_session)
            item_ids_fonte = set()
            for item in items:
                item_ids_fonte.add(item.id)
                await devolucao_repo.upsert_item_reference(
                    item_id=item.id,
                    local_id=item.local_id,
                    responsavel_id=item.responsavel_id,
                    status=item.status,
                )

            # Remove projeções órfãs de itens que já não existem na origem.
            ids_projecao = await devolucao_repo.get_all_item_reference_ids()
            ids_orfaos = ids_projecao - item_ids_fonte
            for item_id in ids_orfaos:
                await devolucao_repo.delete_item_reference(item_id)

        logger.info(
            "Sync de itens para devolução finalizado: "
            f"{len(items)} item(ns) sincronizado(s), {len(ids_orfaos)} órfão(s) removido(s)"
        )
    except Exception as e:
        logger.error(f"Erro ao sincronizar itens para devolução: {e}", exc_info=True)
