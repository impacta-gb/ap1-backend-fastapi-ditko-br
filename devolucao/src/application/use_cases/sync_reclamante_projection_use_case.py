import logging
from sqlalchemy import select
from reclamante.src.infrastructure.database.config import async_session_maker as reclamante_session_maker
from reclamante.src.infrastructure.database.models import ReclamanteModel
from devolucao.src.infrastructure.database.config import async_session_maker as devolucao_session_maker
from devolucao.src.infrastructure.repositories.devolucao_repository_impl import DevolucaoRepositoryImpl


logger = logging.getLogger(__name__)


async def sync_reclamante_projection_for_devolucao() -> None:
    """Sincroniza os reclamantes atuais na projeção usada pelo módulo de devolução."""
    logger.info("Iniciando sync de reclamantes para devolução...")
    try:
        async with reclamante_session_maker() as reclamante_session:
            result = await reclamante_session.execute(select(ReclamanteModel))
            reclamantes = result.scalars().all()

        if not reclamantes:
            logger.info("Sync de reclamantes para devolução: nenhum reclamante para sincronizar")
            return

        async with devolucao_session_maker() as devolucao_session:
            devolucao_repo = DevolucaoRepositoryImpl(devolucao_session)
            for reclamante in reclamantes:
                await devolucao_repo.upsert_reclamante_reference(
                    reclamante_id=reclamante.id,
                    nome=reclamante.nome,
                    documento=reclamante.documento,
                    telefone=reclamante.telefone,
                )

        logger.info(
            f"Sync de reclamantes para devolução finalizado: {len(reclamantes)} reclamante(s) sincronizado(s)"
        )
    except Exception as e:
        logger.error(f"Erro ao sincronizar reclamantes para devolução: {e}", exc_info=True)
