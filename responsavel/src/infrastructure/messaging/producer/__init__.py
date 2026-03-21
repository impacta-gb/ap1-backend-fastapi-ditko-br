"""
Producer Kafka para publicar eventos do microserviço de Responsavel
"""
from responsavel.src.infrastructure.messaging.producer.kafka_producer import ResponsavelKafkaProducer

__all__ = ["ResponsavelKafkaProducer"]
