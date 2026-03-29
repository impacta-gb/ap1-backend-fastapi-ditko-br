"""Bootstrap local de mensageria do módulo Devolução."""

import asyncio
import logging

from src.infrastructure.messaging.producer import DevolucaoKafkaProducer
from src.infrastructure.messaging.consumers import ItemEventConsumer, ReclamanteEventConsumer

logger = logging.getLogger(__name__)


class MessagingBootstrap:
    """Gerencia startup/shutdown de producer e consumers do módulo Devolução."""

    RETRY_ATTEMPTS = 10
    RETRY_DELAY_SECONDS = 2

    def __init__(self):
        self.devolucao_producer = DevolucaoKafkaProducer()
        self.item_event_consumer = ItemEventConsumer()
        self.reclamante_event_consumer = ReclamanteEventConsumer()

    async def _start_component(self, component, name: str, component_type: str):
        """Inicia producer/consumer com retry para aguardar Kafka saudável."""
        for attempt in range(1, self.RETRY_ATTEMPTS + 1):
            try:
                await component.start()
                logger.info(f"{name} Kafka {component_type} iniciado com sucesso")
                return
            except Exception as e:
                if attempt == self.RETRY_ATTEMPTS:
                    logger.warning(
                        f"{name} Kafka {component_type} não pôde ser conectado após {self.RETRY_ATTEMPTS} tentativas: {e}"
                    )
                    return

                logger.warning(
                    f"{name} Kafka {component_type} indisponível (tentativa {attempt}/{self.RETRY_ATTEMPTS}): {e}. "
                    f"Nova tentativa em {self.RETRY_DELAY_SECONDS}s"
                )
                await asyncio.sleep(self.RETRY_DELAY_SECONDS)

    async def start_producers(self):
        producers = [(self.devolucao_producer, "Devolucao")]
        for producer, name in producers:
            await self._start_component(producer, name, "Producer")

    async def start_consumers(self):
        consumers = [
            (self.item_event_consumer, "Devolucao Item Event"),
            (self.reclamante_event_consumer, "Devolucao Reclamante Event"),
        ]
        for consumer, name in consumers:
            await self._start_component(consumer, name, "Consumer")

    async def stop_producers(self):
        producers = [(self.devolucao_producer, "Devolucao")]
        for producer, name in producers:
            try:
                await producer.stop()
            except Exception as e:
                logger.error(f"Erro ao parar {name} Kafka Producer: {e}")

    async def stop_consumers(self):
        consumers = [
            (self.item_event_consumer, "Devolucao Item Event"),
            (self.reclamante_event_consumer, "Devolucao Reclamante Event"),
        ]
        for consumer, name in consumers:
            try:
                await consumer.stop()
            except Exception as e:
                logger.error(f"Erro ao parar {name} Consumer: {e}")
