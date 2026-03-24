# Sistema de Mensageria Kafka - Entidade Item

## Visão Geral

A entidade Item implementa um sistema completo de publicação e consumo de eventos através do Apache Kafka, permitindo comunicação assíncrona com outras entidades do sistema.

## Producer: ItemKafkaProducer

### Implementação
- **Localização**: `item/src/infrastructure/messaging/producer/kafka_producer.py`
- **Padrão**: Singleton
- **Topic**: `item_events`

### Eventos Publicados

#### item.criado
Publicado quando um novo item é criado no sistema.

```python
{
    "event_type": "item.criado",
    "aggregate_id": "1",
    "data": {
        "item_id": 1,
        "descricao": "Chave encontrada",
        "status": "disponivel",
        "local_id": 1,
        "responsavel_id": 1
    }
}
```

#### item.atualizado
Publicado quando um item existente é atualizado.

```python
{
    "event_type": "item.atualizado",
    "aggregate_id": "1",
    "data": {
        "item_id": 1,
        "descricao": "Chave encontrada",
        "status": "devolvido",
        "local_id": 1,
        "responsavel_id": 1
    }
}
```

#### item.deletado
Publicado quando um item é removido do sistema.

```python
{
    "event_type": "item.deletado",
    "aggregate_id": "1",
    "data": {
        "item_id": 1
    }
}
```

## Consumer: DevolucaoEventConsumer

### Implementação
- **Localização**: `item/src/infrastructure/messaging/consumers/devolucao_event_consumer.py`
- **Topic**: `devolucao_events`
- **Funcionalidade**: Atualiza o status do item quando uma devolução é criada

### Eventos Consumidos

Quando um evento de devolução é recebido, o consumer:
1. Identifica o item relacionado
2. Atualiza seu status para "devolvido"
3. Registra a atualização no banco de dados

## Fluxo de Integração

### Criação de Item
```
CreateItemUseCase
    ↓
ItemRepository.create()
    ↓
ItemKafkaProducer.publish_item_criado()
    ↓
Kafka Topic: item_events
```

### Consumo de Evento de Devolução
```
Kafka Topic: devolucao_events
    ↓
DevolucaoEventConsumer
    ↓
Atualiza status do Item
```

## Testes

### Testes do Producer (tests/integration/test_kafka_producers.py)
- Teste de inicialização do ItemKafkaProducer
- Teste de padrão Singleton
- Teste de método publish_item_criado()

### Testes do Consumer (item/tests/integration/test_devolucao_event_consumer.py)
- Teste de inicialização do DevolucaoEventConsumer
- Teste de consumo de eventos
- Teste de atualização de status

## Uso em Produção

### Producer
```python
producer = ItemKafkaProducer()
await producer.publish_item_criado(
    item_id=1,
    descricao="Chave encontrada",
    status="disponivel",
    local_id=1,
    responsavel_id=1
)
```

### Consumer
O consumer é iniciado automaticamente pelo bootstrap da aplicação durante o startup.

## Configuração Kafka

### Bootstrap Server
- Host: localhost
- Port: 9092

### Topic: item_events
- Partitions: 1
- Replication Factor: 1

### Topic: devolucao_events
- Partitions: 1
- Replication Factor: 1

## Tratamento de Erros

Ambos producer e consumer implementam tratamento robusto de erros:

- **Producer**: Se a publicação falhar, a operação de item ainda é completada (non-blocking) e um warning é registrado no log
- **Consumer**: Erros no processamento são capturados e registrados sem parar o consumer