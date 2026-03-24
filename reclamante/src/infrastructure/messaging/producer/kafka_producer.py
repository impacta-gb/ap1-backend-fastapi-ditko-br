"""
Producer Kafka para publicar eventos do microserviço de Reclamante
"""
import json
import logging

logger = logging.getLogger(__name__)


class ReclamanteKafkaProducer:
    """Producer para publicar eventos de reclamante no Kafka"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.producer = None
    
    async def start(self):
        """Inicia a conexão com Kafka"""
        try:
            from aiokafka import AIOKafkaProducer
            self.producer = AIOKafkaProducer(
                bootstrap_servers='localhost:9092'
            )
            await self.producer.start()
            logger.info("ReclamanteKafkaProducer iniciado com sucesso")
        except Exception as e:
            logger.warning(f"ReclamanteKafkaProducer não pôde conectar: {e}")
            self.producer = None
    
    async def stop(self):
        """Para a conexão com Kafka"""
        if self.producer:
            try:
                await self.producer.stop()
                logger.info("ReclamanteKafkaProducer parado com sucesso")
            except Exception as e:
                logger.error(f"Erro ao parar ReclamanteKafkaProducer: {e}")

    async def _ensure_started(self):
        """Garante producer conectado antes de publicar."""
        if self.producer is None:
            await self.start()
    
    async def publish_reclamante_criado(self, reclamante_id: int, nome: str, documento: str, telefone: str):
        """Publica evento de reclamante criado"""
        await self._ensure_started()
        if not self.producer:
            logger.warning("Producer não está disponível")
            return
        
        try:
            event = {
                "event_type": "reclamante.criado",
                "aggregate_id": str(reclamante_id),
                "data": {
                    "reclamante_id": reclamante_id,
                    "nome": nome,
                    "documento": documento,
                    "telefone": telefone
                }
            }
            
            await self.producer.send_and_wait(
                "reclamante_events",
                json.dumps(event).encode('utf-8')
            )
            logger.info(f"Evento reclamante.criado publicado para reclamante {reclamante_id}")
        except Exception as e:
            logger.error(f"Erro ao publicar evento reclamante.criado: {e}")

    async def publish_reclamante_atualizado(self, reclamante_id: int, nome: str, documento: str, telefone: str):
        """Publica evento de reclamante atualizado"""
        await self._ensure_started()
        if not self.producer:
            logger.warning("Producer não está disponível")
            return

        try:
            event = {
                "event_type": "reclamante.atualizado",
                "aggregate_id": str(reclamante_id),
                "data": {
                    "reclamante_id": reclamante_id,
                    "nome": nome,
                    "documento": documento,
                    "telefone": telefone
                }
            }

            await self.producer.send_and_wait(
                "reclamante_events",
                json.dumps(event).encode('utf-8')
            )
            logger.info(f"Evento reclamante.atualizado publicado para reclamante {reclamante_id}")
        except Exception as e:
            logger.error(f"Erro ao publicar evento reclamante.atualizado: {e}")

    async def publish_reclamante_deletado(self, reclamante_id: int):
        """Publica evento de reclamante deletado"""
        await self._ensure_started()
        if not self.producer:
            logger.warning("Producer não está disponível")
            return

        try:
            event = {
                "event_type": "reclamante.deletado",
                "aggregate_id": str(reclamante_id),
                "data": {
                    "reclamante_id": reclamante_id,
                }
            }

            await self.producer.send_and_wait(
                "reclamante_events",
                json.dumps(event).encode('utf-8')
            )
            logger.info(f"Evento reclamante.deletado publicado para reclamante {reclamante_id}")
        except Exception as e:
            logger.error(f"Erro ao publicar evento reclamante.deletado: {e}")
