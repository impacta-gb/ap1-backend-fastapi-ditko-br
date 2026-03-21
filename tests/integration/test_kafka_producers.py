"""
Testes para todos os Kafka Producers
Verifica que cada producer funciona corretamente e é um Singleton
"""
import pytest
from unittest.mock import AsyncMock, patch


class TestItemKafkaProducer:
    """Testes para ItemKafkaProducer"""
    
    @pytest.mark.asyncio
    async def test_item_producer_initialization(self):
        """Testa inicialização do ItemKafkaProducer"""
        from item.src.infrastructure.messaging.producer import ItemKafkaProducer
        
        producer = ItemKafkaProducer()
        assert producer is not None
        assert hasattr(producer, 'producer')
    
    @pytest.mark.asyncio
    async def test_item_producer_singleton(self):
        """Testa que ItemKafkaProducer é singleton"""
        from item.src.infrastructure.messaging.producer import ItemKafkaProducer
        
        producer1 = ItemKafkaProducer()
        producer2 = ItemKafkaProducer()
        
        assert producer1 is producer2
    
    @pytest.mark.asyncio
    async def test_item_producer_has_publish_method(self):
        """Testa que ItemKafkaProducer tem método publish_item_criado"""
        from item.src.infrastructure.messaging.producer import ItemKafkaProducer
        
        producer = ItemKafkaProducer()
        assert hasattr(producer, 'publish_item_criado')
        assert callable(producer.publish_item_criado)


class TestDevolucaoKafkaProducer:
    """Testes para DevolucaoKafkaProducer"""
    
    @pytest.mark.asyncio
    async def test_devolucao_producer_initialization(self):
        """Testa inicialização do DevolucaoKafkaProducer"""
        from devolucao.src.infrastructure.messaging.producer import DevolucaoKafkaProducer
        
        producer = DevolucaoKafkaProducer()
        assert producer is not None
        assert hasattr(producer, 'producer')
    
    @pytest.mark.asyncio
    async def test_devolucao_producer_singleton(self):
        """Testa que DevolucaoKafkaProducer é singleton"""
        from devolucao.src.infrastructure.messaging.producer import DevolucaoKafkaProducer
        
        producer1 = DevolucaoKafkaProducer()
        producer2 = DevolucaoKafkaProducer()
        
        assert producer1 is producer2
    
    @pytest.mark.asyncio
    async def test_devolucao_producer_has_publish_method(self):
        """Testa que DevolucaoKafkaProducer tem método publish_devolucao_criada"""
        from devolucao.src.infrastructure.messaging.producer import DevolucaoKafkaProducer
        
        producer = DevolucaoKafkaProducer()
        assert hasattr(producer, 'publish_devolucao_criada')
        assert callable(producer.publish_devolucao_criada)


class TestReclamanteKafkaProducer:
    """Testes para ReclamanteKafkaProducer"""
    
    @pytest.mark.asyncio
    async def test_reclamante_producer_initialization(self):
        """Testa inicialização do ReclamanteKafkaProducer"""
        from reclamante.src.infrastructure.messaging.producer import ReclamanteKafkaProducer
        
        producer = ReclamanteKafkaProducer()
        assert producer is not None
        assert hasattr(producer, 'producer')
    
    @pytest.mark.asyncio
    async def test_reclamante_producer_singleton(self):
        """Testa que ReclamanteKafkaProducer é singleton"""
        from reclamante.src.infrastructure.messaging.producer import ReclamanteKafkaProducer
        
        producer1 = ReclamanteKafkaProducer()
        producer2 = ReclamanteKafkaProducer()
        
        assert producer1 is producer2
    
    @pytest.mark.asyncio
    async def test_reclamante_producer_has_publish_method(self):
        """Testa que ReclamanteKafkaProducer tem método publish_reclamante_criado"""
        from reclamante.src.infrastructure.messaging.producer import ReclamanteKafkaProducer
        
        producer = ReclamanteKafkaProducer()
        assert hasattr(producer, 'publish_reclamante_criado')
        assert callable(producer.publish_reclamante_criado)


class TestResponsavelKafkaProducer:
    """Testes para ResponsavelKafkaProducer"""
    
    @pytest.mark.asyncio
    async def test_responsavel_producer_initialization(self):
        """Testa inicialização do ResponsavelKafkaProducer"""
        from responsavel.src.infrastructure.messaging.producer import ResponsavelKafkaProducer
        
        producer = ResponsavelKafkaProducer()
        assert producer is not None
        assert hasattr(producer, 'producer')
    
    @pytest.mark.asyncio
    async def test_responsavel_producer_singleton(self):
        """Testa que ResponsavelKafkaProducer é singleton"""
        from responsavel.src.infrastructure.messaging.producer import ResponsavelKafkaProducer
        
        producer1 = ResponsavelKafkaProducer()
        producer2 = ResponsavelKafkaProducer()
        
        assert producer1 is producer2
    
    @pytest.mark.asyncio
    async def test_responsavel_producer_has_publish_method(self):
        """Testa que ResponsavelKafkaProducer tem método publish_responsavel_criado"""
        from responsavel.src.infrastructure.messaging.producer import ResponsavelKafkaProducer
        
        producer = ResponsavelKafkaProducer()
        assert hasattr(producer, 'publish_responsavel_criado')
        assert callable(producer.publish_responsavel_criado)


class TestLocalKafkaProducer:
    """Testes para LocalKafkaProducer"""
    
    @pytest.mark.asyncio
    async def test_local_producer_initialization(self):
        """Testa inicialização do LocalKafkaProducer"""
        from local.src.infrastructure.messaging.producer import LocalKafkaProducer
        
        producer = LocalKafkaProducer()
        assert producer is not None
        assert hasattr(producer, 'producer')
    
    @pytest.mark.asyncio
    async def test_local_producer_singleton(self):
        """Testa que LocalKafkaProducer é singleton"""
        from local.src.infrastructure.messaging.producer import LocalKafkaProducer
        
        producer1 = LocalKafkaProducer()
        producer2 = LocalKafkaProducer()
        
        assert producer1 is producer2
    
    @pytest.mark.asyncio
    async def test_local_producer_has_publish_method(self):
        """Testa que LocalKafkaProducer tem método publish_local_criado"""
        from local.src.infrastructure.messaging.producer import LocalKafkaProducer
        
        producer = LocalKafkaProducer()
        assert hasattr(producer, 'publish_local_criado')
        assert callable(producer.publish_local_criado)
