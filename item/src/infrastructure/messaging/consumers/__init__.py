"""
Módulo de consumers para o microserviço de Item
"""
from item.src.infrastructure.messaging.consumers.devolucao_event_consumer import DevolucaoEventConsumer
from item.src.infrastructure.messaging.consumers.local_event_consumer import LocalEventConsumer
from item.src.infrastructure.messaging.consumers.responsavel_event_consumer import ResponsavelEventConsumer

__all__ = ['DevolucaoEventConsumer', 'LocalEventConsumer', 'ResponsavelEventConsumer']
