"""
Producer Kafka para publicar eventos do microserviço de Devolucao
"""
import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class DevolucaoKafkaProducer:
    """Producer para publicar eventos de devolução no Kafka"""
    
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
            logger.info("DevolucaoKafkaProducer iniciado com sucesso")
        except Exception as e:
            logger.warning(f"DevolucaoKafkaProducer não pôde conectar: {e}")
            self.producer = None
    
    async def stop(self):
        """Para a conexão com Kafka"""
        if self.producer:
            try:
                await self.producer.stop()
                logger.info("DevolucaoKafkaProducer parado com sucesso")
            except Exception as e:
                logger.error(f"Erro ao parar DevolucaoKafkaProducer: {e}")
    
    async def publish_devolucao_criada(self, devolucao_id: int, item_id: int, reclamante_id: int):
        """Publica evento de devolução criada"""
        if not self.producer:
            logger.warning("Producer não está disponível")
            return
        
        try:
            event = {
                "event_type": "devolucao.criada",
                "aggregate_id": str(devolucao_id),
                "data": {
                    "devolucao_id": devolucao_id,
                    "item_id": item_id,
                    "reclamante_id": reclamante_id
                }
            }
            
            await self.producer.send_and_wait(
                "devolucao_events",
                json.dumps(event).encode('utf-8')
            )
            logger.info(f"Evento devolucao.criada publicado para devolução {devolucao_id}")
        except Exception as e:
            logger.error(f"Erro ao publicar evento devolucao.criada: {e}")
