"""
Consumer que processa eventos de item para o serviço de Reclamante
"""
import logging
from reclamante.src.infrastructure.messaging.consumers.kafka_consumer import KafkaConsumer

logger = logging.getLogger(__name__)


class ItemEventConsumer(KafkaConsumer):
    """Consumer que escuta eventos de item registrado"""
    
    def __init__(self):
        super().__init__(
            topics=['item_events'],
            group_id='reclamante_item_listener_group'
        )
    
    async def handle_message(self, message: dict):
        """Processa eventos de item"""
        try:
            event_type = message.get('event_type')
            
            if event_type == 'item.registrado':
                await self._handle_item_registrado(message)
            else:
                logger.debug(f"Tipo de evento não tratado: {event_type}")
        except Exception as e:
            logger.error(f"Erro ao processar mensagem de item: {e}")
    
    async def _handle_item_registrado(self, message: dict):
        """Processa quando um item é registrado
        Pode ser usado para sincronizar estado ou disparar fluxos de reclamação
        """
        try:
            data = message.get('data', {})
            item_id = data.get('item_id')
            
            if not item_id:
                logger.warning("item_id não encontrado na mensagem de item registrado")
                return
            
            # Implementar lógica de negócio específica
            logger.info(f"Item {item_id} foi registrado - Reclamante pode processar")
            
            # Exemplo: Você pode adicionar lógica para notificar reclamantes
            # ou dispara processos específicos relacionados ao item
            
        except Exception as e:
            logger.error(f"Erro ao processar item registrado: {e}")
