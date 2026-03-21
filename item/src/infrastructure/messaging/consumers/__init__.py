"""
Módulo de consumers para o microserviço de Item
"""
from item.src.infrastructure.messaging.consumers.devolucao_event_consumer import DevolucaoEventConsumer

__all__ = ['DevolucaoEventConsumer']
