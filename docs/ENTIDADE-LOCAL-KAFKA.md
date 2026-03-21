# Sistema de Mensageria Kafka - Entidade Local

## Visão Geral

A entidade Local implementa um sistema completo de publicação e consumo de eventos através do Apache Kafka, permitindo comunicação assíncrona com outras entidades do sistema.

## Producer: LocalKafkaProducer

### Implementação
- **Localização**: `local/src/infrastructure/messaging/producer/kafka_producer.py`
- **Padrão**: Singleton
- **Topic**: `local_events`

### Eventos Publicados

#### local_criado
Publicado quando um novo local é criado no sistema.

```python
{
    "evento": "local_criado",
    "local_id": 1,
    "nome": "Recepção",
    "descricao": "Área de entrada principal",
    "ativo": true,
    "timestamp": "2026-03-21T10:30:00"
}
```

#### local_atualizado
Publicado quando um local existente é atualizado.

```python
{
    "evento": "local_atualizado",
    "local_id": 1,
    "nome": "Recepção",
    "ativo": true,
    "timestamp": "2026-03-21T10:35:00"
}
```

#### local_deletado
Publicado quando um local é removido do sistema.

```python
{
    "evento": "local_deletado",
    "local_id": 1,
    "timestamp": "2026-03-21T10:40:00"
}
```

## Consumer: ItemEventConsumer

### Implementação
- **Localização**: `local/src/infrastructure/messaging/consumers/item_event_consumer.py`
- **Topic**: `item_events`
- **Funcionalidade**: Monitora criação e atualização de itens associados a locais

### Eventos Consumidos

Quando um evento de item é recebido, o consumer:
1. Valida se o local associado está ativo
2. Sincroniza informações de itens registrados no local
3. Processa eventos de item para auditoria

## Fluxo de Integração

### Criação de Local
```
CreateLocalUseCase
    ↓
LocalRepository.create()
    ↓
LocalKafkaProducer.publish_local_criado()
    ↓
Kafka Topic: local_events
```

### Consumo de Evento de Item
```
Kafka Topic: item_events
    ↓
ItemEventConsumer
    ↓
Valida local associado ao item
```

## Testes

### Testes do Producer (tests/integration/test_kafka_producers.py)
- Teste de inicialização do LocalKafkaProducer
- Teste de padrão Singleton
- Teste de método publish_local_criado()

### Testes do Consumer (local/tests/integration/test_item_event_consumer.py)
- Teste de inicialização do ItemEventConsumer
- Teste de consumo de eventos de item
- Teste de validação de local

## Uso em Produção

### Producer
```python
producer = LocalKafkaProducer()
await producer.publish_local_criado(
    local_id=1,
    nome="Recepção",
    descricao="Área de entrada principal"
)
```

### Consumer
O consumer é iniciado automaticamente pelo bootstrap da aplicação durante o startup.

## Configuração Kafka

### Bootstrap Server
- Host: localhost
- Port: 9092

### Topic: local_events
- Partitions: 1
- Replication Factor: 1

### Topic: item_events
- Partitions: 1
- Replication Factor: 1

## Tratamento de Erros

Ambos producer e consumer implementam tratamento robusto de erros:

- **Producer**: Se a publicação falhar, a operação de local ainda é completada (non-blocking) e um warning é registrado no log
- **Consumer**: Erros no processamento são capturados e registrados sem parar o consumer
