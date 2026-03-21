"""
Producer Kafka para publicar eventos do microserviço de Responsavel
"""
import json
import logging

logger = logging.getLogger(__name__)


class ResponsavelKafkaProducer:
    """Producer para publicar eventos de responsável no Kafka"""
    
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
            logger.info("ResponsavelKafkaProducer iniciado com sucesso")
        except Exception as e:
            logger.warning(f"ResponsavelKafkaProducer não pôde conectar: {e}")
            self.producer = None
    
    async def stop(self):
        """Para a conexão com Kafka"""
        if self.producer:
            try:
                await self.producer.stop()
                logger.info("ResponsavelKafkaProducer parado com sucesso")
            except Exception as e:
                logger.error(f"Erro ao parar ResponsavelKafkaProducer: {e}")
    
    async def publish_responsavel_criado(self, responsavel_id: int, nome: str, cargo: str, telefone: str):
        """Publica evento de responsável criado"""
        if not self.producer:
            logger.warning("Producer não está disponível")
            return
        
        try:
            event = {
                "event_type": "responsavel.criado",
                "aggregate_id": str(responsavel_id),
                "data": {
                    "responsavel_id": responsavel_id,
                    "nome": nome,
                    "cargo": cargo,
                    "telefone": telefone
                }
            }
            
            await self.producer.send_and_wait(
                "responsavel_events",
                json.dumps(event).encode('utf-8')
            )
            logger.info(f"Evento responsavel.criado publicado para responsável {responsavel_id}")
        except Exception as e:
            logger.error(f"Erro ao publicar evento responsavel.criado: {e}")
