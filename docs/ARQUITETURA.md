# Arquitetura Diplomata - Sistema de Achados e Perdidos

## Visão Geral

Este projeto segue a **Arquitetura Diplomata**, organizando o código em camadas bem definidas com separação clara de responsabilidades.

Hoje, o sistema combina:
- Microsserviços independentes por contexto de negócio
- API REST com FastAPI em cada módulo
- Comunicação assíncrona com Apache Kafka
- Persistência isolada por serviço
- Arquitetura em camadas (Diplomata) dentro de cada microsserviço

## Microsserviços do Backend

O domínio foi dividido em cinco serviços:

1. Local
2. Reclamante
3. Responsável
4. Item
5. Devolução

Cada serviço tem:
- código-fonte próprio
- endpoints próprios
- banco de dados próprio
- produtor e/ou consumidores Kafka
- suíte de testes própria

## Arquitetura Interna de Cada Serviço

Cada microsserviço segue o padrão em camadas:

```
src/
├── domain/            # Entidades e contratos de repositório
├── application/       # Use cases e schemas de entrada/saída
├── infrastructure/    # Banco, repositórios e mensageria
└── presentation/      # Rotas HTTP (FastAPI)
```

Responsabilidades por camada:

### 1. Domain
- Regras de negócio centrais
- Entidades do contexto
- Interfaces de repositório (ports)

### 2. Application
- Casos de uso
- Orquestração das regras
- Validação de payloads com schemas

### 3. Infrastructure
- SQLAlchemy e modelos ORM
- Implementações concretas de repositório
- Producers, consumers e bootstrap de mensageria

### 4. Presentation
- Endpoints REST
- Mapeamento request/response
- Tratamento de erros HTTP

## Comunicação Entre Serviços

O sistema usa dois tipos de comunicação:

1. Síncrona: HTTP REST para operações expostas por API.
2. Assíncrona: eventos Kafka para sincronização entre contextos.

Tópicos principais usados pelo projeto:
- item_events
- local_events
- responsavel_events
- reclamante_events
- devolucao_events

Padrão de evento:

```json
{
  "event_type": "entidade.acao",
  "aggregate_id": "123",
  "data": {}
}
```

## Consistência e Projeções

Como cada serviço possui seu próprio banco, a consistência entre módulos é eventual.

Exemplo prático:
- O serviço Item valida referências de Local e Responsável a partir de projeções locais.
- Essas projeções são alimentadas por consumers Kafka.
- Se a mensageria estiver indisponível, pode haver atraso de sincronização.

Esse modelo privilegia:
- desacoplamento entre serviços
- resiliência de comunicação
- escalabilidade por contexto

## Ciclo de Vida e Mensageria

No startup de cada API:

1. inicializa banco local
2. inicializa bootstrap de mensageria
3. inicia producers e consumers

No shutdown:

1. encerra consumers
2. encerra producers

Os componentes de mensageria possuem tratamento de falha e tentativa de reconexão para reduzir impacto de indisponibilidade temporária do broker.

## Fluxos Arquiteturais

### Fluxo síncrono (dentro do serviço)

```
HTTP Request
  -> presentation/routes
  -> application/use_cases
  -> domain/entities + regras
  -> infrastructure/repositories
  -> banco local
  -> HTTP Response
```

### Fluxo assíncrono (entre serviços)

```
Ação de negócio em um serviço
  -> producer publica evento
  -> Kafka topic
  -> consumer em outro serviço
  -> atualização de projeção local
```

## Benefícios da Arquitetura Atual

- Separação clara de responsabilidades
- Independência de deploy por módulo
- Isolamento de falhas por contexto
- Escalabilidade horizontal por serviço
- Evolução independente dos domínios
- Testabilidade por camadas e por módulo

## Trade-offs e Pontos de Atenção

- Consistência eventual exige monitoramento de eventos
- Inicialização de mensageria pode aumentar tempo de startup
- Testes de integração precisam controlar dependências externas (ex.: Kafka)
- Observabilidade (logs, rastreio de eventos, métricas) é essencial

## Referências Relacionadas

- docs/KAFKA.md
- docs/DOCKER.md
- docs/ENTIDADE-ITEM.md
- docs/ENTIDADE-LOCAL.md
- docs/ENTIDADE-RESPONSAVEL.md
- docs/ENTIDADE-RECLAMANTE.md
- docs/ENTIDADE-DEVOLUCAO.md
