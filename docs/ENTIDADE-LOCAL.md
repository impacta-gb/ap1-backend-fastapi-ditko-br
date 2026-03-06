# Implementação da Entidade Local - Arquitetura Diplomata

## O que foi implementado

### 1. Estrutura de Diretórios (Arquitetura Diplomata)

```
local/
├── src/
│   ├── domain/                           # Camada de Domínio
│   │   ├── entities/
│   │   │   └── local.py                 # Entidade Local com validações
│   │   └── repositories/
│   │       └── local_repository.py      # Interface do repositório (Port)
│   │
│   ├── application/                      # Camada de Aplicação
│   │   ├── use_cases/
│   │   │   └── local_use_cases.py       # 5 casos de uso implementados
│   │   └── schemas/
│   │       └── local_schema.py          # Schemas Pydantic
│   │
│   ├── infrastructure/                   # Camada de Infraestrutura
│   │   ├── database/
│   │   │   ├── config.py               # Configuração SQLAlchemy
│   │   │   └── models.py               # Modelo ORM LocalModel
│   │   └── repositories/
│   │       └── local_repository_impl.py # Implementação concreta
│   │
│   └── presentation/                     # Camada de Apresentação
│       └── api/
│           └── routes/
│               └── local_routes.py      # Endpoints FastAPI
└── __init__.py                          # Torna local um módulo Python
```

### 2. Domain Layer (Domínio)

#### Entidade Local (`local.py`)
- Dataclass com todos os atributos necessários
- Validações de negócio no `__post_init__`:
  - Tipo: não pode estar vazio
  - Descrição: não pode estar vazia
  - Bairro: não pode estar vazio
- Método de domínio:
  - `atualizar_descricao()` - Atualiza a descrição do local com validação
- Campos opcionais com default `None` para `id`, `created_at` e `updated_at`
- Independente de frameworks

#### Interface LocalRepository (`local_repository.py`)
- Abstração (Port) para acesso a dados
- Métodos definidos:
  - `create()` - Criar local
  - `get_by_id()` - Buscar por ID
  - `get_all()` - Listar todos (com paginação)
  - `update()` - Atualizar
  - `delete()` - Deletar
  - `get_by_bairro()` - Buscar por bairro
  - `count()` - Contar total de registros

### 3. Application Layer (Aplicação)

#### Use Cases (`local_use_cases.py`)
5 casos de uso implementados:
1. `CreateLocalUseCase` - Criar novo local
2. `GetLocalByIdUseCase` - Buscar local por ID (valida ID > 0)
3. `GetAllLocalsUseCase` - Listar todos os locais (com validação de paginação)
4. `UpdateLocalUseCase` - Atualizar local existente
5. `DeleteLocalUseCase` - Deletar local
6. `GetLocalsByBairroUseCase` - Buscar locais por bairro

#### Schemas Pydantic (`local_schema.py`)
- `LocalBase` - Schema base com campos comuns
- `LocalCreate` - Para criação (herda de LocalBase, todos os campos obrigatórios)
- `LocalUpdate` - Para atualização parcial (todos os campos opcionais)
- `LocalResponse` - Para resposta da API (inclui `id`, `created_at`, `updated_at`)
- `LocalListResponse` - Para listagem paginada

### 4. Infrastructure Layer (Infraestrutura)

#### Database Config (`config.py`)
- Setup do SQLAlchemy com async
- Engine assíncrono para banco SQLite separado (`local.db`)
- Session maker específico com `async_sessionmaker`
- Função `get_session()` para dependency injection (retorna `AsyncGenerator`)
- Função `init_db()` para criar tabelas

#### Model ORM (`models.py`)
- `LocalModel` - Modelo SQLAlchemy
- Mapeamento completo da tabela `locais`
- Campos:
  - `id` - INTEGER PRIMARY KEY AUTOINCREMENT
  - `tipo` - VARCHAR(255) NOT NULL
  - `descricao` - VARCHAR(255) NOT NULL
  - `bairro` - VARCHAR(100) NOT NULL
  - `created_at` - DATETIME com `server_default=func.now()`
  - `updated_at` - DATETIME com `onupdate=func.now()`

#### Repository Implementation (`local_repository_impl.py`)
- Implementação concreta de `LocalRepository`
- Conversões entre Entity e Model:
  - `_model_to_entity()` - ORM → Domain (inclui `created_at` e `updated_at`)
  - `_entity_to_model()` - Domain → ORM
- Implementação de todos os métodos da interface
- Uso de SQLAlchemy async com `select`, `func.count()`

### 5. Presentation Layer (Apresentação)

#### API Routes (`local_routes.py`)
Endpoints REST implementados:

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/v1/local/` | Criar novo local |
| GET | `/api/v1/local/` | Listar todos (paginado) |
| GET | `/api/v1/local/bairro/{bairro}` | Buscar por bairro |
| GET | `/api/v1/local/{local_id}` | Buscar local por ID |
| PUT | `/api/v1/local/{local_id}` | Atualizar local |
| DELETE | `/api/v1/local/{local_id}` | Deletar local |

**Características:**
- Dependency Injection do repositório via `Depends(get_session)`
- Tratamento de erros com `HTTPException`
- Validação automática via Pydantic
- Documentação automática (OpenAPI/Swagger)
- Revalidação da entidade de domínio após atualização (`__post_init__`)

### 6. Arquivos de Configuração

#### `app.py` - Atualizado
- Importação do módulo `local`
- Lifespan atualizado para inicializar os três bancos:
  - `init_db_item()` - Banco de items
  - `init_db_responsavel()` - Banco de responsaveis
  - `init_db_local()` - Banco de locais
- Inclusão das rotas de local
- Prefixo: `/api/v1/local`

#### `local/__init__.py` - Criado
- Torna o diretório `local` um módulo Python importável
- Permite importação correta das rotas no `app.py`

## Validações Implementadas

### Domain Layer (Entidade)

```python
def __post_init__(self):
    if not self.tipo or len(self.tipo.strip()) == 0:
        raise ValueError("Tipo do local é obrigatório")
    if not self.descricao or len(self.descricao.strip()) == 0:
        raise ValueError("Descrição do local é obrigatória")
    if not self.bairro or len(self.bairro.strip()) == 0:
        raise ValueError("Bairro do local é obrigatório")
```

### Application Layer (Schema Pydantic)

```python
class LocalBase(BaseModel):
    tipo: str = Field(..., min_length=1, max_length=255)
    descricao: str = Field(..., min_length=1, max_length=255)
    bairro: str = Field(..., min_length=1, max_length=255)
```

### Use Case Layer

```python
# GetLocalByIdUseCase
if local_id <= 0:
    raise ValueError("ID de local deve ser maior que zero")

# GetAllLocalsUseCase
if skip < 0:
    raise ValueError("Skip não pode ser negativo")
if limit <= 0 or limit > 1000:
    raise ValueError("Limit deve estar entre 1 e 1000")

# GetLocalsByBairroUseCase
if not bairro or len(bairro.strip()) == 0:
    raise ValueError("Bairro não pode estar vazio")
```

## Benefícios da Implementação

### Separação de Responsabilidades
- Domain não conhece banco de dados
- Infrastructure não conhece regras de negócio
- Presentation não conhece detalhes de persistência

### Banco de Dados Isolado
- Banco `local.db` separado dos demais (`items.db`, `responsavel.db`)
- Facilita escalabilidade e manutenção
- Potencial para arquitetura de microserviços

### Testabilidade
- Domain pode ser testado sem banco de dados
- Use Cases podem ser testados com mocks do repositório
- Fácil criar testes unitários e de integração

### Manutenibilidade
- Código organizado em camadas com responsabilidades claras
- Mudanças isoladas por camada
- Fácil localizar e corrigir problemas

## Como Usar

### 1. Executar a Aplicação
```bash
poetry run uvicorn app:app --reload
```

### 2. Acessar Documentação
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 3. Testar Endpoints

#### Criar Local
```bash
curl -X POST "http://localhost:8000/api/v1/local/" \
  -H "Content-Type: application/json" \
  -d '{
    "tipo": "Escola",
    "descricao": "Escola pública estadual",
    "bairro": "Centro"
  }'
```

**Resposta:**
```json
{
  "id": 1,
  "tipo": "Escola",
  "descricao": "Escola pública estadual",
  "bairro": "Centro",
  "created_at": "2026-03-06T12:00:00",
  "updated_at": null
}
```

#### Listar Todos (Paginado)
```bash
curl -X GET "http://localhost:8000/api/v1/local/?skip=0&limit=10"
```

**Resposta:**
```json
{
  "locals": [
    {
      "id": 1,
      "tipo": "Escola",
      "descricao": "Escola pública estadual",
      "bairro": "Centro",
      "created_at": "2026-03-06T12:00:00",
      "updated_at": null
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 10
}
```

#### Buscar por ID
```bash
curl -X GET "http://localhost:8000/api/v1/local/1"
```

#### Buscar por Bairro
```bash
curl -X GET "http://localhost:8000/api/v1/local/bairro/Centro"
```

#### Atualizar (PUT)
```bash
curl -X PUT "http://localhost:8000/api/v1/local/1" \
  -H "Content-Type: application/json" \
  -d '{
    "tipo": "Universidade",
    "descricao": "Universidade federal do bairro",
    "bairro": "Bela Vista"
  }'
```

#### Deletar
```bash
curl -X DELETE "http://localhost:8000/api/v1/local/1"
```

## Diferenças em Relação às Demais Entidades

### Estrutura Modular
- **Item**: Dentro de `src/` (módulo raiz)
- **Responsavel**: Módulo separado `responsavel/src/`
- **Local**: Módulo separado `local/src/` — mesmo padrão adotado pelo Responsavel

### Banco de Dados
- **Item**: `items.db`
- **Responsavel**: `responsavel.db`
- **Local**: `local.db`

### Timestamps
- **Local** é a única entidade que inclui `created_at` e `updated_at` mapeados tanto no Model ORM quanto na Entidade de domínio e no Schema de resposta (`LocalResponse`).

### Update Unificado
- **Local**: Um único schema `LocalUpdate` com todos os campos opcionais (equivalente ao PATCH)
- **Responsavel**: Schemas separados `ResponsavelUpdate` (PUT obrigatório), `ResponsavelPatch` (PATCH parcial) e `ResponsavelStatusUpdate`
- A rota PUT do Local comporta-se como PATCH — atualiza apenas os campos enviados

## Integração Futura com Item

Quando as entidades forem relacionadas:

### 1. Foreign Key em Item
```python
# Em item/src/infrastructure/database/models.py (ItemModel)
local_id = Column(Integer, ForeignKey('locais.id'), nullable=False)
```

### 2. Relationship ORM
```python
# Em ItemModel
local = relationship("LocalModel", back_populates="items")

# Em LocalModel
items = relationship("ItemModel", back_populates="local")
```

### 3. Validação no Use Case
```python
# Em CreateItemUseCase
async def execute(self, item: Item, local_repository: LocalRepository):
    local = await local_repository.get_by_id(item.local_id)
    if not local:
        raise ValueError("Local não encontrado")
    return await self.repository.create(item)
```

### 4. Response Expandido
```python
class ItemResponseWithLocal(BaseModel):
    id: int
    nome: str
    # ... outros campos
    local: LocalResponse
```

## Conceitos Aplicados

### Clean Architecture / Arquitetura Diplomata
- **Separação em camadas**: Domain, Application, Infrastructure, Presentation
- **Regra de dependência**: Camadas internas não conhecem externas
- **Inversão de dependências**: Use cases dependem de interfaces, não implementações

### SOLID Principles
- **S**ingle Responsibility: Cada classe tem uma única responsabilidade
- **O**pen/Closed: Aberto para extensão, fechado para modificação
- **L**iskov Substitution: Implementações substituíveis pela interface
- **I**nterface Segregation: Interface específica e enxuta
- **D**ependency Inversion: Dependência de abstrações, não concretizações

### Design Patterns
- **Repository Pattern**: Abstração de acesso a dados
- **Dependency Injection**: Injeção de dependências via FastAPI
- **DTO (Data Transfer Object)**: Schemas Pydantic
- **Use Case Pattern**: Encapsulamento de lógica de aplicação

### REST API Best Practices
- **Resource-Oriented**: URLs representam recursos (`/api/v1/local/`)
- **HTTP Status Codes**: Uso apropriado (200, 201, 204, 400, 404)
- **Idempotência**: PUT e DELETE são idempotentes

## Arquivos Criados/Modificados

### Criados
```
local/__init__.py
local/src/__init__.py
local/src/domain/__init__.py
local/src/domain/entities/__init__.py
local/src/domain/entities/local.py
local/src/domain/repositories/__init__.py
local/src/domain/repositories/local_repository.py
local/src/application/__init__.py
local/src/application/schemas/__init__.py
local/src/application/schemas/local_schema.py
local/src/application/use_cases/__init__.py
local/src/application/use_cases/local_use_cases.py
local/src/infrastructure/__init__.py
local/src/infrastructure/database/__init__.py
local/src/infrastructure/database/config.py
local/src/infrastructure/database/models.py
local/src/infrastructure/repositories/__init__.py
local/src/infrastructure/repositories/local_repository_impl.py
local/src/presentation/__init__.py
local/src/presentation/api/__init__.py
local/src/presentation/api/routes/__init__.py
local/src/presentation/api/routes/local_routes.py
docs/ENTIDADE-LOCAL.md
```

### Modificados
```
app.py          # Inclusão de rotas e lifespan para init_db_local()
```

## Referências

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Clean Architecture (Robert C. Martin)](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Pydantic Documentation](https://docs.pydantic.dev/)

---

**Grupo Ditko.br**
Projeto Frameworks Full Stack - Prof. Giovani Bontempo - Faculdade Impacta

**Data de Implementação**: 6 de Março de 2026
