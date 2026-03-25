# Sistema de Mensageria Kafka - Entidade Devolucao

## Visão Geral

A entidade Devolucao implementa um sistema completo de publicação e consumo de eventos através do Apache Kafka, permitindo comunicação assíncrona com outras entidades do sistema.

## Producer: DevolucaoKafkaProducer

### Implementação
- **Localização**: `devolucao/src/infrastructure/messaging/producer/kafka_producer.py`
- **Padrão**: Singleton
- **Topic**: `devolucao_events`

### Eventos Publicados

#### devolucao.criada
Publicado quando uma nova devolução é criada no sistema.

```python
{
    "event_type": "devolucao.criada",
    "aggregate_id": "1",
    "data": {
        "devolucao_id": 1,
        "item_id": 1,
        "reclamante_id": 1
    }
}
```

#### devolucao.atualizada
Publicado quando uma devolução existente é atualizada.

```python
{
    "event_type": "devolucao.atualizada",
    "aggregate_id": "1",
    "data": {
        "devolucao_id": 1,
        "item_id": 1,
        "reclamante_id": 1
    }
}
```

#### devolucao.deletada
Publicado quando uma devolução é removida do sistema.

```python
{
    "event_type": "devolucao.deletada",
    "aggregate_id": "1",
    "data": {
        "devolucao_id": 1,
        "item_id": 1,
        "reclamante_id": 1
    }
}
```

## Consumer: ItemEventConsumer

### Implementação
- **Localização**: `devolucao/src/infrastructure/messaging/consumers/item_event_consumer.py`
- **Topic**: `item_events`
- **Funcionalidade**: Monitora eventos de item para processar devoluções relacionadas

### Eventos Consumidos

Quando um evento de item é recebido, o consumer processa informações sobre:
1. Itens criados - para associação com devoluções futuras
2. Itens atualizados - para sincronização de status
3. Itens deletados - para limpeza de devoluções relacionadas

## Fluxo de Integração

### Criação de Devolução
```
CreateDevolucaoUseCase
    ↓
DevolucaoRepository.create()
    ↓
DevolucaoKafkaProducer.publish_devolucao_criada()
    ↓
Kafka Topic: devolucao_events
```

### Consumo de Evento de Item
```
Kafka Topic: item_events
    ↓
ItemEventConsumer
    ↓
Processa informações do item
```

## Testes

### Testes do Producer (tests/integration/test_kafka_producers.py)
- Teste de inicialização do DevolucaoKafkaProducer
- Teste de padrão Singleton
- Teste de método publish_devolucao_criada()

### Testes do Consumer (devolucao/tests/integration/test_item_event_consumer.py)
- Teste de inicialização do ItemEventConsumer
- Teste de consumo de eventos de item
- Teste de processamento de eventos

## Uso em Produção

### Producer
```python
producer = DevolucaoKafkaProducer()
await producer.publish_devolucao_criada(
    devolucao_id=1,
    item_id=1,
    reclamante_id=1,
    observacao="Item devolvido com sucesso"
)
```

### Consumer
O consumer é iniciado automaticamente pelo bootstrap da aplicação durante o startup.

## Configuração Kafka

### Bootstrap Server
- Host: localhost
- Port: 9092

### Topic: devolucao_events
- Partitions: 1
- Replication Factor: 1

### Topic: item_events
- Partitions: 1
- Replication Factor: 1

## Tratamento de Erros

Ambos producer e consumer implementam tratamento robusto de erros:

- **Producer**: Se a publicação falhar, a operação de devolução ainda é completada (non-blocking) e um warning é registrado no log
- **Consumer**: Erros no processamento são capturados e registrados sem parar o consumer
