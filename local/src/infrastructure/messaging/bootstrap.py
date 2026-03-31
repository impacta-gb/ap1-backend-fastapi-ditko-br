"""Bootstrap local de mensageria do módulo Local."""

import asyncio
import logging

from src.infrastructure.messaging.producer import LocalKafkaProducer
from src.infrastructure.messaging.consumers import ItemEventConsumer

logger = logging.getLogger(__name__)


class MessagingBootstrap:
    """Gerencia startup/shutdown de producer e consumers do módulo Local."""

    RETRY_ATTEMPTS = 10
    RETRY_DELAY_SECONDS = 2

    def __init__(self):
        self.local_producer = LocalKafkaProducer()
        self.item_event_consumer = ItemEventConsumer()

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
        producers = [(self.local_producer, "Local")]
        for producer, name in producers:
            await self._start_component(producer, name, "Producer")

    async def start_consumers(self):
        consumers = [(self.item_event_consumer, "Local Item Event")]
        for consumer, name in consumers:
            await self._start_component(consumer, name, "Consumer")

    async def stop_producers(self):
        producers = [(self.local_producer, "Local")]
        for producer, name in producers:
            try:
                await producer.stop()
            except Exception as e:
                logger.error(f"Erro ao parar {name} Kafka Producer: {e}")

    async def stop_consumers(self):
        consumers = [(self.item_event_consumer, "Local Item Event")]
        for consumer, name in consumers:
            try:
                await consumer.stop()
            except Exception as e:
                logger.error(f"Erro ao parar {name} Consumer: {e}")
