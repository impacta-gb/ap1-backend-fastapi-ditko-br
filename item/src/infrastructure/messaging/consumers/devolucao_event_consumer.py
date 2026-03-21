"""
Consumer que processa eventos de devolução e atualiza status do item
"""
import logging
from item.src.infrastructure.messaging.consumers.kafka_consumer import KafkaConsumer
from item.src.infrastructure.database.config import get_session
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
            
            # Obter sessão do banco de dados
            async with get_session() as session:
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
