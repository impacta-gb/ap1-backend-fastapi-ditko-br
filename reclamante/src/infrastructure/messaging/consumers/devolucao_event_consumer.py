"""
Consumer que processa eventos de devolução para o serviço de Reclamante
"""
import logging
from reclamante.src.infrastructure.messaging.consumers.kafka_consumer import KafkaConsumer

logger = logging.getLogger(__name__)


class DevolucaoEventConsumer(KafkaConsumer):
    """Consumer que escuta eventos de devolução realizada"""
    
    def __init__(self):
        super().__init__(
            topics=['devolucao_events'],
            group_id='reclamante_devolucao_listener_group'
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
        """Processa quando uma devolução é criada
        Pode ser usado para atualizar status ou disparar notificações
        """
        try:
            data = message.get('data', {})
            devolucao_id = data.get('devolucao_id')
            reclamante_id = data.get('reclamante_id')
            item_id = data.get('item_id')
            
            if not devolucao_id:
                logger.warning("devolucao_id não encontrado na mensagem de devolução criada")
                return
            
            # Implementar lógica de negócio específica
            logger.info(f"Devolução {devolucao_id} criada para Reclamante {reclamante_id} - Item {item_id}")
            
            # Exemplo: Você pode adicionar lógica para:
            # - Atualizar status do reclamante (item recuperado)
            # - Enviar notificação/confirmação para o reclamante
            # - Registrar histórico de devoluções realizadas
            
        except Exception as e:
            logger.error(f"Erro ao processar devolução criada: {e}")
