"""
Testes para ResponsavelEventConsumer do módulo Reclamante
"""
import pytest
from unittest.mock import AsyncMock
from reclamante.src.infrastructure.messaging.consumers.responsavel_event_consumer import ResponsavelEventConsumer


class TestReclamanteResponsavelEventConsumer:
    """Testes para ResponsavelEventConsumer (Reclamante)"""
    
    @pytest.mark.asyncio
    async def test_consumer_initialization(self):
        """Testa inicialização do consumer"""
        consumer = ResponsavelEventConsumer()
        assert consumer.topics == ['responsavel_events']
        assert consumer.group_id == 'reclamante_responsavel_listener_group'
    
    @pytest.mark.asyncio
    async def test_handle_responsavel_criado_event(self):
        """Testa processamento de evento responsavel.criado"""
        consumer = ResponsavelEventConsumer()
        
        event = {
            'event_type': 'responsavel.criado',
            'aggregate_id': '1',
            'data': {
                'responsavel_id': '1',
                'nome': 'João Silva',
                'cargo': 'Gerente',
                'telefone': '11999999999'
            }
        }
        
        consumer._handle_responsavel_criado = AsyncMock()
        await consumer.handle_message(event)
        consumer._handle_responsavel_criado.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_handle_unknown_event_type(self):
        """Testa que eventos desconhecidos são ignorados"""
        consumer = ResponsavelEventConsumer()
        
        event = {
            'event_type': 'unknown.event',
            'data': {}
        }
        
        await consumer.handle_message(event)
    
    @pytest.mark.asyncio
    async def test_handle_message_with_error(self):
        """Testa tratamento de erros ao processar mensagem"""
        consumer = ResponsavelEventConsumer()
        
        consumer._handle_responsavel_criado = AsyncMock(side_effect=Exception("Erro de teste"))
        
        event = {
            'event_type': 'responsavel.criado',
            'data': {'responsavel_id': '1'}
        }
        
        await consumer.handle_message(event)
