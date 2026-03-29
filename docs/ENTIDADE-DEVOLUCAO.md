# Implementação da Entidade Devolucao - Arquitetura Diplomata

## O que foi implementado

### 1. Estrutura de Diretórios (Arquitetura Diplomata)

```
devolucao/
├── src/
│   ├── domain/                           # Camada de Domínio
│   │   ├── entities/
│   │   │   └── devolucao.py             # Entidade Devolucao com validações
│   │   └── repositories/
│   │       └── devolucao_repository.py  # Interface do repositório (Port)
│   │
│   ├── application/                      # Camada de Aplicação
│   │   ├── use_cases/
│   │   │   └── devolucao_use_cases.py   # 7 casos de uso implementados
│   │   └── schemas/
│   │       └── devolucao_schema.py      # Schemas Pydantic
│   │
│   ├── infrastructure/                   # Camada de Infraestrutura
│   │   ├── database/
│   │   │   ├── config.py               # Configuração SQLAlchemy
│   │   │   └── models.py               # Modelo ORM DevolucaoModel
│   │   └── repositories/
│   │       └── devolucao_repository_impl.py # Implementação concreta
│   │
│   └── presentation/                     # Camada de Apresentação
│       └── api/
│           └── routes/
│               └── devolucao_routes.py  # Endpoints FastAPI
└── __init__.py                          # Torna devolucao um módulo Python
```

### 2. Domain Layer (Domínio)

#### Entidade Devolucao (`devolucao.py`)
- Dataclass com todos os atributos necessários
- Validações de negócio no `__post_init__`:
  - `reclamante_id`: deve ser um número positivo
  - `item_id`: deve ser um número positivo
  - `observacao`: não pode ser vazia
- `data_devolucao` com `default_factory=datetime.now` (registra data/hora atual automaticamente)
- Método de domínio:
  - `atualizar_observacao()` - Atualiza a observação com validação
- Independente de frameworks

#### Interface DevolucaoRepository (`devolucao_repository.py`)
- Abstração (Port) para acesso a dados
- Métodos definidos:
  - `create()` - Criar devolução
  - `get_by_id()` - Buscar por ID
  - `get_all()` - Listar todos (com paginação)
  - `update()` - Atualizar
  - `delete()` - Deletar
  - `get_by_data()` - Buscar por data
  - `count()` - Contar total de registros

### 3. Application Layer (Aplicação)

#### Use Cases (`devolucao_use_cases.py`)
7 casos de uso implementados:
1. `CreateDevolucaoUseCase` - Criar nova devolução
2. `GetDevolucaoByIdUseCase` - Buscar devolução por ID
3. `GetAllDevolucoesUseCase` - Listar todas as devoluções (com validação de paginação)
4. `UpdateDevolucaoUseCase` - Atualizar devolução existente
5. `DeleteDevolucaoUseCase` - Deletar devolução
6. `GetDevolucoesByDataUseCase` - Buscar devoluções por data
7. `CountDevolucoesUseCase` - Contar total de devoluções

#### Schemas Pydantic (`devolucao_schema.py`)
- `DevolucaoBase` - Schema base com campos comuns
- `DevolucaoCreate` - Para criação (herda de DevolucaoBase)
- `DevolucaoUpdate` - Para atualização completa PUT (herda de DevolucaoBase)
- `DevolucaoPatch` - Para atualização parcial PATCH (campos opcionais)
- `DevolucaoResponse` - Para resposta da API (inclui `id`, `created_at`, `updated_at`)
- `DevolucaoListResponse` - Para listagem paginada

### 4. Infrastructure Layer (Infraestrutura)

#### Database Config (`config.py`)
- Setup do SQLAlchemy com async
- Engine assíncrono para banco SQLite separado (`devolucao.db`)
- Session maker específico com `async_sessionmaker`
- Função `get_session()` para dependency injection
- Função `init_db()` para criar tabelas

#### Model ORM (`models.py`)
- `DevolucaoModel` - Modelo SQLAlchemy
- Mapeamento completo da tabela `devolucoes`
- Importa `Base` do próprio módulo `devolucao` (banco isolado)
- Campos:
  - `id` - INTEGER PRIMARY KEY AUTOINCREMENT
  - `data_devolucao` - DATETIME NOT NULL
  - `observacao` - TEXT NOT NULL
  - `reclamante_id` - INTEGER NOT NULL
  - `item_id` - INTEGER NOT NULL
  - `created_at` - DATETIME com `server_default=func.now()`
  - `updated_at` - DATETIME com `onupdate=func.now()`

#### Repository Implementation (`devolucao_repository_impl.py`)
- Implementação concreta de `DevolucaoRepository`
- Conversões entre Entity e Model:
  - `_model_to_entity()` - ORM → Domain
  - `_entity_to_model()` - Domain → ORM
- Implementação de todos os métodos da interface
- `get_by_data()` usa `func.date()` para comparar apenas a parte da data (sem hora)
- Uso de SQLAlchemy async com `select`, `func.count()`

### 5. Presentation Layer (Apresentação)

#### API Routes (`devolucao_routes.py`)
Endpoints REST implementados:

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/v1/devolucoes/` | Criar nova devolução |
| GET | `/api/v1/devolucoes/` | Listar todas (paginado) |
| GET | `/api/v1/devolucoes/data/{data}` | Buscar por data |
| GET | `/api/v1/devolucoes/{id}` | Buscar devolução por ID |
| PUT | `/api/v1/devolucoes/{id}` | Atualizar devolução (completa) |
| PATCH | `/api/v1/devolucoes/{id}` | Atualização parcial |
| DELETE | `/api/v1/devolucoes/{id}` | Deletar devolução |

**Características:**
- Dependency Injection do repositório via `Depends(get_session)`
- Tratamento de erros com `HTTPException`
- Validação automática via Pydantic
- Documentação automática (OpenAPI/Swagger)
- PATCH reutiliza `UpdateDevolucaoUseCase` com merge dos campos na camada de apresentação

### 6. Arquivos de Configuração

#### `main.py` - Atualizado
- Importação do módulo `devolucao`
- Lifespan atualizado para inicializar os quatro bancos:
  - `init_db_item()` - Banco de items
  - `init_db_responsavel()` - Banco de responsaveis
  - `init_db_local()` - Banco de locais
  - `init_db_devolucao()` - Banco de devoluções
- Inclusão das rotas de devolução
- Prefixo: `/api/v1/devolucoes`

## Validações Implementadas

### Domain Layer (Entidade)

```python
def __post_init__(self):
    if self.reclamante_id <= 0:
        raise ValueError("O ID do reclamante deve ser um número positivo.")
    if self.item_id <= 0:
        raise ValueError("O ID do item deve ser um número positivo.")
    if not self.observacao or len(self.observacao.strip()) == 0:
        raise ValueError("A observação é obrigatória.")
```

### Application Layer (Schema Pydantic)

```python
class DevolucaoBase(BaseModel):
    reclamante_id: int = Field(..., gt=0)
    item_id: int = Field(..., gt=0)
    observacao: str = Field(..., min_length=1, max_length=255)
    data_devolucao: datetime = Field(default_factory=datetime.now)
```

### Use Case Layer

```python
# CreateDevolucaoUseCase / UpdateDevolucaoUseCase
if devolucao.data_devolucao > datetime.now():
    raise ValueError("Data da devolução não pode ser no futuro")

# GetDevolucaoByIdUseCase
if devolucao_id <= 0:
    raise ValueError("ID da devolução deve ser maior que zero")

# GetAllDevolucoesUseCase
if skip < 0:
    raise ValueError("Skip não pode ser negativo")
if limit <= 0 or limit > 1000:
    raise ValueError("Limit deve estar entre 1 e 1000")

# GetDevolucoesByDataUseCase
if not data:
    raise ValueError("Data não pode ser nula")
```

## Como Usar

### 1. Executar a Aplicação
```bash
poetry run uvicorn main:app --reload --port 5003
```

### 2. Acessar Documentação
- Swagger UI: http://localhost:5003/docs
- ReDoc: http://localhost:5003/redoc

### 3. Testar Endpoints

#### Criar Devolução
```bash
curl -X POST "http://localhost:5003/api/v1/devolucoes/" \
  -H "Content-Type: application/json" \
  -d '{
    "reclamante_id": 1,
    "item_id": 1,
    "observacao": "Item devolvido ao proprietário após verificação de identidade"
  }'
```

**Resposta:**
```json
{
  "id": 1,
  "reclamante_id": 1,
  "item_id": 1,
  "observacao": "Item devolvido ao proprietário após verificação de identidade",
  "data_devolucao": "2026-03-07T14:30:00",
  "created_at": "2026-03-07T14:30:00",
  "updated_at": null
}
```

#### Listar Todas (Paginado)
```bash
curl -X GET "http://localhost:5003/api/v1/devolucoes/?skip=0&limit=10"
```

**Resposta:**
```json
{
  "devolucoes": [
    {
      "id": 1,
      "reclamante_id": 1,
      "item_id": 1,
      "observacao": "Item devolvido ao proprietário após verificação de identidade",
      "data_devolucao": "2026-03-07T14:30:00",
      "created_at": "2026-03-07T14:30:00",
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
curl -X GET "http://localhost:5003/api/v1/devolucoes/1"
```

#### Buscar por Data
```bash
curl -X GET "http://localhost:5003/api/v1/devolucoes/data/2026-03-07T00:00:00"
```

#### Atualizar (PUT)
```bash
curl -X PUT "http://localhost:5003/api/v1/devolucoes/1" \
  -H "Content-Type: application/json" \
  -d '{
    "reclamante_id": 1,
    "item_id": 1,
    "observacao": "Observação atualizada com mais detalhes da devolução",
    "data_devolucao": "2026-03-07T15:00:00"
  }'
```

#### Atualização Parcial (PATCH)
```bash
curl -X PATCH "http://localhost:5003/api/v1/devolucoes/1" \
  -H "Content-Type: application/json" \
  -d '{
    "observacao": "Apenas a observação foi atualizada"
  }'
```

#### Deletar
```bash
curl -X DELETE "http://localhost:5003/api/v1/devolucoes/1"
```

## Diferenças em Relação às Demais Entidades

### Banco de Dados
- **Item**: `achados_perdidos.db`
- **Responsavel**: `responsavel.db`
- **Local**: `local.db`
- **Devolucao**: `devolucao.db`

### Relacionamentos
- `Devolucao` é a entidade de maior dependência do sistema: relaciona-se com `Item` (via `item_id`) e com `Reclamante` (via `reclamante_id`)
- As Foreign Keys estão temporariamente como campos INTEGER simples, a serem adicionadas quando a entidade `Reclamante` for implementada

### Data com Default Automático
- `data_devolucao` usa `default_factory=datetime.now` — ao criar uma devolução sem informar a data, é registrado o momento atual automaticamente

### Busca por Data
- `get_by_data()` compara apenas a **parte da data** (sem hora) usando `func.date()`, permitindo buscar todas as devoluções de um determinado dia

### Regra de Negócio de Data
- A data da devolução **não pode ser futura** — validada no `CreateDevolucaoUseCase` e `UpdateDevolucaoUseCase`

## Integração Futura com Reclamante e Item

Quando as entidades forem relacionadas:

### 1. Foreign Keys
```python
# Em devolucao/src/infrastructure/database/models.py
reclamante_id = Column(Integer, ForeignKey('reclamantes.id'), nullable=False)
item_id = Column(Integer, ForeignKey('items.id'), nullable=False)
```

### 2. Validação no Use Case
```python
# Em CreateDevolucaoUseCase
async def execute(self, devolucao: Devolucao, item_repository, reclamante_repository):
    item = await item_repository.get_by_id(devolucao.item_id)
    if not item:
        raise ValueError("Item não encontrado")
    if item.status != 'disponivel':
        raise ValueError("Item não está disponível para devolução")

    reclamante = await reclamante_repository.get_by_id(devolucao.reclamante_id)
    if not reclamante:
        raise ValueError("Reclamante não encontrado")

    # Marca o item como devolvido
    item.marcar_como_devolvido()
    await item_repository.update(item.id, item)

    return await self.repository.create(devolucao)
```

### 3. Response Expandido
```python
class DevolucaoResponseCompleta(BaseModel):
    id: int
    item: ItemResponse
    reclamante: ReclamanteResponse
    observacao: str
    data_devolucao: datetime
    created_at: datetime
    updated_at: Optional[datetime]
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
- **PUT vs PATCH**: Uso semântico correto
  - PUT: Atualização completa (todos os campos obrigatórios)
  - PATCH: Atualização parcial (campos opcionais, merge na camada de apresentação)
- **Resource-Oriented**: URLs representam recursos (`/api/v1/devolucoes/`)
- **HTTP Status Codes**: Uso apropriado (200, 201, 204, 400, 404)

## Arquivos Criados/Modificados

### Criados
```
devolucao/__init__.py
devolucao/src/__init__.py
devolucao/src/domain/__init__.py
devolucao/src/domain/entities/__init__.py
devolucao/src/domain/entities/devolucao.py
devolucao/src/domain/repositories/__init__.py
devolucao/src/domain/repositories/devolucao_repository.py
devolucao/src/application/__init__.py
devolucao/src/application/schemas/__init__.py
devolucao/src/application/schemas/devolucao_schema.py
devolucao/src/application/use_cases/__init__.py
devolucao/src/application/use_cases/devolucao_use_cases.py
devolucao/src/infrastructure/__init__.py
devolucao/src/infrastructure/database/__init__.py
devolucao/src/infrastructure/database/config.py
devolucao/src/infrastructure/database/models.py
devolucao/src/infrastructure/repositories/__init__.py
devolucao/src/infrastructure/repositories/devolucao_repository_impl.py
devolucao/src/presentation/__init__.py
devolucao/src/presentation/api/__init__.py
devolucao/src/presentation/api/routes/__init__.py
devolucao/src/presentation/api/routes/devolucao_routes.py
docs/ENTIDADE-DEVOLUCAO.md
```

### Modificados
```
main.py          # Inclusão de rotas e lifespan para init_db_devolucao()
```

## Referências

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Clean Architecture (Robert C. Martin)](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Pydantic Documentation](https://docs.pydantic.dev/)

---

**Grupo Ditko.br**
Projeto Frameworks Full Stack - Prof. Giovani Bontempo - Faculdade Impacta

**Data de Implementação**: 7 de Março de 2026



