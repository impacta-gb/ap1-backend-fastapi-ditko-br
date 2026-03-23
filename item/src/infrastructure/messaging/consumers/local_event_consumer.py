"""
Consumer que processa eventos de local para criação de item
"""

import logging
from item.src.infrastructure.messaging.consumers.kafka_consumer import KafkaConsumer
from item.src.infrastructure.database.config import async_session_maker
from item.src.infrastructure.repositories.item_repository_impl import ItemRepositoryImpl

logger = logging.getLogger(__name__)


class LocalEventConsumer(KafkaConsumer):
    """Consumer que escuta eventos de local para criação do item"""

    def __init__(self):
        super().__init__(
            topics=['local_events'],
            group_id='item_local_listener_group'
        )

    async def handle_message(self, message: dict):
        """Processa eventos de local"""
        try:
            event_type = message.get('event_type')

            if event_type == 'local.criado':
                await self._handle_local_criado(message)
            elif event_type == 'local.atualizado':
                await self._handle_local_atualizado(message)
            elif event_type == 'local.deletado':
                await self._handle_local_deletado(message)
            else:
                logger.debug(f"Tipo de evento não tratado: {event_type}")
        except Exception as e:
            logger.error(f"Erro ao processar mensagem de local: {e}")

    async def _handle_local_criado(self, message: dict):
        """Sincroniza local criado no banco do módulo Item."""
        try:
            data = message.get('data', {})
            local_id = data.get('local_id')
            tipo = data.get('tipo')
            bairro = data.get('bairro')
            descricao = data.get('descricao')

            if not local_id:
                logger.warning("local_id não encontrado na mensagem de local")
                return

            if not tipo or not bairro or not descricao:
                logger.warning("Dados incompletos para sincronizar local")
                return

            async with async_session_maker() as session:
                repository = ItemRepositoryImpl(session)
                await repository.upsert_local_reference(
                    local_id=local_id,
                    tipo=tipo,
                    bairro=bairro,
                    descricao=descricao,
                )

            logger.info(f"Local {local_id} sincronizado no módulo Item")
        except Exception as e:
            logger.error(f"Erro ao sincronizar local no módulo Item: {e}")

    async def _handle_local_atualizado(self, message: dict):
        """Sincroniza atualização de local no banco do módulo Item."""
        await self._handle_local_criado(message)

    async def _handle_local_deletado(self, message: dict):
        """Remove local da projeção do módulo Item."""
        try:
            data = message.get('data', {})
            local_id = data.get('local_id')

            if not local_id:
                logger.warning("local_id não encontrado na mensagem de local deletado")
                return

            async with async_session_maker() as session:
                repository = ItemRepositoryImpl(session)
                await repository.delete_local_reference(local_id=local_id)

            logger.info(f"Local {local_id} removido da projeção no módulo Item")
        except Exception as e:
            logger.error(f"Erro ao remover local no módulo Item: {e}")
