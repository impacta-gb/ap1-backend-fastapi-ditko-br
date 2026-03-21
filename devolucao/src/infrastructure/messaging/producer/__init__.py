"""
Producer Kafka para publicar eventos do microserviço de Devolucao
"""
from devolucao.src.infrastructure.messaging.producer.kafka_producer import DevolucaoKafkaProducer

__all__ = ["DevolucaoKafkaProducer"]
