"""
Bootstrap de Producers e Consumers
Centraliza toda a lógica de inicialização de messaging (Kafka)
"""
import logging
from item.src.infrastructure.messaging.producer import ItemKafkaProducer
from devolucao.src.infrastructure.messaging.producer import DevolucaoKafkaProducer
from reclamante.src.infrastructure.messaging.producer import ReclamanteKafkaProducer
from responsavel.src.infrastructure.messaging.producer import ResponsavelKafkaProducer
from local.src.infrastructure.messaging.producer import LocalKafkaProducer
from item.src.infrastructure.messaging.consumers import DevolucaoEventConsumer, LocalEventConsumer as ItemLocalEventConsumer, ResponsavelEventConsumer as ItemResponsavelEventConsumer
from devolucao.src.infrastructure.messaging.consumers import ItemEventConsumer as DevolucaoItemEventConsumer, ReclamanteEventConsumer as DevolucaoReclamanteEventConsumer
from reclamante.src.infrastructure.messaging.consumers import ItemEventConsumer as ReclamanteItemEventConsumer, ResponsavelEventConsumer, DevolucaoEventConsumer as ReclamanteDevolucaoEventConsumer
from responsavel.src.infrastructure.messaging.consumers import ItemEventConsumer as ResponsavelItemEventConsumer
from local.src.infrastructure.messaging.consumers import ItemEventConsumer as LocalItemEventConsumer

logger = logging.getLogger(__name__)


class MessagingBootstrap:
    """Gerencia a inicialização e shutdown de producers e consumers"""
    
    def __init__(self):
        """Inicializa as instâncias de producers e consumers"""
        # Producers
        self.item_producer = ItemKafkaProducer()
        self.devolucao_producer = DevolucaoKafkaProducer()
        self.reclamante_producer = ReclamanteKafkaProducer()
        self.responsavel_producer = ResponsavelKafkaProducer()
        self.local_producer = LocalKafkaProducer()
        
        # Consumers
        self.devolucao_event_consumer = DevolucaoEventConsumer()
        self.item_local_event_consumer = ItemLocalEventConsumer()
        self.item_responsavel_event_consumer = ItemResponsavelEventConsumer()
        self.devolucao_item_event_consumer = DevolucaoItemEventConsumer()
        self.devolucao_reclamante_event_consumer = DevolucaoReclamanteEventConsumer()
        self.reclamante_item_event_consumer = ReclamanteItemEventConsumer()
        self.reclamante_responsavel_event_consumer = ResponsavelEventConsumer()
        self.reclamante_devolucao_event_consumer = ReclamanteDevolucaoEventConsumer()
        self.responsavel_item_event_consumer = ResponsavelItemEventConsumer()
        self.local_item_event_consumer = LocalItemEventConsumer()
    
    async def start_producers(self):
        """Inicia todos os producers"""
        producers = [
            (self.item_producer, "Item"),
            (self.devolucao_producer, "Devolucao"),
            (self.reclamante_producer, "Reclamante"),
            (self.responsavel_producer, "Responsavel"),
            (self.local_producer, "Local"),
        ]
        
        for producer, name in producers:
            try:
                await producer.start()
                logger.info(f"{name} Kafka Producer iniciado com sucesso")
            except Exception as e:
                logger.warning(f"{name} Kafka Producer não pôde ser conectado: {e}")
    
    async def start_consumers(self):
        """Inicia todos os consumers"""
        consumers = [
            (self.devolucao_event_consumer, "Devolucao Event"),
            (self.item_local_event_consumer, "Item Local Event"),
            (self.item_responsavel_event_consumer, "Item Responsavel Event"),
            (self.devolucao_item_event_consumer, "Devolucao Item Event"),
            (self.devolucao_reclamante_event_consumer, "Devolucao Reclamante Event"),
            (self.reclamante_item_event_consumer, "Reclamante Item Event"),
            (self.reclamante_responsavel_event_consumer, "Reclamante Responsavel Event"),
            (self.reclamante_devolucao_event_consumer, "Reclamante Devolucao Event"),
            (self.responsavel_item_event_consumer, "Responsavel Item Event"),
            (self.local_item_event_consumer, "Local Item Event"),
        ]
        
        for consumer, name in consumers:
            try:
                await consumer.start()
                logger.info(f"{name} Consumer iniciado com sucesso")
            except Exception as e:
                logger.warning(f"{name} Consumer não pôde ser conectado: {e}")
    
    async def stop_producers(self):
        """Para todos os producers"""
        producers = [
            (self.item_producer, "Item"),
            (self.devolucao_producer, "Devolucao"),
            (self.reclamante_producer, "Reclamante"),
            (self.responsavel_producer, "Responsavel"),
            (self.local_producer, "Local"),
        ]
        
        for producer, name in producers:
            try:
                await producer.stop()
            except Exception as e:
                logger.error(f"Erro ao parar {name} Kafka Producer: {e}")
    
    async def stop_consumers(self):
        """Para todos os consumers"""
        consumers = [
            (self.devolucao_event_consumer, "Devolucao Event"),
            (self.item_local_event_consumer, "Item Local Event"),
            (self.item_responsavel_event_consumer, "Item Responsavel Event"),
            (self.devolucao_item_event_consumer, "Devolucao Item Event"),
            (self.devolucao_reclamante_event_consumer, "Devolucao Reclamante Event"),
            (self.reclamante_item_event_consumer, "Reclamante Item Event"),
            (self.reclamante_responsavel_event_consumer, "Reclamante Responsavel Event"),
            (self.reclamante_devolucao_event_consumer, "Reclamante Devolucao Event"),
            (self.responsavel_item_event_consumer, "Responsavel Item Event"),
            (self.local_item_event_consumer, "Local Item Event"),
        ]
        
        for consumer, name in consumers:
            try:
                await consumer.stop()
            except Exception as e:
                logger.error(f"Erro ao parar {name} Consumer: {e}")
