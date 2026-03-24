# Sistema de Mensageria Kafka - Entidade Responsavel

## Visão Geral

A entidade Responsavel implementa um sistema completo de publicação e consumo de eventos através do Apache Kafka, permitindo comunicação assíncrona com outras entidades do sistema.

## Producer: ResponsavelKafkaProducer

### Implementação
- **Localização**: `responsavel/src/infrastructure/messaging/producer/kafka_producer.py`
- **Padrão**: Singleton
- **Topic**: `responsavel_events`

### Eventos Publicados

#### responsavel.criado
Publicado quando um novo responsável é criado no sistema.

```python
{
    "event_type": "responsavel.criado",
    "aggregate_id": "1",
    "data": {
        "responsavel_id": 1,
        "nome": "João Silva",
        "cargo": "Recepcionista",
        "telefone": "11987654321"
    }
}
```

#### responsavel.atualizado
Publicado quando um responsável existente é atualizado.

```python
{
    "event_type": "responsavel.atualizado",
    "aggregate_id": "1",
    "data": {
        "responsavel_id": 1,
        "nome": "João Silva",
        "cargo": "Recepcionista",
        "telefone": "11987654321",
        "ativo": true
    }
}
```

#### responsavel.status_alterado
Publicado quando há alteração de status de um responsável.

```python
{
    "event_type": "responsavel.status_alterado",
    "aggregate_id": "1",
    "data": {
        "responsavel_id": 1,
        "nome": "João Silva",
        "cargo": "Recepcionista",
        "telefone": "11987654321",
        "ativo": false
    }
}
```

#### responsavel.deletado
Publicado quando um responsável é removido do sistema.

```python
{
    "event_type": "responsavel.deletado",
    "aggregate_id": "1",
    "data": {
        "responsavel_id": 1
    }
}
```

## Consumer: ItemEventConsumer

### Implementação
- **Localização**: `responsavel/src/infrastructure/messaging/consumers/item_event_consumer.py`
- **Topic**: `item_events`
- **Funcionalidade**: Monitora criação e atualização de itens associados a responsáveis

### Eventos Consumidos

Quando um evento de item é recebido, o consumer:
1. Valida se o responsável associado está ativo
2. Sincroniza informações de itens registrados
3. Processa eventos de item para auditoria

## Fluxo de Integração

### Criação de Responsavel
```
CreateResponsavelUseCase
    ↓
ResponsavelRepository.create()
    ↓
ResponsavelKafkaProducer.publish_responsavel_criado()
    ↓
Kafka Topic: responsavel_events
```

### Consumo de Evento de Item
```
Kafka Topic: item_events
    ↓
ItemEventConsumer
    ↓
Valida responsável associado ao item
```

## Testes

### Testes do Producer (tests/integration/test_kafka_producers.py)
- Teste de inicialização do ResponsavelKafkaProducer
- Teste de padrão Singleton
- Teste de método publish_responsavel_criado()

### Testes do Consumer (responsavel/tests/integration/test_item_event_consumer.py)
- Teste de inicialização do ItemEventConsumer
- Teste de consumo de eventos de item
- Teste de validação de responsável

## Uso em Produção

### Producer
```python
producer = ResponsavelKafkaProducer()
await producer.publish_responsavel_criado(
    responsavel_id=1,
    nome="João Silva",
    cargo="Recepcionista",
    telefone="11987654321"
)
```

### Consumer
O consumer é iniciado automaticamente pelo bootstrap da aplicação durante o startup.

## Configuração Kafka

### Bootstrap Server
- Host: localhost
- Port: 9092

### Topic: responsavel_events
- Partitions: 1
- Replication Factor: 1

### Topic: item_events
- Partitions: 1
- Replication Factor: 1

## Tratamento de Erros

Ambos producer e consumer implementam tratamento robusto de erros:

- **Producer**: Se a publicação falhar, a operação de responsável ainda é completada (non-blocking) e um warning é registrado no log
- **Consumer**: Erros no processamento são capturados e registrados sem parar o consumer
