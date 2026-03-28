# Documentação Docker — módulos do sistema

Este documento descreve como construir e executar as imagens Docker para os serviços:
- `devolucao` (porta 5003)
- `reclamante` (porta 5001)
- `responsavel` (porta 5002)
- `local` (porta 5000)
- `item` (porta 5004)

Observação: os Dockerfiles de cada módulo já existem na raiz de cada pasta e expõem as portas acima (ver `*/Dockerfile`). Cada serviço usa Python 3.11-slim e executa `python main.py`.

## Sumário rápido

- Build (por serviço):
  - docker build -t ap1-<servico>:latest ./<servico>
- Run (dev):
  - docker run --rm -p <host_port>:<container_port> -v $(pwd)/<servico>:/app --name <servico> ap1-<servico>:latest
- Compor local com docker-compose (raiz):
  - docker-compose up --build

## Portas (conforme Dockerfile)
- devolucao: 5003
- reclamante: 5001
- responsavel: 5002
- local: 5000
- item: 5004

> Assunção: As portas foram extraídas dos `EXPOSE` dos Dockerfiles. Se sua infra usar portas diferentes, ajuste os mapeamentos de host ao executar os containers.

---

## 1) Como construir uma imagem (por serviço)

Entre na raiz do repositório e execute (PowerShell):

```powershell
# Exemplo para o serviço 'devolucao'
docker build -t ap1-devolucao:latest .\devolucao

# Outros serviços
# docker build -t ap1-reclamante:latest .\reclamante
# docker build -t ap1-responsavel:latest .\responsavel
# docker build -t ap1-local:latest .\local
# docker build -t ap1-item:latest .\item
```

Opções úteis:
- `--no-cache` força rebuild completo.
- `-f` permite especificar outro Dockerfile.

## 2) Como executar um serviço (modo desenvolvimento)

Para montar o código local (hot-edit) e expor a porta:

```powershell
# Exemplo para devolucao
docker run --rm -p 5003:5003 -v ${PWD}\\devolucao:/app --name devolucao ap1-devolucao:latest
```

Explicação das flags:
- `--rm`: remove o container após parada (útil em dev)
- `-p host:container`: mapeia portas
- `-v host:container`: monta código local dentro do container

### Variáveis de ambiente
Os serviços dependem de banco de dados e de mensageria (Kafka). Configure através de variáveis de ambiente ao executar o container, por exemplo:

```powershell
docker run --rm -p 5003:5003 -e DATABASE_URL="postgresql://user:pass@db:5432/database" -e KAFKA_BOOTSTRAP_SERVERS="kafka:9092" --name devolucao ap1-devolucao:latest
```

Nota: os nomes exatos das variáveis podem variar no código; revise `src/infrastructure` de cada módulo para confirmar (assumi `DATABASE_URL` e `KAFKA_BOOTSTRAP_SERVERS` como padrão comum).

## 3) Rodando tudo com docker-compose

Na raiz do projeto existe um `docker-compose.yml`. Observação rápida: o arquivo atual parece ter problemas de indentação/estrutura (algumas entradas `reclamante` estão indentadas dentro de `devolucao`), então recomendo usar uma versão corrigida como a amostra abaixo.

Exemplo de `docker-compose.yml` (corrigido, mínimo):

```yaml
version: '3.8'

services:
  devolucao:
    build: ./devolucao
    ports:
      - "5003:5003"
    volumes:
      - ./devolucao:/app
    networks:
      - backend
    container_name: devolucao

  reclamante:
    build: ./reclamante
    ports:
      - "5001:5001"
    volumes:
      - ./reclamante:/app
    networks:
      - backend
    container_name: reclamante

  responsavel:
    build: ./responsavel
    ports:
      - "5002:5002"
    volumes:
      - ./responsavel:/app
    networks:
      - backend
    container_name: responsavel

  local:
    build: ./local
    ports:
      - "5000:5000"
    volumes:
      - ./local:/app
    networks:
      - backend
    container_name: local

  item:
    build: ./item
    ports:
      - "5004:5004"
    volumes:
      - ./item:/app
    networks:
      - backend
    container_name: item

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

networks:
  backend:
    driver: bridge
  kafka-network:
    driver: bridge
```

Para subir tudo (na raiz do repositório):

```powershell
# build + up em foreground
docker-compose up --build

# ou em background (detached)
docker-compose up --build -d

# parar e remover containers, redes e volumes padrão
docker-compose down
```

## 4) Testes rápidos / endpoints

Após subir um serviço, você pode confirmar com `curl` (PowerShell):

```powershell
# devolucao
curl http://localhost:5003/
# devolucao routes: /api/v1/devolucoes
curl http://localhost:5003/api/v1/devolucoes

# reclamante
curl http://localhost:5001/
curl http://localhost:5001/api/v1/reclamantes

# responsavel
curl http://localhost:5002/
curl http://localhost:5002/api/v1/responsaveis

# local
curl http://localhost:5000/
curl http://localhost:5000/api/v1/locais

# item
curl http://localhost:5004/
curl http://localhost:5004/api/v1/items
```

A raiz (`/`) retorna uma mensagem com a rota `/docs` — abra `http://localhost:<porta>/docs` no navegador para a documentação automática do FastAPI.

## 5) Produção: build, tag e push para registry

Exemplo de comandos para publicar uma imagem em um registry (Docker Hub):

```powershell
# tag
docker build -t meuusuario/ap1-devolucao:1.0.0 .\devolucao
# login
docker login
# push
docker push meuusuario/ap1-devolucao:1.0.0
```

Adapte para o registry da sua organização (ECR, GCR, ACR, etc.).

## 6) Debug e troubleshooting

- Se o container não iniciar: confira o log com `docker logs <nome>`.
- Erros de conexão com DB/Kafka: reveja as variáveis de ambiente e o `depends_on`/ordem de inicialização. Serviços que dependem de Kafka/DB podem precisar de retrials (no código há lógica de reconexão?) — veja `bootstrap.py` e `src/infrastructure`.
- Se o `docker-compose.yml` falhar ao subir, valide o YAML (ferramentas online ou `docker-compose config`) e corrija indentação.
- Ports em uso: `0.0.0.0:<porta>` pode falhar se outra aplicação já estiver usando a porta — troque a porta host ou pare o processo conflitante.

## 7) Observações e suposições

- Assumi nomes comuns de variáveis (ex.: `DATABASE_URL`, `KAFKA_BOOTSTRAP_SERVERS`). Verifique `src/infrastructure` de cada módulo para confirmar as variáveis requeridas.
- O `docker-compose.yml` da raiz contém uma versão que aparenta ter problemas de indentação; incluí uma amostra corrigida neste documento. Se quiser, posso:
  - corrigir e commitar uma versão ajustada do `docker-compose.yml`, ou
  - criar arquivos `docker-compose.override.yml` para desenvolvimento com os mounts e variáveis locais.

## 8) Comandos resumo (PowerShell)

```powershell
# build um serviço
docker build -t ap1-devolucao:latest .\devolucao

# rodar um serviço com mount
docker run --rm -p 5003:5003 -v ${PWD}\\devolucao:/app --name devolucao ap1-devolucao:latest

# subir tudo com compose (na raiz)
docker-compose up --build

# em background
docker-compose up --build -d

# parar e remover
docker-compose down
```

---

Se quiser, eu:
- corrijo e commito a versão ajustada do `docker-compose.yml` (posso abrir um patch com a versão acima),
- ou crio um `docker-compose.dev.yml` com mounts, variáveis de dev e healthchecks para facilitar desenvolvimento local.

Diga qual opção prefere e eu aplico as mudanças no repositório. Boa continuação!