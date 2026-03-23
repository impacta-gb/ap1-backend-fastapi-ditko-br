"""
Consumer que processa eventos de responsável para criação de item
"""

import logging
from item.src.infrastructure.messaging.consumers.kafka_consumer import KafkaConsumer
from item.src.infrastructure.database.config import async_session_maker
from item.src.infrastructure.repositories.item_repository_impl import ItemRepositoryImpl

logger = logging.getLogger(__name__)

class ResponsavelEventConsumer(KafkaConsumer):
    """Consumer que escuta eventos de responsável para criação do item"""

    def __init__(self):
        super().__init__(
            topics=['responsavel_events'],
            group_id='item_create_group'
        )

    async def handle_message(self, message: dict):
        """Processa eventos de responsável"""
        try:
            event_type = message.get('event_type')

            if event_type == 'responsavel.criado':
                await self._handle_responsavel_criado(message)
            elif event_type in ('responsavel.atualizado', 'responsavel.status_alterado'):
                await self._handle_responsavel_atualizado(message)
            elif event_type == 'responsavel.deletado':
                await self._handle_responsavel_deletado(message)
            else:
                logger.debug(f"Tipo de evento não tratado: {event_type}")
        except Exception as e:
            logger.error(f"Erro ao processar mensagem de responsável: {e}")

    async def _handle_responsavel_criado(self, message: dict):
        """Sincroniza responsável criado no banco do módulo Item."""
        try:
            data = message.get('data', {})
            responsavel_id = data.get('responsavel_id')
            nome = data.get('nome')
            cargo = data.get('cargo')
            telefone = data.get('telefone')

            if not responsavel_id:
                logger.warning("responsavel_id não encontrado na mensagem de responsável")
                return

            if not nome or not cargo or not telefone:
                logger.warning("Dados incompletos para sincronizar responsável")
                return

            async with async_session_maker() as session:
                repository = ItemRepositoryImpl(session)
                await repository.upsert_responsavel_reference(
                    responsavel_id=responsavel_id,
                    nome=nome,
                    cargo=cargo,
                    telefone=telefone,
                    ativo=True,
                )

            logger.info(f"Responsável {responsavel_id} sincronizado no módulo Item")
        except Exception as e:
            logger.error(f"Erro ao sincronizar responsável no módulo Item: {e}")

    async def _handle_responsavel_atualizado(self, message: dict):
        """Sincroniza atualização/status do responsável no banco do módulo Item."""
        try:
            data = message.get('data', {})
            responsavel_id = data.get('responsavel_id')
            nome = data.get('nome')
            cargo = data.get('cargo')
            telefone = data.get('telefone')
            ativo = data.get('ativo', True)

            if not responsavel_id:
                logger.warning("responsavel_id não encontrado na mensagem de atualização de responsável")
                return

            if not nome or not cargo or not telefone:
                logger.warning("Dados incompletos para sincronizar atualização de responsável")
                return

            async with async_session_maker() as session:
                repository = ItemRepositoryImpl(session)
                await repository.upsert_responsavel_reference(
                    responsavel_id=responsavel_id,
                    nome=nome,
                    cargo=cargo,
                    telefone=telefone,
                    ativo=bool(ativo),
                )

            logger.info(f"Responsável {responsavel_id} atualizado/sincronizado no módulo Item")
        except Exception as e:
            logger.error(f"Erro ao sincronizar atualização de responsável no módulo Item: {e}")

    async def _handle_responsavel_deletado(self, message: dict):
        """Remove responsável da projeção local de Item."""
        try:
            data = message.get('data', {})
            responsavel_id = data.get('responsavel_id')

            if not responsavel_id:
                logger.warning("responsavel_id não encontrado na mensagem de responsável deletado")
                return

            async with async_session_maker() as session:
                repository = ItemRepositoryImpl(session)
                await repository.delete_responsavel_reference(responsavel_id=responsavel_id)

            logger.info(f"Responsável {responsavel_id} removido da projeção no módulo Item")
        except Exception as e:
            logger.error(f"Erro ao remover responsável no módulo Item: {e}")