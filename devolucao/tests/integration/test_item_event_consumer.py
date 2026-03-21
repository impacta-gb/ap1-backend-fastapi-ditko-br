"""
Testes para ItemEventConsumer do módulo Devolução
"""
import pytest
from unittest.mock import AsyncMock
from devolucao.src.infrastructure.messaging.consumers.item_event_consumer import ItemEventConsumer


class TestDevolucaoItemEventConsumer:
    """Testes para ItemEventConsumer (Devolução)"""
    
    @pytest.mark.asyncio
    async def test_consumer_initialization(self):
        """Testa inicialização do consumer"""
        consumer = ItemEventConsumer()
        assert consumer.topics == ['item_events']
        assert consumer.group_id == 'devolucao_item_listener_group'
    
    @pytest.mark.asyncio
    async def test_handle_item_registrado_event(self):
        """Testa processamento de evento item.registrado"""
        consumer = ItemEventConsumer()
        
        # Mock do evento
        event = {
            'event_type': 'item.registrado',
            'aggregate_id': '123',
            'data': {
                'item_id': '123',
                'descricao': 'Item de teste',
                'status': 'disponivel',
                'local_id': '1',
                'responsavel_id': '1'
            }
        }
        
        # Mockar o método _handle_item_registrado
        consumer._handle_item_registrado = AsyncMock()
        
        await consumer.handle_message(event)
        
        # Verificar que o método foi chamado
        consumer._handle_item_registrado.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_handle_unknown_event_type(self):
        """Testa que eventos desconhecidos são ignorados"""
        consumer = ItemEventConsumer()
        
        event = {
            'event_type': 'unknown.event',
            'data': {}
        }
        
        # Não deve lançar exceção
        await consumer.handle_message(event)
    
    @pytest.mark.asyncio
    async def test_handle_message_with_error(self):
        """Testa tratamento de erros ao processar mensagem"""
        consumer = ItemEventConsumer()
        
        # Mock que lança exceção
        consumer._handle_item_registrado = AsyncMock(side_effect=Exception("Erro de teste"))
        
        event = {
            'event_type': 'item.registrado',
            'data': {'item_id': '123'}
        }
        
        # Não deve lançar exceção (deve ser capturada e logada)
        await consumer.handle_message(event)
