"""
Testes para validar que o sistema de Kafka está integrado corretamente
"""
import pytest


@pytest.mark.asyncio
async def test_item_kafka_producer_singleton():
    """Testa que o ItemKafkaProducer é singleton"""
    from item.src.infrastructure.messaging.producer import ItemKafkaProducer
    
    producer1 = ItemKafkaProducer()
    producer2 = ItemKafkaProducer()
    
    assert producer1 is producer2


@pytest.mark.asyncio
async def test_devolucao_kafka_producer_singleton():
    """Testa que o DevolucaoKafkaProducer é singleton"""
    from devolucao.src.infrastructure.messaging.producer import DevolucaoKafkaProducer
    
    producer1 = DevolucaoKafkaProducer()
    producer2 = DevolucaoKafkaProducer()
    
    assert producer1 is producer2


@pytest.mark.asyncio
async def test_reclamante_kafka_producer_singleton():
    """Testa que o ReclamanteKafkaProducer é singleton"""
    from reclamante.src.infrastructure.messaging.producer import ReclamanteKafkaProducer
    
    producer1 = ReclamanteKafkaProducer()
    producer2 = ReclamanteKafkaProducer()
    
    assert producer1 is producer2


@pytest.mark.asyncio
async def test_responsavel_kafka_producer_singleton():
    """Testa que o ResponsavelKafkaProducer é singleton"""
    from responsavel.src.infrastructure.messaging.producer import ResponsavelKafkaProducer
    
    producer1 = ResponsavelKafkaProducer()
    producer2 = ResponsavelKafkaProducer()
    
    assert producer1 is producer2


@pytest.mark.asyncio
async def test_local_kafka_producer_singleton():
    """Testa que o LocalKafkaProducer é singleton"""
    from local.src.infrastructure.messaging.producer import LocalKafkaProducer
    
    producer1 = LocalKafkaProducer()
    producer2 = LocalKafkaProducer()
    
    assert producer1 is producer2
