"""
Testes para ItemEventConsumer do módulo Reclamante
"""
import pytest
from unittest.mock import AsyncMock
from reclamante.src.infrastructure.messaging.consumers.item_event_consumer import ItemEventConsumer


class TestReclamanteItemEventConsumer:
    """Testes para ItemEventConsumer (Reclamante)"""
    
    @pytest.mark.asyncio
    async def test_consumer_initialization(self):
        """Testa inicialização do consumer"""
        consumer = ItemEventConsumer()
        assert consumer.topics == ['item_events']
        assert consumer.group_id == 'reclamante_item_listener_group'
    
    @pytest.mark.asyncio
    async def test_handle_item_registrado_event(self):
        """Testa processamento de evento item.criado"""
        consumer = ItemEventConsumer()
        
        event = {
            'event_type': 'item.criado',
            'aggregate_id': '123',
            'data': {
                'item_id': '123',
                'descricao': 'Item de teste',
                'status': 'disponivel'
            }
        }
        
        consumer._handle_item_criado = AsyncMock()
        await consumer.handle_message(event)
        consumer._handle_item_criado.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_handle_unknown_event_type(self):
        """Testa que eventos desconhecidos são ignorados"""
        consumer = ItemEventConsumer()
        
        event = {
            'event_type': 'unknown.event',
            'data': {}
        }
        
        await consumer.handle_message(event)
    
    @pytest.mark.asyncio
    async def test_handle_message_with_error(self):
        """Testa tratamento de erros ao processar mensagem"""
        consumer = ItemEventConsumer()
        
        consumer._handle_item_criado = AsyncMock(side_effect=Exception("Erro de teste"))
        
        event = {
            'event_type': 'item.criado',
            'data': {'item_id': '123'}
        }
        
        await consumer.handle_message(event)
