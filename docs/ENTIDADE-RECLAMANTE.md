# Implementação da Entidade Reclamante - Arquitetura Diplomata

## O que foi implementado

### 1. Estrutura de Diretórios (Arquitetura Diplomata)

```
reclamante/
├── src/
│   ├── domain/                           # Camada de Domínio
│   │   ├── entities/
│   │   │   └── reclamante.py           # Entidade Reclamante com validações
│   │   └── repositories/
│   │       └── reclamante_repository.py # Interface do repositório (Port)
│   │
│   ├── application/                      # Camada de Aplicação
│   │   ├── use_cases/
│   │   │   └── reclamante_use_cases.py  # 5 casos de uso implementados
│   │   └── schemas/
│   │       └── reclamante_schema.py     # Schemas Pydantic
│   │
│   ├── infrastructure/                   # Camada de Infraestrutura
│   │   ├── database/
│   │   │   ├── config.py               # Configuração SQLAlchemy
│   │   │   └── models.py               # Modelo ORM ReclamanteModel
│   │   └── repositories/
│   │       └── reclamante_repository_impl.py # Implementação concreta
│   │
│   └── presentation/                     # Camada de Apresentação
│       └── api/
│           └── routes/
│               └── reclamante_routes.py # Endpoints FastAPI
└── __init__.py                          # Torna reclamante um módulo Python
```

### 2. Domain Layer (Domínio)

#### Entidade Reclamante (reclamante.py)
- Dataclass com os campos nome, telefone, documento e id
- Validações de negócio no __post_init__:
  - Nome: não pode estar vazio
  - Telefone: não pode estar vazio
  - Documento: não pode estar vazio
- Método de domínio:
  - atualizar_telefone() - Atualiza o telefone com validação
- Independente de frameworks

#### Interface ReclamanteRepository (reclamante_repository.py)
- Abstração (Port) para acesso a dados
- Métodos definidos:
  - create() - Criar reclamante
  - get_by_id() - Buscar por ID
  - get_all() - Listar todos com paginação
  - update() - Atualizar
  - delete() - Deletar
  - count() - Contar total de registros

### 3. Application Layer (Aplicação)

#### Use Cases (reclamante_use_cases.py)
5 casos de uso implementados:
1. CreateReclamanteUseCase - Criar novo reclamante
2. GetReclamanteByIdUseCase - Buscar reclamante por ID
3. GetAllReclamantesUseCase - Listar todos os reclamantes
4. UpdateReclamanteUseCase - Atualizar reclamante
5. DeleteReclamanteUseCase - Deletar reclamante

#### Schemas Pydantic (reclamante_schema.py)
- ReclamanteBase - Schema base com campos comuns
- ReclamanteCreate - Para criação
- ReclamanteUpdate - Para atualização
- ReclamanteResponse - Para resposta da API
- ReclamanteListResponse - Para listagem paginada

### 4. Infrastructure Layer (Infraestrutura)

#### Database Config (config.py)
- Setup do SQLAlchemy com async
- Engine assíncrono para banco SQLite separado (reclamante.db)
- Session maker específico com async_sessionmaker
- Função get_session() para dependency injection
- Função init_db() para criar tabelas

#### Model ORM (models.py)
- ReclamanteModel - Modelo SQLAlchemy
- Mapeamento completo da tabela reclamantes
- Campos:
  - id - INTEGER PRIMARY KEY AUTOINCREMENT
  - nome - VARCHAR(255) NOT NULL
  - documento - VARCHAR(255) NOT NULL
  - telefone - VARCHAR(100) NOT NULL
- Índices nos campos id, nome, documento e telefone

#### Repository Implementation (reclamante_repository_impl.py)
- Implementação concreta de ReclamanteRepository
- Conversões entre Entity e Model:
  - _model_to_entity() - ORM -> Domain
  - _entity_to_model() - Domain -> ORM
- Implementação de todos os métodos da interface
- Método count() usando func.count() para paginação
- Uso de SQLAlchemy async com select()

### 5. Presentation Layer (Apresentação)

#### API Routes (reclamante_routes.py)
Endpoints REST implementados:

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | /api/v1/reclamantes/ | Criar novo reclamante |
| GET | /api/v1/reclamantes/ | Listar todos (paginado) |
| GET | /api/v1/reclamantes/{reclamante_id} | Buscar reclamante por ID |
| PUT | /api/v1/reclamantes/{reclamante_id} | Atualizar reclamante |
| DELETE | /api/v1/reclamantes/{reclamante_id} | Deletar reclamante |

Caracteristicas:
- Dependency Injection do repositório via Depends(get_session)
- Tratamento de erros com HTTPException
- Validação automática via Pydantic
- Documentação automática (OpenAPI/Swagger)

### 6. Arquivos de Configuração

#### app.py - Atualizado
- Importação do módulo reclamante
- Lifespan atualizado para inicializar os cinco bancos:
  - init_db_item() - Banco de items
  - init_db_responsavel() - Banco de responsaveis
  - init_db_local() - Banco de locais
  - init_db_devolucao() - Banco de devoluções
  - init_db_reclamante() - Banco de reclamantes
- Inclusão das rotas de reclamante
- Prefixo: /api/v1/reclamantes

## Validações Implementadas

### Domain Layer (Entidade)

```python
def __post_init__(self):
    if not self.nome or len(self.nome.strip()) == 0:
        raise ValueError("Nome do reclamante é obrigatório")

    if not self.telefone or len(self.telefone.strip()) == 0:
        raise ValueError("Telefone do reclamante é obrigatório")

    if not self.documento or len(self.documento.strip()) == 0:
        raise ValueError("Documento do reclamante é obrigatório")
```

### Application Layer (Schema Pydantic)

```python
class ReclamanteBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=255)
    telefone: str = Field(..., min_length=1, max_length=100)
    documento: str = Field(...)
```

### Use Case Layer

```python
# GetReclamanteByIdUseCase
if id <= 0:
    raise ValueError("ID de reclamante deve ser maior que zero")

# GetAllReclamantesUseCase
if skip < 0:
    raise ValueError("Skip não pode ser negativo")
if limit <= 0 or limit > 1000:
    raise ValueError("Limit deve estar entre 1 e 1000")
```

## Benefícios da Implementação

### Modularidade
- Módulo reclamante independente das demais entidades
- Estrutura compatível com evolução para serviços separados
- Banco de dados isolado facilita manutenção

### Separação de Responsabilidades
- Domain não conhece banco de dados
- Infrastructure não conhece regras de negócio
- Presentation não conhece detalhes de persistência

### Testabilidade
- Domain pode ser testado sem banco de dados
- Use Cases podem ser testados com mocks do repositório
- Repositório pode ser validado com testes de integração

### Manutenibilidade
- Código organizado em camadas com responsabilidades claras
- Mudanças isoladas por camada
- Fácil localizar a lógica de cada operação

## Como Usar

### 1. Executar a Aplicação
```bash
poetry run uvicorn app:app --reload
```

### 2. Acessar Documentação
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 3. Testar Endpoints

#### Criar Reclamante
```bash
curl -X POST "http://localhost:8000/api/v1/reclamantes/" \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Maria Aparecida Souza",
    "telefone": "11987654321",
    "documento": "12345678900"
  }'
```

Resposta:
```json
{
  "id": 1,
  "nome": "Maria Aparecida Souza",
  "telefone": "11987654321",
  "documento": "12345678900"
}
```

#### Listar Todos
```bash
curl -X GET "http://localhost:8000/api/v1/reclamantes/?skip=0&limit=10"
```

Resposta:
```json
{
  "reclamantes": [
    {
      "id": 1,
      "nome": "Maria Aparecida Souza",
      "telefone": "11987654321",
      "documento": "12345678900"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 10
}
```

#### Buscar por ID
```bash
curl -X GET "http://localhost:8000/api/v1/reclamantes/1"
```

#### Atualizar
```bash
curl -X PUT "http://localhost:8000/api/v1/reclamantes/1" \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Maria Souza",
    "telefone": "11999998888",
    "documento": "12345678900"
  }'
```

#### Deletar
```bash
curl -X DELETE "http://localhost:8000/api/v1/reclamantes/1"
```

## Diferenças em Relação às Demais Entidades

### Banco de Dados
- Item: achados_perdidos.db ou banco configurado na raiz do módulo item
- Responsavel: responsavel.db
- Local: local.db
- Devolucao: devolucao.db
- Reclamante: reclamante.db

### Estrutura de Dados
- Reclamante é uma entidade simples, sem timestamps e sem controle de status
- O foco atual está no cadastro e gerenciamento básico dos dados do reclamante
- Ainda não há relacionamentos ORM explícitos com devolução

### Operações Disponíveis
- Possui CRUD básico com listagem paginada
- Não possui PATCH dedicado
- Não possui buscas especializadas por documento ou telefone

## Integração Futura com Devolucao

Quando as entidades forem relacionadas:

### 1. Foreign Key em Devolucao
```python
# Em devolucao/src/infrastructure/database/models.py
reclamante_id = Column(Integer, ForeignKey('reclamantes.id'), nullable=False)
```

### 2. Validação no Use Case
```python
# Em CreateDevolucaoUseCase
async def execute(self, devolucao: Devolucao, reclamante_repository):
    reclamante = await reclamante_repository.get_by_id(devolucao.reclamante_id)
    if not reclamante:
        raise ValueError("Reclamante não encontrado")

    return await self.repository.create(devolucao)
```

### 3. Response Expandido
```python
class DevolucaoResponseCompleta(BaseModel):
    id: int
    reclamante: ReclamanteResponse
    item_id: int
    observacao: str
    data_devolucao: datetime
```

## Conceitos Aplicados

### Clean Architecture / Arquitetura Diplomata
- Separação em camadas: Domain, Application, Infrastructure, Presentation
- Regra de dependência: camadas internas não conhecem externas
- Inversão de dependências: use cases dependem de interfaces, não implementações

### SOLID Principles
- Single Responsibility: cada classe tem uma única responsabilidade
- Open/Closed: estrutura preparada para extensão
- Liskov Substitution: implementações podem substituir a interface do repositório
- Interface Segregation: interface enxuta e focada no agregado reclamante
- Dependency Inversion: dependência de abstrações, não de concretizações

### Design Patterns
- Repository Pattern
- Dependency Injection
- DTO (Data Transfer Object)
- Use Case Pattern

### REST API Best Practices
- Resource-Oriented: URLs representam recursos
- HTTP Status Codes: uso apropriado de 200, 201, 204, 400 e 404
- Paginação via query params skip e limit

## Arquivos Criados/Modificados

### Criados
```
reclamante/__init__.py
reclamante/src/__init__.py
reclamante/src/domain/__init__.py
reclamante/src/domain/entities/__init__.py
reclamante/src/domain/entities/reclamante.py
reclamante/src/domain/repositories/__init__.py
reclamante/src/domain/repositories/reclamante_repository.py
reclamante/src/application/__init__.py
reclamante/src/application/schemas/__init__.py
reclamante/src/application/schemas/reclamante_schema.py
reclamante/src/application/use_cases/__init__.py
reclamante/src/application/use_cases/reclamante_use_cases.py
reclamante/src/infrastructure/__init__.py
reclamante/src/infrastructure/database/__init__.py
reclamante/src/infrastructure/database/config.py
reclamante/src/infrastructure/database/models.py
reclamante/src/infrastructure/repositories/__init__.py
reclamante/src/infrastructure/repositories/reclamante_repository_impl.py
reclamante/src/presentation/__init__.py
reclamante/src/presentation/api/__init__.py
reclamante/src/presentation/api/routes/__init__.py
reclamante/src/presentation/api/routes/reclamante_routes.py
docs/ENTIDADE-RECLAMANTE.md
```

### Modificados
```
app.py          # Inclusão de rotas e lifespan para init_db_reclamante()
```

## Referências

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Clean Architecture (Robert C. Martin)](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Pydantic Documentation](https://docs.pydantic.dev/)

---

**Grupo Ditko.br**
Projeto Frameworks Full Stack - Prof. Giovani Bontempo - Faculdade Impacta

**Data de Implementação**: 13 de Março de 2026