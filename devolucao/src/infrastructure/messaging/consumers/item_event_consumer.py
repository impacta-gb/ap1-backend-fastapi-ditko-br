"""
Consumer que processa eventos de item para o serviço de Devolução
"""
import logging
import json
from sqlalchemy.ext.asyncio import async_sessionmaker
from devolucao.src.infrastructure.messaging.consumers.kafka_consumer import KafkaConsumer
from devolucao.src.infrastructure.database.config import engine
from devolucao.src.infrastructure.repositories.devolucao_repository_impl import DevolucaoRepositoryImpl

logger = logging.getLogger(__name__)


class ItemEventConsumer(KafkaConsumer):
    """Consumer que escuta eventos de item e sincroniza projeção"""
    
    def __init__(self):
        super().__init__(
            topics=['item_events'],
            group_id='devolucao_item_listener_group'
        )
        self.async_session_maker = async_sessionmaker(engine, expire_on_commit=False)
    
    async def handle_message(self, message: dict):
        """Processa eventos de item"""
        try:
            event_type = message.get('event_type')
            
            if event_type == 'item.criado':
                await self._handle_item_criado(message)
            elif event_type == 'item.atualizado':
                await self._handle_item_atualizado(message)
            elif event_type == 'item.deletado':
                await self._handle_item_deletado(message)
            else:
                logger.debug(f"Tipo de evento não tratado: {event_type}")
        except Exception as e:
            logger.error(f"Erro ao processar mensagem de item: {e}")
    
    async def _handle_item_criado(self, message: dict):
        """Processa quando um item é criado
        Sincroniza a projeção de item em devolução
        """
        try:
            data = message.get('data', {})
            item_id = data.get('item_id')
            local_id = data.get('local_id')
            responsavel_id = data.get('responsavel_id')
            
            if not all([item_id, local_id, responsavel_id]):
                logger.warning("Dados incompletos na mensagem de item criado")
                return
            
            async with self.async_session_maker() as session:
                repository = DevolucaoRepositoryImpl(session)
                await repository.upsert_item_reference(
                    item_id=item_id,
                    local_id=local_id,
                    responsavel_id=responsavel_id,
                    status="disponivel"
                )
                logger.info(f"Item {item_id} sincronizado em devolução (status: disponivel)")
        except Exception as e:
            logger.error(f"Erro ao processar item criado: {e}")

    async def _handle_item_atualizado(self, message: dict):
        """Processa quando um item é atualizado
        Sincroniza status do item em devolução
        """
        try:
            data = message.get('data', {})
            item_id = data.get('item_id')
            local_id = data.get('local_id')
            responsavel_id = data.get('responsavel_id')
            status = data.get('status', 'disponivel')
            
            if not item_id:
                logger.warning("item_id não encontrado na mensagem de item atualizado")
                return
            
            async with self.async_session_maker() as session:
                repository = DevolucaoRepositoryImpl(session)
                await repository.upsert_item_reference(
                    item_id=item_id,
                    local_id=local_id or 0,
                    responsavel_id=responsavel_id or 0,
                    status=status
                )
                logger.info(f"Item {item_id} atualizado em devolução (status: {status})")
        except Exception as e:
            logger.error(f"Erro ao processar item atualizado: {e}")

    async def _handle_item_deletado(self, message: dict):
        """Processa quando um item é deletado
        Remove item da projeção de devolução para bloquear novas devoluções.
        """
        try:
            data = message.get('data', {})
            item_id = data.get('item_id')

            if not item_id:
                logger.warning("item_id não encontrado na mensagem de item deletado")
                return

            async with self.async_session_maker() as session:
                repository = DevolucaoRepositoryImpl(session)
                await repository.delete_item_reference(item_id=int(item_id))
                logger.info(f"Item {item_id} removido da projeção de devolução")
        except Exception as e:
            logger.error(f"Erro ao processar item deletado: {e}")
