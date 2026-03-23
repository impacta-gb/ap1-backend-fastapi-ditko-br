"""
Consumer que processa eventos de devolução e atualiza status do item
"""
import logging
from item.src.infrastructure.messaging.consumers.kafka_consumer import KafkaConsumer
from item.src.infrastructure.database.config import async_session_maker
from item.src.infrastructure.repositories.item_repository_impl import ItemRepositoryImpl

logger = logging.getLogger(__name__)


class DevolucaoEventConsumer(KafkaConsumer):
    """Consumer que escuta eventos de devolução e atualiza item status"""
    
    def __init__(self):
        super().__init__(
            topics=['devolucao_events'],
            group_id='item_status_updater_group'
        )
    
    async def handle_message(self, message: dict):
        """Processa eventos de devolução"""
        try:
            event_type = message.get('event_type')
            
            if event_type == 'devolucao.criada':
                await self._handle_devolucao_criada(message)
            elif event_type == 'devolucao.atualizada':
                await self._handle_devolucao_atualizada(message)
            elif event_type == 'devolucao.deletada':
                await self._handle_devolucao_deletada(message)
            else:
                logger.debug(f"Tipo de evento não tratado: {event_type}")
        except Exception as e:
            logger.error(f"Erro ao processar mensagem de devolução: {e}")
    
    async def _handle_devolucao_criada(self, message: dict):
        """Atualiza status do item para 'devolvido' quando devolução é criada"""
        try:
            data = message.get('data', {})
            item_id = data.get('item_id')
            
            if not item_id:
                logger.warning("item_id não encontrado na mensagem de devolução")
                return
            
            # Abre sessão assíncrona de banco para atualizar o item.
            async with async_session_maker() as session:
                repository = ItemRepositoryImpl(session)
                
                # Buscar item
                item = await repository.get_by_id(item_id)
                if not item:
                    logger.warning(f"Item {item_id} não encontrado")
                    return
                
                # Atualizar status
                item.status = 'devolvido'
                await repository.update(item_id, item)
                
                logger.info(f"Item {item_id} status atualizado para 'devolvido' via evento de devolução")
        except Exception as e:
            logger.error(f"Erro ao atualizar item: {e}")

    async def _handle_devolucao_atualizada(self, message: dict):
        """Processa atualização de devolução."""
        try:
            data = message.get('data', {})
            devolucao_id = data.get('devolucao_id')
            item_id = data.get('item_id')
            logger.info(
                f"Devolução {devolucao_id} atualizada para item {item_id}; "
                "nenhuma alteração adicional de status necessária no Item"
            )
        except Exception as e:
            logger.error(f"Erro ao processar devolução atualizada: {e}")

    async def _handle_devolucao_deletada(self, message: dict):
        """Processa deleção de devolução."""
        try:
            data = message.get('data', {})
            devolucao_id = data.get('devolucao_id')
            item_id = data.get('item_id')
            logger.info(
                f"Devolução {devolucao_id} deletada para item {item_id}; "
                "evento recebido pelo módulo Item"
            )
        except Exception as e:
            logger.error(f"Erro ao processar devolução deletada: {e}")
