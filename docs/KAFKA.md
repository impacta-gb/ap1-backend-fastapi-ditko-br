# Documentação de Integração com Apache Kafka

## Visão Geral

O projeto utiliza Apache Kafka para comunicação assíncrona entre os microserviços. Isso permite que os serviços se comuniquem através de eventos, tornando o sistema mais desacoplado, resiliente e escalável.

## Arquitetura

### Componentes Principais

#### 1. **Producers (Produtores)**

Responsáveis por publicar eventos nos tópicos Kafka. Implementados em cada microserviço em uma pasta `producer`:

- `item/src/infrastructure/messaging/producer/` → **ItemKafkaProducer**
- `devolucao/src/infrastructure/messaging/producer/` → **DevolucaoKafkaProducer**
- `reclamante/src/infrastructure/messaging/producer/` → **ReclamanteKafkaProducer**
- `responsavel/src/infrastructure/messaging/producer/` → **ResponsavelKafkaProducer**
- `local/src/infrastructure/messaging/producer/` → **LocalKafkaProducer**

**Características:**
- ✅ Implementados como Singletons
- ✅ Gerenciam conexão com Kafka automaticamente
- ✅ Métodos start() e stop() para ciclo de vida
- ✅ Publicam eventos estruturados com event_type, aggregate_id e data
- ✅ Tratamento robusto de exceções e logging

**Importação:**
```python
from {modulo}.src.infrastructure.messaging.producer import {ProducerClass}
```

**Exemplo:**
```python
from item.src.infrastructure.messaging.producer import ItemKafkaProducer

producer = ItemKafkaProducer()
await producer.start()
await producer.publish_item_criado(item_id=1, descricao="Item", status="disponivel", local_id=1, responsavel_id=1)
```

#### 2. **Consumers (Consumidores)**

Responsáveis por consumir eventos dos tópicos Kafka. Cada módulo possui uma pasta `consumers` com a classe base e implementações específicas.

**Arquitetura:**

| Módulo | Consumer | Tópicos | Eventos |
|--------|----------|---------|---------|
| **Item** | `DevolucaoEventConsumer` | `devolucao_events` | `devolucao.criada` |
| **Devolução** | `ItemEventConsumer` | `item_events` | `item.registrado` |
| **Reclamante** | `ItemEventConsumer` | `item_events` | `item.registrado` |
| **Reclamante** | `ResponsavelEventConsumer` | `responsavel_events` | `responsavel.criado` |
| **Reclamante** | `DevolucaoEventConsumer` | `devolucao_events` | `devolucao.criada` |
| **Responsável** | `ItemEventConsumer` | `item_events` | `item.registrado` |
| **Local** | `ItemEventConsumer` | `item_events` | `item.registrado` |

**Classe Base: KafkaConsumer**
```python
# Localização: {modulo}/src/infrastructure/messaging/consumers/kafka_consumer.py

class KafkaConsumer(ABC):
    - Gerencia conexão com Kafka
    - Implementa loop de processamento de mensagens
    - Fornece métodos start() e stop()
    - Herança para implementações específicas via handle_message()
```

**Características:**
- ✅ Conexão automática com broker Kafka (`localhost:9092`)
- ✅ Desserialização automática de JSON
- ✅ Tratamento robusto de exceções
- ✅ Logging detalhado
- ✅ Consumer group para controle de offset
- ✅ Background task para processamento assíncrono

**Importação:**
```python
from {modulo}.src.infrastructure.messaging.consumers import {ConsumerClass}
```

#### 3. **Eventos de Domínio**

Publicados pelos producers quando uma ação acontece.

**Estrutura Padrão:**
```json
{
  "event_type": "xxx.yyy",
  "aggregate_id": "123",
  "data": {
    "campo1": "valor1",
    "campo2": "valor2"
  }
}
```

**Eventos Disponíveis:**

| Evento | Producer | Tópico | Consumidores |
|--------|----------|--------|-------------|
| `item.registrado` | ItemKafkaProducer | `item_events` | DevolucaoItemEventConsumer, ReclamanteItemEventConsumer, ResponsavelItemEventConsumer, LocalItemEventConsumer |
| `devolucao.criada` | DevolucaoKafkaProducer | `devolucao_events` | ItemDevolucaoEventConsumer, ReclamanteDevolucaoEventConsumer |
| `responsavel.criado` | ResponsavelKafkaProducer | `responsavel_events` | ReclamanteResponsavelEventConsumer |
| `reclamante.criado` | ReclamanteKafkaProducer | `reclamante_events` | (Aberto para expansão) |
| `local.criado` | LocalKafkaProducer | `local_events` | (Aberto para expansão) |

---

## Tópicos Kafka

Os tópicos foram criados para comunicação entre os serviços:

| Tópico | Descrição | Produtor | Consumidores |
|--------|-----------|----------|-------------|
| `item_events` | Eventos de itens registrados | ItemKafkaProducer | 4 consumers (Devolução, Reclamante, Responsável, Local) |
| `devolucao_events` | Eventos relacionados a devoluções | DevolucaoKafkaProducer | ItemDevolucaoEventConsumer, ReclamanteDevolucaoEventConsumer |
| `responsavel_events` | Eventos de responsáveis registrados | ResponsavelKafkaProducer | ReclamanteResponsavelEventConsumer |
| `reclamante_events` | Eventos de reclamantes registrados | ReclamanteKafkaProducer | (Aberto para expansão) |
| `local_events` | Eventos de locais registrados | LocalKafkaProducer | (Aberto para expansão) |

---

## Fluxo de Comunicação

### Exemplo 1: Criação de Devolução

```
POST /api/v1/devolucoes
    ↓
CreateDevolucaoUseCase.execute()
    ↓
Repository.create() → BD de Devolução
    ↓
DevolucaoKafkaProducer.publish_devolucao_criada()
    ↓
[KAFKA TOPIC: devolucao_events / Evento: devolucao.criada]
    ↓
ItemDevolucaoEventConsumer recebe evento
    ↓
Busca item e atualiza status → "devolvido"
    ↓
Repository.update() → BD de Item
    ↓
ReclamanteDevolucaoEventConsumer recebe evento
    ↓
Confirma devolução ao reclamante
```

### Exemplo 2: Criação de Item

```
POST /api/v1/items
    ↓
CreateItemUseCase.execute()
    ↓
Repository.create() → BD de Item
    ↓
ItemKafkaProducer.publish_item_criado()
    ↓
[KAFKA TOPIC: item_events / Evento: item.registrado]
    ↓
Múltiplos consumers escutam simultaneamente:
├── DevolucaoItemEventConsumer → sincroniza item
├── ReclamanteItemEventConsumer → notifica reclamante
├── ResponsavelItemEventConsumer → atualiza histórico
└── LocalItemEventConsumer → associa local
```

### Exemplo 3: Criação de Responsável

```
POST /api/v1/responsaveis
    ↓
CreateResponsavelUseCase.execute()
    ↓
Repository.create() → BD de Responsável
    ↓
ResponsavelKafkaProducer.publish_responsavel_criado()
    ↓
[KAFKA TOPIC: responsavel_events / Evento: responsavel.criado]
    ↓
ReclamanteResponsavelEventConsumer recebe evento
    ↓
Sincroniza dados de responsável
```

---

## Inicialização (Bootstrap)

### Arquivo bootstrap.py

A inicialização centralizada de todos os producers e consumers está em `bootstrap.py` na raiz do projeto.

```python
from bootstrap import MessagingBootstrap

# Inicializar
messaging = MessagingBootstrap()
await messaging.start_producers()    # Inicia 5 producers
await messaging.start_consumers()    # Inicia 7 consumers

# Cleanup
await messaging.stop_producers()
await messaging.stop_consumers()
```

### Classe MessagingBootstrap

```python
class MessagingBootstrap:
    """Gerencia a inicialização e shutdown de producers e consumers"""
    
    async def start_producers(self):
        """Inicia todos os 5 producers"""
        # ItemKafkaProducer
        # DevolucaoKafkaProducer
        # ReclamanteKafkaProducer
        # ResponsavelKafkaProducer
        # LocalKafkaProducer
    
    async def start_consumers(self):
        """Inicia todos os 7 consumers"""
        # DevolucaoEventConsumer (Item)
        # ItemEventConsumer (Devolução)
        # ItemEventConsumer (Reclamante)
        # ResponsavelEventConsumer (Reclamante)
        # DevolucaoEventConsumer (Reclamante)
        # ItemEventConsumer (Responsável)
        # ItemEventConsumer (Local)
    
    async def stop_producers(self):
        """Para todos os producers"""
    
    async def stop_consumers(self):
        """Para todos os consumers"""
```

### Integração com app.py

```python
from bootstrap import MessagingBootstrap

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação"""
    
    # Inicializar bancos de dados
    await init_db_local()
    await init_db_responsavel()
    await init_db_item()
    await init_db_devolucao()
    await init_db_reclamante()
    
    # Inicializar messaging (Kafka)
    messaging = MessagingBootstrap()
    await messaging.start_producers()
    await messaging.start_consumers()
    
    yield
    
    # Cleanup - parar producers e consumers
    await messaging.stop_producers()
    await messaging.stop_consumers()
```

---

## Configuração

### Variáveis de Ambiente

Por padrão, o Kafka é acessado em `localhost:9092`. Para alterar:

1. **Modificar em cada producer/consumer:**
   ```python
   bootstrap_servers='seu_host:9092'
   ```

2. **Adicionar variáveis de ambiente (recomendado para produção):**
   ```bash
   KAFKA_BOOTSTRAP_SERVERS=seu_host:9092
   ```

### Estrutura de Diretórios

```
projeto/
├── item/src/infrastructure/messaging/
│   ├── producer/
│   │   ├── __init__.py
│   │   └── kafka_producer.py
│   └── consumers/
│       ├── __init__.py
│       ├── kafka_consumer.py
│       └── devolucao_event_consumer.py
├── devolucao/src/infrastructure/messaging/
│   ├── producer/
│   │   ├── __init__.py
│   │   └── kafka_producer.py
│   └── consumers/
│       ├── __init__.py
│       ├── kafka_consumer.py
│       └── item_event_consumer.py
├── reclamante/src/infrastructure/messaging/
│   ├── producer/
│   │   ├── __init__.py
│   │   └── kafka_producer.py
│   └── consumers/
│       ├── __init__.py
│       ├── kafka_consumer.py
│       ├── item_event_consumer.py
│       ├── responsavel_event_consumer.py
│       └── devolucao_event_consumer.py
├── responsavel/src/infrastructure/messaging/
│   ├── producer/
│   │   ├── __init__.py
│   │   └── kafka_producer.py
│   └── consumers/
│       ├── __init__.py
│       ├── kafka_consumer.py
│       └── item_event_consumer.py
├── local/src/infrastructure/messaging/
│   ├── producer/
│   │   ├── __init__.py
│   │   └── kafka_producer.py
│   └── consumers/
│       ├── __init__.py
│       ├── kafka_consumer.py
│       └── item_event_consumer.py
└── bootstrap.py (Inicialização centralizada)
```

---

## Como Usar

### Publicar um Evento

```python
from item.src.infrastructure.messaging.producer import ItemKafkaProducer

# Obter a instância do producer (Singleton)
producer = ItemKafkaProducer()

# Já foi inicializado em bootstrap.py durante startup
# Publicar um evento de item criado
await producer.publish_item_criado(
    item_id=123,
    descricao="Carteira de couro",
    status="disponivel",
    local_id=5,
    responsavel_id=10
)
```

**Estrutura do evento publicado:**
```json
{
  "event_type": "item.registrado",
  "aggregate_id": "123",
  "data": {
    "item_id": 123,
    "descricao": "Carteira de couro",
    "status": "disponivel",
    "local_id": 5,
    "responsavel_id": 10
  }
}
```

### Criar um Novo Consumer

1. **Crie a classe que herda de KafkaConsumer:**

```python
# devolucao/src/infrastructure/messaging/consumers/item_event_consumer.py

from devolucao.src.infrastructure.messaging.consumers.kafka_consumer import KafkaConsumer

class ItemEventConsumer(KafkaConsumer):
    def __init__(self):
        super().__init__(
            topics=["item_events"],
            group_id="devolucao_item_listener_group"
        )
    
    async def handle_message(self, message: dict):
        """Processa a mensagem recebida do Kafka"""
        event_type = message.get("event_type")
        
        if event_type == "item.registrado":
            await self._handle_item_registrado(message)
        else:
            logger.debug(f"Tipo de evento não tratado: {event_type}")
    
    async def _handle_item_registrado(self, message: dict):
        """Processa quando um item é registrado"""
        try:
            data = message.get('data', {})
            item_id = data.get('item_id')
            
            # Sua lógica aqui
            logger.info(f"Item {item_id} foi registrado")
            
        except Exception as e:
            logger.error(f"Erro ao processar item registrado: {e}")
```

2. **Adicione ao __init__.py do módulo:**

```python
# devolucao/src/infrastructure/messaging/consumers/__init__.py

from devolucao.src.infrastructure.messaging.consumers.item_event_consumer import ItemEventConsumer

__all__ = ["ItemEventConsumer"]
```

3. **Integre ao bootstrap.py:**

```python
# bootstrap.py

from devolucao.src.infrastructure.messaging.consumers import ItemEventConsumer as DevolucaoItemEventConsumer

class MessagingBootstrap:
    def __init__(self):
        self.novo_consumer = DevolucaoItemEventConsumer()
    
    async def start_consumers(self):
        try:
            await self.novo_consumer.start()
            logger.info(f"Novo Consumer iniciado com sucesso")
        except Exception as e:
            logger.warning(f"Novo Consumer não pôde ser conectado: {e}")
    
    async def stop_consumers(self):
        try:
            await self.novo_consumer.stop()
        except Exception as e:
            logger.error(f"Erro ao parar Novo Consumer: {e}")
```

---

## Instalação do Apache Kafka

### Docker Compose (Recomendado)

O projeto possui um arquivo `docker-compose.yml` configurado:

```powershell
docker-compose up -d
```

**Arquivo docker-compose.yml:**

```yaml
version: '3.8'

services:
  zookeeper:
    image: confluentinc/cp-zookeeper:7.5.0
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000
    ports:
      - "2181:2181"
    networks:
      - kafka-network

  kafka:
    image: confluentinc/cp-kafka:7.5.0
    depends_on:
      - zookeeper
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:29092,PLAINTEXT_HOST://localhost:9092
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
      KAFKA_INTER_BROKER_LISTENER_NAME: PLAINTEXT
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_AUTO_CREATE_TOPICS_ENABLE: "true"
    networks:
      - kafka-network
    healthcheck:
      test: kafka-broker-api-versions --bootstrap-server localhost:9092 || exit 1
      interval: 5s
      timeout: 10s
      retries: 5

networks:
  kafka-network:
    driver: bridge
```

### Verificação

```powershell
# Listar tópicos
docker exec lostfoundfullstack-kafka-1 kafka-topics --list --bootstrap-server localhost:9092

# Criar um tópico (opcional)
docker exec lostfoundfullstack-kafka-1 kafka-topics --create --topic test --bootstrap-server localhost:9092

# Consumir mensagens de um tópico em tempo real
docker exec lostfoundfullstack-kafka-1 kafka-console-consumer --topic item_events --from-beginning --bootstrap-server localhost:9092

# Status dos containers
docker-compose ps
```

---

## Testes

### Testes Existentes

**Localização:** `tests/integration/`

- `test_devolucao_event_consumer.py` - Testes do DevolucaoEventConsumer
- `test_kafka_messaging.py` - Testes gerais de messaging

### Executar Testes

```powershell
# Todos os testes do projeto
pytest -v

# Apenas testes de Kafka
pytest tests/integration/test_kafka_messaging.py tests/integration/test_devolucao_event_consumer.py -v

# Testes com coverage
pytest --cov

# Testes de uma entidade específica
pytest item/tests/ -v
pytest devolucao/tests/ -v
pytest reclamante/tests/ -v
pytest responsavel/tests/ -v
pytest local/tests/ -v
```

### Verificação de Producers e Consumers por Entidade

**Status de Implementação:**

| Entidade | Producer | Consumers | Status |
|----------|----------|-----------|--------|
| **Item** | ✅ ItemKafkaProducer | ✅ DevolucaoEventConsumer | ✅ Completo |
| **Devolução** | ✅ DevolucaoKafkaProducer | ✅ ItemEventConsumer | ✅ Completo |
| **Reclamante** | ✅ ReclamanteKafkaProducer | ✅ ItemEventConsumer, ResponsavelEventConsumer, DevolucaoEventConsumer | ✅ Completo |
| **Responsável** | ✅ ResponsavelKafkaProducer | ✅ ItemEventConsumer | ✅ Completo |
| **Local** | ✅ LocalKafkaProducer | ✅ ItemEventConsumer | ✅ Completo |

**Conclusão:** Todos os módulos possuem producers e consumers implementados de forma consistente.

---

## Tratamento de Erros

O sistema é resiliente por design:

- ✅ Se o Kafka não estiver disponível na inicialização, um warning é registrado e a aplicação continua
- ✅ Se houver erro ao publicar um evento, um warning é registrado mas o serviço continua
- ✅ Mensagens são desserializadas com segurança
- ✅ Exceptions em handle_message() são capturadas e registradas

---

## Troubleshooting

### "Kafka Producer/Consumer não foi inicializado"

**Problema:** Erro ao tentar enviar um evento antes do producer iniciar.

**Solução:** Verifique se a aplicação completou a inicialização nos logs.

### "Connection refused localhost:9092"

**Problema:** Kafka não está rodando.

**Solução:**
1. Inicie o Docker Desktop
2. Execute `docker-compose up -d`
3. Verifique com `docker-compose ps`

### Consumer não processando mensagens

**Problema:** Consumer inicia mas não processa eventos.

**Solução:**
1. Verifique se o tópico existe
2. Verifique se o `group_id` está correto
3. Verifique logs da aplicação

### Tópicos não sendo criados automaticamente

**Problema:** Eventos não estão sendo publicados.

**Solução:**
1. Verifique se `KAFKA_AUTO_CREATE_TOPICS_ENABLE: "true"` está no docker-compose.yml
2. Crie manualmente o tópico se necessário

---

## Rodar a Aplicação

### Instalar dependências

```powershell
pip install -r requirements.txt
```

### Iniciar Kafka

```powershell
docker-compose up -d
```

### Iniciar o servidor FastAPI

```powershell
python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

**Acesso:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

--- 

## Referências

- [Apache Kafka Documentation](https://kafka.apache.org/documentation/)
- [aiokafka Python Client](https://aiokafka.readthedocs.io/)
- [Event Sourcing Pattern](https://martinfowler.com/eaaDev/EventSourcing.html)
- [Arquitetura do Projeto](./ARQUITETURA.md)
- [Testes do Projeto](./TESTS.md)