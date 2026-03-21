"""
Producer Kafka para publicar eventos do microserviço de Local
"""
from local.src.infrastructure.messaging.producer.kafka_producer import LocalKafkaProducer

__all__ = ["LocalKafkaProducer"]
