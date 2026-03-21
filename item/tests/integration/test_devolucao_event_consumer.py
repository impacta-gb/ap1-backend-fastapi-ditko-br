"""
Testes para o DevolucaoEventConsumer
"""
import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
from item.src.infrastructure.messaging.consumers.devolucao_event_consumer import DevolucaoEventConsumer


class TestDevolucaoEventConsumer:
    """Testes para DevolucaoEventConsumer"""
    
    @pytest.mark.asyncio
    async def test_consumer_initialization(self):
        """Testa inicialização do consumer"""
        consumer = DevolucaoEventConsumer()
        assert consumer.topics == ['devolucao_events']
        assert consumer.group_id == 'item_status_updater_group'
    
    @pytest.mark.asyncio
    async def test_handle_devolucao_criada_event(self):
        """Testa processamento de evento devolucao.criada"""
        consumer = DevolucaoEventConsumer()
        
        # Mock do evento
        event = {
            'event_type': 'devolucao.criada',
            'aggregate_id': '1',
            'data': {
                'devolucao_id': '1',
                'item_id': '123',
                'reclamante_id': '456'
            }
        }
        
        # Mockar o método _handle_devolucao_criada
        consumer._handle_devolucao_criada = AsyncMock()
        
        await consumer.handle_message(event)
        
        # Verificar que o método foi chamado
        consumer._handle_devolucao_criada.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_handle_unknown_event_type(self):
        """Testa que eventos desconhecidos são ignorados"""
        consumer = DevolucaoEventConsumer()
        
        event = {
            'event_type': 'unknown.event',
            'data': {}
        }
        
        # Não deve lançar exceção
        await consumer.handle_message(event)
    
    @pytest.mark.asyncio
    async def test_handle_message_with_error(self):
        """Testa tratamento de erros ao processar mensagem"""
        consumer = DevolucaoEventConsumer()
        
        # Mock que lança exceção
        consumer._handle_devolucao_criada = AsyncMock(side_effect=Exception("Erro de teste"))
        
        event = {
            'event_type': 'devolucao.criada',
            'data': {'item_id': '123'}
        }
        
        # Não deve lançar exceção (deve ser capturada e logada)
        await consumer.handle_message(event)
