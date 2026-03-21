"""
Producer Kafka para publicar eventos do microserviço de Reclamante
"""
from reclamante.src.infrastructure.messaging.producer.kafka_producer import ReclamanteKafkaProducer

__all__ = ["ReclamanteKafkaProducer"]
