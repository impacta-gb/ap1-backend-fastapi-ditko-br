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

    async def _ensure_started(self):
        """Garante producer conectado antes de publicar."""
        if self.producer is None:
            await self.start()
    
    async def publish_responsavel_criado(self, responsavel_id: int, nome: str, cargo: str, telefone: str):
        """Publica evento de responsável criado"""
        await self._ensure_started()
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

    async def publish_responsavel_atualizado(self, responsavel_id: int, nome: str, cargo: str, telefone: str, ativo: bool):
        """Publica evento de responsável atualizado"""
        await self._ensure_started()
        if not self.producer:
            logger.warning("Producer não está disponível")
            return

        try:
            event = {
                "event_type": "responsavel.atualizado",
                "aggregate_id": str(responsavel_id),
                "data": {
                    "responsavel_id": responsavel_id,
                    "nome": nome,
                    "cargo": cargo,
                    "telefone": telefone,
                    "ativo": ativo
                }
            }

            await self.producer.send_and_wait(
                "responsavel_events",
                json.dumps(event).encode('utf-8')
            )
            logger.info(f"Evento responsavel.atualizado publicado para responsável {responsavel_id}")
        except Exception as e:
            logger.error(f"Erro ao publicar evento responsavel.atualizado: {e}")

    async def publish_responsavel_status_alterado(self, responsavel_id: int, nome: str, cargo: str, telefone: str, ativo: bool):
        """Publica evento de alteração de status de responsável"""
        await self._ensure_started()
        if not self.producer:
            logger.warning("Producer não está disponível")
            return

        try:
            event = {
                "event_type": "responsavel.status_alterado",
                "aggregate_id": str(responsavel_id),
                "data": {
                    "responsavel_id": responsavel_id,
                    "nome": nome,
                    "cargo": cargo,
                    "telefone": telefone,
                    "ativo": ativo
                }
            }

            await self.producer.send_and_wait(
                "responsavel_events",
                json.dumps(event).encode('utf-8')
            )
            logger.info(f"Evento responsavel.status_alterado publicado para responsável {responsavel_id}")
        except Exception as e:
            logger.error(f"Erro ao publicar evento responsavel.status_alterado: {e}")

    async def publish_responsavel_deletado(self, responsavel_id: int):
        """Publica evento de responsável deletado"""
        await self._ensure_started()
        if not self.producer:
            logger.warning("Producer não está disponível")
            return

        try:
            event = {
                "event_type": "responsavel.deletado",
                "aggregate_id": str(responsavel_id),
                "data": {
                    "responsavel_id": responsavel_id,
                }
            }

            await self.producer.send_and_wait(
                "responsavel_events",
                json.dumps(event).encode('utf-8')
            )
            logger.info(f"Evento responsavel.deletado publicado para responsável {responsavel_id}")
        except Exception as e:
            logger.error(f"Erro ao publicar evento responsavel.deletado: {e}")
