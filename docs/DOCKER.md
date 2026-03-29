# Operação com Docker - Sistema de Achados e Perdidos

## Visão Geral

Este documento descreve como executar os microsserviços em containers Docker, tanto de forma isolada quanto com orquestração via Docker Compose.

Serviços da solução:
- item
- local
- responsavel
- devolucao
- reclamante

Dependências de infraestrutura:
- zookeeper
- kafka

## Portas de API

As APIs são expostas nas seguintes portas:

| Serviço | Porta |
|---------|-------|
| item | 5000 |
| local | 5001 |
| responsavel | 5002 |
| devolucao | 5003 |
| reclamante | 5004 |

## Arquitetura de Execução

Cada módulo possui:
- Dockerfile próprio
- entrypoint em main.py
- conexão com banco local do módulo
- integração assíncrona por Kafka

Quando executados com Compose, os serviços compartilham rede Docker para comunicação interna e utilizam o broker Kafka para publicação e consumo de eventos.

## Execução com Docker Compose

Na raiz do repositório:

```bash
docker compose up --build
```

Para subir em background:

```bash
docker compose up --build -d
```

Para parar e remover os containers:

```bash
docker compose down
```

Para acompanhar logs:

```bash
docker compose logs -f
```

Para logs de um serviço específico:

```bash
docker compose logs -f item
```

## Build e Execução Isolada por Serviço

Exemplo para o módulo item:

```bash
docker build -t ap1-item:latest ./item
docker run --rm -p 5000:5000 --name item ap1-item:latest
```

Mesmo padrão para os demais módulos:

```bash
docker build -t ap1-local:latest ./local
docker build -t ap1-responsavel:latest ./responsavel
docker build -t ap1-devolucao:latest ./devolucao
docker build -t ap1-reclamante:latest ./reclamante
```

## Verificação Rápida de Saúde

Com o ambiente no ar, valide os endpoints raiz:

```bash
curl http://localhost:5000/
curl http://localhost:5001/
curl http://localhost:5002/
curl http://localhost:5003/
curl http://localhost:5004/
```

Documentação OpenAPI de cada módulo:
- http://localhost:5000/docs
- http://localhost:5001/docs
- http://localhost:5002/docs
- http://localhost:5003/docs
- http://localhost:5004/docs

## Operações Kafka (Diagnóstico)

Consumir eventos de um tópico:

```bash
docker compose exec kafka kafka-console-consumer --bootstrap-server kafka:29092 --topic item_events --from-beginning
```

Tópicos principais:
- item_events
- local_events
- responsavel_events
- devolucao_events
- reclamante_events

## Troubleshooting

### 1. Container sobe, mas API não responde

Verificar logs:

```bash
docker compose logs -f <serviço>
```

### 2. Erro de conexão com Kafka

Validar se kafka e zookeeper estão ativos:

```bash
docker compose ps
```

Reiniciar stack completa:

```bash
docker compose down
docker compose up --build -d
```

### 3. Porta já em uso

Alterar mapeamento de porta no docker-compose.yml ou encerrar o processo que ocupa a porta local.

### 4. Build inconsistente

Forçar rebuild sem cache:

```bash
docker compose build --no-cache
docker compose up -d
```

## Boas Práticas de Uso

- Subir sempre zookeeper e kafka junto dos módulos em testes de integração.
- Usar logs por serviço para diagnóstico rápido.
- Evitar alterações de porta sem atualizar a documentação.
- Executar testes com ambiente previsível para reduzir falso positivo de falha.

## Referências Relacionadas

- docs/KAFKA.md
- docs/ARQUITETURA.md
- docker-compose.yml