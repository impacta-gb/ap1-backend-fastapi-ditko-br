"""
Producer Kafka para publicar eventos do microserviço de Item
"""
from item.src.infrastructure.messaging.producer.kafka_producer import ItemKafkaProducer

__all__ = ["ItemKafkaProducer"]
