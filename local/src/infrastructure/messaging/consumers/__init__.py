"""
Consumers para o microserviço de Local
"""
from local.src.infrastructure.messaging.consumers.item_event_consumer import ItemEventConsumer

__all__ = ["ItemEventConsumer"]
