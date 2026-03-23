"""
Producer Kafka para publicar eventos do microserviço de Item
"""
import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class ItemKafkaProducer:
    """Producer para publicar eventos de item no Kafka"""
    
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
            logger.info("ItemKafkaProducer iniciado com sucesso")
        except Exception as e:
            logger.warning(f"ItemKafkaProducer não pôde conectar: {e}")
            self.producer = None

    async def _ensure_started(self):
        """Garante que o producer está conectado antes de publicar eventos."""
        if self.producer is None:
            await self.start()
    
    async def stop(self):
        """Para a conexão com Kafka"""
        if self.producer:
            try:
                await self.producer.stop()
                logger.info("ItemKafkaProducer parado com sucesso")
            except Exception as e:
                logger.error(f"Erro ao parar ItemKafkaProducer: {e}")
    
    async def publish_item_criado(self, item_id: int, descricao: str, status: str, local_id: int, responsavel_id: int):
        """Publica evento de item criado"""
        await self._ensure_started()
        if not self.producer:
            logger.warning("Producer não está disponível")
            return
        
        try:
            event = {
                "event_type": "item.criado",
                "aggregate_id": str(item_id),
                "data": {
                    "item_id": item_id,
                    "descricao": descricao,
                    "status": status,
                    "local_id": local_id,
                    "responsavel_id": responsavel_id
                }
            }
            
            await self.producer.send_and_wait(
                "item_events",
                json.dumps(event).encode('utf-8')
            )
            logger.info(f"Evento item.criado publicado para item {item_id}")
        except Exception as e:
            logger.warning(f"Falha ao publicar item.criado, tentando reconectar: {e}")
            self.producer = None
            await self._ensure_started()
            if not self.producer:
                logger.error("Erro ao publicar evento item.criado: producer indisponível após reconexão")
                return
            try:
                event = {
                    "event_type": "item.criado",
                    "aggregate_id": str(item_id),
                    "data": {
                        "item_id": item_id,
                        "descricao": descricao,
                        "status": status,
                        "local_id": local_id,
                        "responsavel_id": responsavel_id
                    }
                }
                await self.producer.send_and_wait(
                    "item_events",
                    json.dumps(event).encode('utf-8')
                )
                logger.info(f"Evento item.criado publicado para item {item_id} (após reconexão)")
            except Exception as retry_error:
                logger.error(f"Erro ao publicar evento item.criado após reconexão: {retry_error}")

    async def publish_item_atualizado(self, item_id: int, descricao: str, status: str, local_id: int, responsavel_id: int):
        """Publica evento de item atualizado"""
        await self._ensure_started()
        if not self.producer:
            logger.warning("Producer não está disponível")
            return
        
        try:
            event = {
                "event_type": "item.atualizado",
                "aggregate_id": str(item_id),
                "data": {
                    "item_id": item_id,
                    "descricao": descricao,
                    "status": status,
                    "local_id": local_id,
                    "responsavel_id": responsavel_id
                }
            }
            
            await self.producer.send_and_wait(
                "item_events",
                json.dumps(event).encode('utf-8')
            )
            logger.info(f"Evento item.atualizado publicado para item {item_id}")
        except Exception as e:
            logger.warning(f"Falha ao publicar item.atualizado, tentando reconectar: {e}")
            self.producer = None
            await self._ensure_started()
            if not self.producer:
                logger.error("Erro ao publicar evento item.atualizado: producer indisponível após reconexão")
                return
            try:
                event = {
                    "event_type": "item.atualizado",
                    "aggregate_id": str(item_id),
                    "data": {
                        "item_id": item_id,
                        "descricao": descricao,
                        "status": status,
                        "local_id": local_id,
                        "responsavel_id": responsavel_id
                    }
                }
                await self.producer.send_and_wait(
                    "item_events",
                    json.dumps(event).encode('utf-8')
                )
                logger.info(f"Evento item.atualizado publicado para item {item_id} (após reconexão)")
            except Exception as retry_error:
                logger.error(f"Erro ao publicar evento item.atualizado após reconexão: {retry_error}")

    async def publish_item_deletado(self, item_id: int):
        """Publica evento de item deletado"""
        await self._ensure_started()
        if not self.producer:
            logger.warning("Producer não está disponível")
            return

        try:
            event = {
                "event_type": "item.deletado",
                "aggregate_id": str(item_id),
                "data": {
                    "item_id": item_id,
                }
            }

            await self.producer.send_and_wait(
                "item_events",
                json.dumps(event).encode('utf-8')
            )
            logger.info(f"Evento item.deletado publicado para item {item_id}")
        except Exception as e:
            logger.warning(f"Falha ao publicar item.deletado, tentando reconectar: {e}")
            self.producer = None
            await self._ensure_started()
            if not self.producer:
                logger.error("Erro ao publicar evento item.deletado: producer indisponível após reconexão")
                return
            try:
                event = {
                    "event_type": "item.deletado",
                    "aggregate_id": str(item_id),
                    "data": {
                        "item_id": item_id,
                    }
                }
                await self.producer.send_and_wait(
                    "item_events",
                    json.dumps(event).encode('utf-8')
                )
                logger.info(f"Evento item.deletado publicado para item {item_id} (após reconexão)")
            except Exception as retry_error:
                logger.error(f"Erro ao publicar evento item.deletado após reconexão: {retry_error}")
