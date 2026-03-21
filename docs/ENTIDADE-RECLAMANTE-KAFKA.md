# Sistema de Mensageria Kafka - Entidade Reclamante

## Visão Geral

A entidade Reclamante implementa um sistema completo de publicação e consumo de eventos através do Apache Kafka, permitindo comunicação assíncrona com outras entidades do sistema.

## Producer: ReclamanteKafkaProducer

### Implementação
- **Localização**: `reclamante/src/infrastructure/messaging/producer/kafka_producer.py`
- **Padrão**: Singleton
- **Topic**: `reclamante_events`

### Eventos Publicados

#### reclamante_criado
Publicado quando um novo reclamante é criado no sistema.

```python
{
    "evento": "reclamante_criado",
    "reclamante_id": 1,
    "nome": "Maria Silva",
    "telefone": "11987654321",
    "documento": "12345678900",
    "timestamp": "2026-03-21T10:30:00"
}
```

#### reclamante_atualizado
Publicado quando um reclamante existente é atualizado.

```python
{
    "evento": "reclamante_atualizado",
    "reclamante_id": 1,
    "nome": "Maria Silva",
    "timestamp": "2026-03-21T10:35:00"
}
```

#### reclamante_deletado
Publicado quando um reclamante é removido do sistema.

```python
{
    "evento": "reclamante_deletado",
    "reclamante_id": 1,
    "timestamp": "2026-03-21T10:40:00"
}
```

## Consumers

A entidade Reclamante monitora eventos de outras entidades através de três consumers:

### 1. ItemEventConsumer
- **Localização**: `reclamante/src/infrastructure/messaging/consumers/item_event_consumer.py`
- **Topic**: `item_events`
- **Funcionalidade**: Monitora criação e atualização de itens para associação com reclamações

### 2. DevolucaoEventConsumer
- **Localização**: `reclamante/src/infrastructure/messaging/consumers/devolucao_event_consumer.py`
- **Topic**: `devolucao_events`
- **Funcionalidade**: Escuta eventos de devolução para atualizar status de reclamações

### 3. ResponsavelEventConsumer
- **Localização**: `reclamante/src/infrastructure/messaging/consumers/responsavel_event_consumer.py`
- **Topic**: `responsavel_events`
- **Funcionalidade**: Monitora eventos de responsáveis para sincronização de dados

## Fluxo de Integração

### Criação de Reclamante
```
CreateReclamanteUseCase
    ↓
ReclamanteRepository.create()
    ↓
ReclamanteKafkaProducer.publish_reclamante_criado()
    ↓
Kafka Topic: reclamante_events
```

### Consumo de Eventos
```
Kafka Topics (item_events, devolucao_events, responsavel_events)
    ↓
ItemEventConsumer, DevolucaoEventConsumer, ResponsavelEventConsumer
    ↓
Processam informações de outras entidades
```

## Testes

### Testes do Producer (tests/integration/test_kafka_producers.py)
- Teste de inicialização do ReclamanteKafkaProducer
- Teste de padrão Singleton
- Teste de método publish_reclamante_criado()

### Testes dos Consumers
- `reclamante/tests/integration/test_item_event_consumer.py` (4 testes)
- `reclamante/tests/integration/test_devolucao_event_consumer.py` (4 testes)
- `reclamante/tests/integration/test_responsavel_event_consumer.py` (4 testes)
- Total: 12 testes de consumer

## Uso em Produção

### Producer
```python
producer = ReclamanteKafkaProducer()
await producer.publish_reclamante_criado(
    reclamante_id=1,
    nome="Maria Silva",
    telefone="11987654321",
    documento="12345678900"
)
```

### Consumers
Os consumers são iniciados automaticamente pelo bootstrap da aplicação durante o startup.

## Configuração Kafka

### Bootstrap Server
- Host: localhost
- Port: 9092

### Topic: reclamante_events
- Partitions: 1
- Replication Factor: 1

### Topics Consumidos
- item_events
- devolucao_events
- responsavel_events

## Tratamento de Erros

Ambos producer e consumers implementam tratamento robusto de erros:

- **Producer**: Se a publicação falhar, a operação de reclamante ainda é completada (non-blocking) e um warning é registrado no log
- **Consumers**: Erros no processamento são capturados e registrados sem parar os consumers
