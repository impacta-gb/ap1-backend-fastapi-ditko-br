"""
Consumer base class para Kafka
Cada microserviço pode herdar dessa classe para processar eventos
"""
import json
import logging
import os
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class KafkaConsumer(ABC):
    """Classe base para consumers Kafka"""
    
    def __init__(self, topics: list, group_id: str):
        self.topics = topics
        self.group_id = group_id
        self.consumer = None
        self.running = False
    
    async def start(self):
        """Inicia o consumer e começa a escutar mensagens"""
        try:
            from aiokafka import AIOKafkaConsumer
            self.consumer = AIOKafkaConsumer(
                *self.topics,
                bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
                group_id=self.group_id,
                auto_offset_reset='earliest',
                value_deserializer=lambda m: json.loads(m.decode('utf-8'))
            )
            await self.consumer.start()
            self.running = True
            logger.info(f"Consumer {self.__class__.__name__} iniciado com sucesso")
            
            # Inicia background task para processar mensagens
            import asyncio
            asyncio.create_task(self._process_messages())
        except Exception as e:
            logger.warning(f"Consumer {self.__class__.__name__} não pôde conectar: {e}")
            self.consumer = None
            raise
    
    async def stop(self):
        """Para o consumer"""
        self.running = False
        if self.consumer:
            try:
                await self.consumer.stop()
                logger.info(f"Consumer {self.__class__.__name__} parado com sucesso")
            except Exception as e:
                logger.error(f"Erro ao parar Consumer {self.__class__.__name__}: {e}")
    
    async def _process_messages(self):
        """Loop para processar mensagens do Kafka"""
        if not self.consumer:
            return
        
        try:
            async for message in self.consumer:
                if not self.running:
                    break
                
                try:
                    await self.handle_message(message.value)
                except Exception as e:
                    logger.error(f"Erro ao processar mensagem: {e}")
        except Exception as e:
            logger.error(f"Erro no loop de processamento: {e}")
    
    @abstractmethod
    async def handle_message(self, message: dict):
        """
        Processa a mensagem recebida do Kafka
        Deve ser implementado por subclasses
        """
        pass
