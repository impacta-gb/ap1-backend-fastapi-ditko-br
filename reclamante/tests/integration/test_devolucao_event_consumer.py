"""
Testes para DevolucaoEventConsumer do módulo Reclamante
"""
import pytest
from unittest.mock import AsyncMock
from reclamante.src.infrastructure.messaging.consumers.devolucao_event_consumer import DevolucaoEventConsumer


class TestReclamanteDevolucaoEventConsumer:
    """Testes para DevolucaoEventConsumer (Reclamante)"""
    
    @pytest.mark.asyncio
    async def test_consumer_initialization(self):
        """Testa inicialização do consumer"""
        consumer = DevolucaoEventConsumer()
        assert consumer.topics == ['devolucao_events']
        assert consumer.group_id == 'reclamante_devolucao_listener_group'
    
    @pytest.mark.asyncio
    async def test_handle_devolucao_criada_event(self):
        """Testa processamento de evento devolucao.criada"""
        consumer = DevolucaoEventConsumer()
        
        event = {
            'event_type': 'devolucao.criada',
            'aggregate_id': '1',
            'data': {
                'devolucao_id': '1',
                'item_id': '123',
                'reclamante_id': '456'
            }
        }
        
        consumer._handle_devolucao_criada = AsyncMock()
        await consumer.handle_message(event)
        consumer._handle_devolucao_criada.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_handle_unknown_event_type(self):
        """Testa que eventos desconhecidos são ignorados"""
        consumer = DevolucaoEventConsumer()
        
        event = {
            'event_type': 'unknown.event',
            'data': {}
        }
        
        await consumer.handle_message(event)
    
    @pytest.mark.asyncio
    async def test_handle_message_with_error(self):
        """Testa tratamento de erros ao processar mensagem"""
        consumer = DevolucaoEventConsumer()
        
        consumer._handle_devolucao_criada = AsyncMock(side_effect=Exception("Erro de teste"))
        
        event = {
            'event_type': 'devolucao.criada',
            'data': {'item_id': '123'}
        }
        
        await consumer.handle_message(event)
