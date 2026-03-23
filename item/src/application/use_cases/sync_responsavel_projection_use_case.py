import logging
from sqlalchemy import select
from responsavel.src.infrastructure.database.config import async_session_maker as responsavel_session_maker
from responsavel.src.infrastructure.database.models import ResponsavelModel
from item.src.infrastructure.database.config import async_session_maker as item_session_maker
from item.src.infrastructure.repositories.item_repository_impl import ItemRepositoryImpl


logger = logging.getLogger(__name__)


async def sync_responsavel_projection_for_item() -> None:
    """Sincroniza os responsáveis atuais na projeção usada pelo módulo de item."""
    logger.info("Iniciando sync de responsáveis para item...")
    try:
        async with responsavel_session_maker() as responsavel_session:
            result = await responsavel_session.execute(select(ResponsavelModel))
            responsaveis = result.scalars().all()

        if not responsaveis:
            logger.info("Sync de responsáveis para item: nenhum responsável para sincronizar")
            return

        async with item_session_maker() as item_session:
            item_repo = ItemRepositoryImpl(item_session)
            for responsavel in responsaveis:
                await item_repo.upsert_responsavel_reference(
                    responsavel_id=responsavel.id,
                    nome=responsavel.nome,
                    cargo=responsavel.cargo,
                    telefone=responsavel.telefone,
                    ativo=bool(responsavel.ativo),
                )

        logger.info(
            f"Sync de responsáveis para item finalizado: {len(responsaveis)} responsável(eis) sincronizado(s)"
        )
    except Exception as e:
        logger.error(f"Erro ao sincronizar responsáveis para item: {e}", exc_info=True)
