"""
Consumers para o microserviço de Devolução
"""
from devolucao.src.infrastructure.messaging.consumers.item_event_consumer import ItemEventConsumer

__all__ = ["ItemEventConsumer"]
