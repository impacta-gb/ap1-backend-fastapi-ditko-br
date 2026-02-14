# Arquitetura Diplomata - Sistema de Achados e Perdidos

## Estrutura do Projeto

Este projeto segue a **Arquitetura Diplomata**, organizando o código em camadas bem definidas com separação clara de responsabilidades.

```
src/
├── domain/                    # Camada de Domínio (Core)
│   ├── entities/             # Entidades de negócio
│   │   └── item.py          # Entidade Item
│   └── repositories/         # Interfaces dos repositórios (Ports)
│       └── item_repository.py
│
├── application/              # Camada de Aplicação
│   ├── use_cases/           # Casos de uso (regras de negócio)
│   │   └── item_use_cases.py
│   └── schemas/             # DTOs/Schemas Pydantic
│       └── item_schema.py
│
├── infrastructure/           # Camada de Infraestrutura (Adapters)
│   ├── database/            # Configuração do banco de dados
│   │   ├── config.py       # Configuração SQLAlchemy
│   │   └── models.py       # Modelos ORM
│   └── repositories/        # Implementações concretas dos repositórios
│       └── item_repository_impl.py
│
└── presentation/            # Camada de Apresentação
    └── api/                # API REST
        └── routes/         # Endpoints FastAPI
            └── item_routes.py
```

## Camadas da Arquitetura

### 1. Domain (Domínio)
**Propósito**: Núcleo da aplicação, contém a lógica de negócio pura.

- **Entities**: Classes que representam os conceitos principais do negócio
  - `Item`: Representa um item perdido/encontrado
  - Contém validações e regras de negócio

- **Repositories (Interfaces)**: Contratos (abstrações) para acesso a dados
  - Define o que pode ser feito, não como
  - Inversão de dependência (Dependency Inversion Principle)

**Características**:
- Independente de frameworks
- Independente de banco de dados
- Testável isoladamente
- Sem dependências externas

### 2. Application (Aplicação)
**Propósito**: Orquestra o fluxo de dados e coordena os casos de uso.

- **Use Cases**: Casos de uso específicos da aplicação
  - `CreateItemUseCase`: Criar novo item
  - `GetItemByIdUseCase`: Buscar item por ID
  - `UpdateItemUseCase`: Atualizar item
  - etc.

- **Schemas**: DTOs (Data Transfer Objects) usando Pydantic
  - Validação de entrada/saída
  - Serialização/Deserialização
  - Documentação automática

**Características**:
- Depende apenas do Domain
- Define interfaces de entrada/saída
- Orquestra a lógica de negócio

### 3. Infrastructure (Infraestrutura)
**Propósito**: Implementações concretas e detalhes técnicos.

- **Database**: Configuração e modelos do banco de dados
  - SQLAlchemy setup
  - Modelos ORM
  - Migrations (futuramente)

- **Repositories (Implementations)**: Implementações concretas dos repositórios
  - Acesso ao banco de dados
  - Conversão entre entidades e modelos ORM

**Características**:
- Implementa as interfaces do Domain
- Lida com detalhes técnicos
- Pode ser substituída facilmente

### 4. Presentation (Apresentação)
**Propósito**: Interface com o mundo externo (API REST).

- **API Routes**: Endpoints HTTP
  - Controllers FastAPI
  - Validação de requisições
  - Formatação de respostas
  - Tratamento de erros

**Características**:
- Depende das camadas Application e Infrastructure
- Lida com HTTP, JSON, etc.
- Injeta dependências

## Fluxo de Dados

```
Request (HTTP)
    ↓
[Presentation Layer] - Recebe e valida request
    ↓
[Application Layer] - Executa use case
    ↓
[Domain Layer] - Aplica regras de negócio
    ↓
[Infrastructure Layer] - Acessa banco de dados
    ↓
Response (HTTP)
```

## Princípios Aplicados

### 1. **Dependency Inversion Principle (DIP)**
- Camadas internas não dependem de camadas externas
- Uso de interfaces (abstrações) no Domain
- Implementações concretas na Infrastructure

### 2. **Single Responsibility Principle (SRP)**
- Cada classe tem uma única responsabilidade
- Use cases focados em uma ação específica
- Separação clara entre camadas

### 3. **Open/Closed Principle (OCP)**
- Aberto para extensão, fechado para modificação
- Novas funcionalidades sem alterar código existente

### 4. **Interface Segregation Principle (ISP)**
- Interfaces específicas e focadas
- Clientes não dependem de métodos que não usam

## Vantagens da Arquitetura Diplomata

- **Testabilidade**: Cada camada pode ser testada isoladamente
- **Manutenibilidade**: Código organizado e fácil de entender
- **Flexibilidade**: Fácil trocar implementações (ex: banco de dados)
- **Escalabilidade**: Estrutura preparada para crescimento
- **Independência**: Core da aplicação independente de frameworks

## Próximos Passos

1. Entidade Item implementada
2. Implementar entidades: Local, Responsável, Reclamante, Devolução
3. Adicionar testes unitários
4. Implementar relacionamentos entre entidades
5. Adicionar migrations com Alembic
6. Implementar autenticação e autorização
7. Adicionar logs e monitoramento

## Executando o Projeto

1. Instale as dependências:
```bash
poetry install
```

2. Execute o servidor:
```bash
poetry run uvicorn app:app --reload
```

3. Acesse a documentação:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testando os Endpoints

### Criar Item
```bash
curl -X POST "http://localhost:8000/api/v1/items/" \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Celular Samsung",
    "categoria": "eletronicos",
    "data_encontro": "2026-02-12T10:00:00",
    "descricao": "Celular Samsung Galaxy encontrado no corredor",
    "status": "disponivel",
    "local_id": 1,
    "responsavel_id": 1
  }'
```

### Listar Itens
```bash
curl -X GET "http://localhost:8000/api/v1/items/"
```

### Buscar Item por ID
```bash
curl -X GET "http://localhost:8000/api/v1/items/1"
```
