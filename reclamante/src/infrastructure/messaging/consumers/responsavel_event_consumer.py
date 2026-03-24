"""
Consumer que processa eventos de responsável para o serviço de Reclamante
"""
import logging
from reclamante.src.infrastructure.messaging.consumers.kafka_consumer import KafkaConsumer

logger = logging.getLogger(__name__)


class ResponsavelEventConsumer(KafkaConsumer):
    """Consumer que escuta eventos de responsável registrado"""
    
    def __init__(self):
        super().__init__(
            topics=['responsavel_events'],
            group_id='reclamante_responsavel_listener_group'
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
        """Processa quando um responsável é criado"""
        try:
            data = message.get('data', {})
            responsavel_id = data.get('responsavel_id')
            nome = data.get('nome')
            
            if not responsavel_id:
                logger.warning("responsavel_id não encontrado na mensagem")
                return
            
            # Implementar lógica de negócio específica
            logger.info(f"Responsável {responsavel_id} ({nome}) foi criado no sistema")
            
            # Exemplo: Você pode adicionar lógica para sincronizar dados
            # ou disparar processos relacionados ao responsável
            
        except Exception as e:
            logger.error(f"Erro ao processar responsável criado: {e}")

    async def _handle_responsavel_atualizado(self, message: dict):
        """Processa quando um responsável é atualizado ou tem status alterado."""
        try:
            data = message.get('data', {})
            responsavel_id = data.get('responsavel_id')
            if not responsavel_id:
                logger.warning("responsavel_id não encontrado na mensagem de atualização")
                return
            logger.info(f"Responsável {responsavel_id} atualizado/status alterado no sistema")
        except Exception as e:
            logger.error(f"Erro ao processar responsável atualizado: {e}")

    async def _handle_responsavel_deletado(self, message: dict):
        """Processa quando um responsável é deletado."""
        try:
            data = message.get('data', {})
            responsavel_id = data.get('responsavel_id')
            if not responsavel_id:
                logger.warning("responsavel_id não encontrado na mensagem de deleção")
                return
            logger.info(f"Responsável {responsavel_id} deletado no sistema")
        except Exception as e:
            logger.error(f"Erro ao processar responsável deletado: {e}")
