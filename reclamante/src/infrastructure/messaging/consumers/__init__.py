"""
Consumers para o microserviço de Reclamante
"""
from reclamante.src.infrastructure.messaging.consumers.item_event_consumer import ItemEventConsumer
from reclamante.src.infrastructure.messaging.consumers.responsavel_event_consumer import ResponsavelEventConsumer
from reclamante.src.infrastructure.messaging.consumers.devolucao_event_consumer import DevolucaoEventConsumer

__all__ = ["ItemEventConsumer", "ResponsavelEventConsumer", "DevolucaoEventConsumer"]
