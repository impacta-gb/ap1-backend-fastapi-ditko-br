"""
Consumers para o microserviço de Devolução
"""
from devolucao.src.infrastructure.messaging.consumers.item_event_consumer import ItemEventConsumer
from devolucao.src.infrastructure.messaging.consumers.reclamante_event_consumer import ReclamanteEventConsumer

__all__ = ["ItemEventConsumer", "ReclamanteEventConsumer"]
