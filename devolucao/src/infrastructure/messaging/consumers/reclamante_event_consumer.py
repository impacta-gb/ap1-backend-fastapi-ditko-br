"""
Consumer que processa eventos de reclamante para o serviço de Devolução
"""
import logging
import json
from sqlalchemy.ext.asyncio import async_sessionmaker
from devolucao.src.infrastructure.messaging.consumers.kafka_consumer import KafkaConsumer
from devolucao.src.infrastructure.database.config import engine
from devolucao.src.infrastructure.repositories.devolucao_repository_impl import DevolucaoRepositoryImpl

logger = logging.getLogger(__name__)


class ReclamanteEventConsumer(KafkaConsumer):
    """Consumer que escuta eventos de reclamante e sincroniza projeção"""
    
    def __init__(self):
        super().__init__(
            topics=['reclamante_events'],
            group_id='devolucao_reclamante_listener_group'
        )
        self.async_session_maker = async_sessionmaker(engine, expire_on_commit=False)
    
    async def handle_message(self, message: dict):
        """Processa eventos de reclamante"""
        try:
            event_type = message.get('event_type')
            
            if event_type == 'reclamante.criado':
                await self._handle_reclamante_criado(message)
            elif event_type == 'reclamante.atualizado':
                await self._handle_reclamante_atualizado(message)
            elif event_type == 'reclamante.deletado':
                await self._handle_reclamante_deletado(message)
            else:
                logger.debug(f"Tipo de evento não tratado: {event_type}")
        except Exception as e:
            logger.error(f"Erro ao processar mensagem de reclamante: {e}")
    
    async def _handle_reclamante_criado(self, message: dict):
        """Processa quando um reclamante é criado
        Sincroniza a projeção de reclamante em devolução
        """
        try:
            data = message.get('data', {})
            reclamante_id = data.get('reclamante_id')
            nome = data.get('nome')
            documento = data.get('documento')
            telefone = data.get('telefone')
            
            if not reclamante_id or not nome:
                logger.warning("Dados incompletos na mensagem de reclamante criado")
                return
            
            async with self.async_session_maker() as session:
                repository = DevolucaoRepositoryImpl(session)
                await repository.upsert_reclamante_reference(
                    reclamante_id=reclamante_id,
                    nome=nome,
                    documento=documento,
                    telefone=telefone
                )
                logger.info(f"Reclamante {reclamante_id} sincronizado em devolução")
        except Exception as e:
            logger.error(f"Erro ao processar reclamante criado: {e}")

    async def _handle_reclamante_atualizado(self, message: dict):
        """Processa quando um reclamante é atualizado
        Sincroniza informações do reclamante em devolução
        """
        try:
            data = message.get('data', {})
            reclamante_id = data.get('reclamante_id')
            nome = data.get('nome')
            documento = data.get('documento')
            telefone = data.get('telefone')
            
            if not reclamante_id or not nome:
                logger.warning("Dados incompletos na mensagem de reclamante atualizado")
                return
            
            async with self.async_session_maker() as session:
                repository = DevolucaoRepositoryImpl(session)
                await repository.upsert_reclamante_reference(
                    reclamante_id=reclamante_id,
                    nome=nome,
                    documento=documento,
                    telefone=telefone
                )
                logger.info(f"Reclamante {reclamante_id} atualizado em devolução")
        except Exception as e:
            logger.error(f"Erro ao processar reclamante atualizado: {e}")

    async def _handle_reclamante_deletado(self, message: dict):
        """Processa quando um reclamante é deletado e remove projeção local."""
        try:
            data = message.get('data', {})
            reclamante_id = data.get('reclamante_id')

            if not reclamante_id:
                logger.warning("reclamante_id não encontrado na mensagem de reclamante deletado")
                return

            async with self.async_session_maker() as session:
                repository = DevolucaoRepositoryImpl(session)
                await repository.delete_reclamante_reference(reclamante_id=int(reclamante_id))
                logger.info(f"Reclamante {reclamante_id} removido da projeção em devolução")
        except Exception as e:
            logger.error(f"Erro ao processar reclamante deletado: {e}")
