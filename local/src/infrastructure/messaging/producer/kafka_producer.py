"""
Producer Kafka para publicar eventos do microserviço de Local
"""
import json
import logging
import os

logger = logging.getLogger(__name__)


class LocalKafkaProducer:
    """Producer para publicar eventos de local no Kafka"""
    
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
                bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
            )
            await self.producer.start()
            logger.info("LocalKafkaProducer iniciado com sucesso")
        except Exception as e:
            logger.warning(f"LocalKafkaProducer não pôde conectar: {e}")
            self.producer = None
    
    async def stop(self):
        """Para a conexão com Kafka"""
        if self.producer:
            try:
                await self.producer.stop()
                logger.info("LocalKafkaProducer parado com sucesso")
            except Exception as e:
                logger.error(f"Erro ao parar LocalKafkaProducer: {e}")

    async def _ensure_started(self):
        """Garante producer conectado antes de publicar."""
        if self.producer is None:
            await self.start()
    
    async def publish_local_criado(self, local_id: int, tipo: str, bairro: str, descricao: str):
        """Publica evento de local criado"""
        await self._ensure_started()
        if not self.producer:
            logger.warning("Producer não está disponível")
            return
        
        try:
            event = {
                "event_type": "local.criado",
                "aggregate_id": str(local_id),
                "data": {
                    "local_id": local_id,
                    "tipo": tipo,
                    "bairro": bairro,
                    "descricao": descricao
                }
            }
            
            await self.producer.send_and_wait(
                "local_events",
                json.dumps(event).encode('utf-8')
            )
            logger.info(f"Evento local.criado publicado para local {local_id}")
        except Exception as e:
            logger.error(f"Erro ao publicar evento local.criado: {e}")

    async def publish_local_atualizado(self, local_id: int, tipo: str, bairro: str, descricao: str):
        """Publica evento de local atualizado"""
        await self._ensure_started()
        if not self.producer:
            logger.warning("Producer não está disponível")
            return

        try:
            event = {
                "event_type": "local.atualizado",
                "aggregate_id": str(local_id),
                "data": {
                    "local_id": local_id,
                    "tipo": tipo,
                    "bairro": bairro,
                    "descricao": descricao
                }
            }

            await self.producer.send_and_wait(
                "local_events",
                json.dumps(event).encode('utf-8')
            )
            logger.info(f"Evento local.atualizado publicado para local {local_id}")
        except Exception as e:
            logger.error(f"Erro ao publicar evento local.atualizado: {e}")

    async def publish_local_deletado(self, local_id: int):
        """Publica evento de local deletado"""
        await self._ensure_started()
        if not self.producer:
            logger.warning("Producer não está disponível")
            return

        try:
            event = {
                "event_type": "local.deletado",
                "aggregate_id": str(local_id),
                "data": {
                    "local_id": local_id,
                }
            }

            await self.producer.send_and_wait(
                "local_events",
                json.dumps(event).encode('utf-8')
            )
            logger.info(f"Evento local.deletado publicado para local {local_id}")
        except Exception as e:
            logger.error(f"Erro ao publicar evento local.deletado: {e}")
