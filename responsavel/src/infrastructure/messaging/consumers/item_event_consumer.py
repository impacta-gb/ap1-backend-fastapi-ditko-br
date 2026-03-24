"""
Consumer que processa eventos de item para o serviço de Responsavel
"""
import logging
from responsavel.src.infrastructure.messaging.consumers.kafka_consumer import KafkaConsumer

logger = logging.getLogger(__name__)


class ItemEventConsumer(KafkaConsumer):
    """Consumer que escuta eventos de item"""
    
    def __init__(self):
        super().__init__(
            topics=['item_events'],
            group_id='responsavel_item_listener_group'
        )
    
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
        """Processa quando um item é criado."""
        try:
            data = message.get('data', {})
            item_id = data.get('item_id')
            responsavel_id = data.get('responsavel_id')
            
            if not item_id:
                logger.warning("item_id não encontrado na mensagem de item criado")
                return
            
            # Implementar lógica de negócio específica
            logger.info(f"Item {item_id} foi criado por Responsável {responsavel_id}")
            
            # Exemplo: Você pode adicionar lógica para:
            # - Atualizar histórico de itens registrados por responsável
            # - Sincronizar dados de responsáveis
            # - Disparar notificações ou validações
            
        except Exception as e:
            logger.error(f"Erro ao processar item criado: {e}")

    async def _handle_item_atualizado(self, message: dict):
        """Processa quando um item é atualizado."""
        try:
            data = message.get('data', {})
            item_id = data.get('item_id')
            responsavel_id = data.get('responsavel_id')
            if not item_id:
                logger.warning("item_id não encontrado na mensagem de item atualizado")
                return
            logger.info(f"Item {item_id} foi atualizado por Responsável {responsavel_id}")
        except Exception as e:
            logger.error(f"Erro ao processar item atualizado: {e}")

    async def _handle_item_deletado(self, message: dict):
        """Processa quando um item é deletado."""
        try:
            item_id = message.get('data', {}).get('item_id')
            if not item_id:
                logger.warning("item_id não encontrado na mensagem de item deletado")
                return
            logger.info(f"Item {item_id} foi deletado - Responsável pode processar")
        except Exception as e:
            logger.error(f"Erro ao processar item deletado: {e}")
