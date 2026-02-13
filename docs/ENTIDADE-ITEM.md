# Implementação da Entidade Item - Arquitetura Diplomata

## O que foi implementado

### 1. Estrutura de Diretórios (Arquitetura Diplomata)

```
src/
├── domain/                           # Camada de Domínio
│   ├── entities/
│   │   └── item.py                  # Entidade Item com validações
│   └── repositories/
│       └── item_repository.py       # Interface do repositório (Port)
│
├── application/                      # Camada de Aplicação
│   ├── use_cases/
│   │   └── item_use_cases.py       # 7 casos de uso implementados
│   └── schemas/
│       └── item_schema.py          # Schemas Pydantic
│
├── infrastructure/                   # Camada de Infraestrutura
│   ├── database/
│   │   ├── config.py               # Configuração SQLAlchemy
│   │   └── models.py               # Modelo ORM ItemModel
│   └── repositories/
│       └── item_repository_impl.py # Implementação concreta
│
└── presentation/                     # Camada de Apresentação
    └── api/
        └── routes/
            └── item_routes.py       # Endpoints FastAPI
```

### 2. Domain Layer (Domínio)

#### Entidade Item (`item.py`)
- Dataclass com todos os atributos do diagrama
- Validações de negócio no `__post_init__`
- Métodos de domínio:
  - `marcar_como_devolvido()`
  - `atualizar_descricao()`
- Independente de frameworks

#### Interface ItemRepository (`item_repository.py`)
- Abstração (Port) para acesso a dados
- Métodos definidos:
  - `create()` - Criar item
  - `get_by_id()` - Buscar por ID
  - `get_all()` - Listar todos
  - `update()` - Atualizar
  - `delete()` - Deletar
  - `get_by_categoria()` - Buscar por categoria
  - `get_by_status()` - Buscar por status

### 3. Application Layer (Aplicação)

#### Use Cases (`item_use_cases.py`)
7 casos de uso implementados:
1. `CreateItemUseCase` - Criar novo item
2. `GetItemByIdUseCase` - Buscar item por ID
3. `GetAllItemsUseCase` - Listar todos os itens
4. `UpdateItemUseCase` - Atualizar item
5. `DeleteItemUseCase` - Deletar item
6. `GetItemsByCategoriaUseCase` - Buscar por categoria
7. `GetItemsByStatusUseCase` - Buscar por status

#### Schemas Pydantic (`item_schema.py`)
- `ItemBase` - Schema base
- `ItemCreate` - Para criação
- `ItemUpdate` - Para atualização (campos opcionais)
- `ItemResponse` - Para resposta
- `ItemListResponse` - Para listagem paginada

### 4. Infrastructure Layer (Infraestrutura)

#### Database Config (`config.py`)
- Setup do SQLAlchemy com async
- Engine assíncrono
- Session maker
- Função `get_session()` para dependency injection
- Função `init_db()` para criar tabelas

#### Model ORM (`models.py`)
- `ItemModel` - Modelo SQLAlchemy
- Mapeamento completo da tabela `items`
- **IMPORTANTE - Fase 1**: Foreign Keys temporariamente removidas
  - `local_id` e `responsavel_id` são campos INTEGER simples
  - As constraints serão adicionadas quando as entidades Local e Responsável forem implementadas
  - Isso permite testar a entidade Item isoladamente
- Timestamps automáticos (created_at, updated_at)

#### Repository Implementation (`item_repository_impl.py`)
- Implementação concreta de `ItemRepository`
- Conversões entre Entity e Model:
  - `_model_to_entity()` - ORM → Domain
  - `_entity_to_model()` - Domain → ORM
- Implementação de todos os métodos da interface
- Uso de SQLAlchemy async

### 5. Presentation Layer (Apresentação)

#### API Routes (`item_routes.py`)
Endpoints REST implementados:

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/v1/items/` | Criar novo item |
| GET | `/api/v1/items/{id}` | Buscar item por ID |
| GET | `/api/v1/items/` | Listar todos (paginado) |
| PUT | `/api/v1/items/{id}` | Atualizar item |
| DELETE | `/api/v1/items/{id}` | Deletar item |
| GET | `/api/v1/items/categoria/{categoria}` | Buscar por categoria |
| GET | `/api/v1/items/status/{status}` | Buscar por status |

- Dependency Injection do repositório
- Tratamento de erros com HTTPException
- Validação automática via Pydantic
- Documentação automática (OpenAPI/Swagger)

### 6. Arquivos de Configuração

#### `app.py` - Atualizado
- FastAPI app com metadados
- Lifespan para inicializar DB
- Inclusão das rotas
- Endpoint raiz com informações

#### `pyproject.toml` - Atualizado
- Dependências necessárias adicionadas:
  - `fastapi[standard]`
  - `sqlalchemy`
  - `aiosqlite`
  - `pydantic`
  - `pydantic-settings`

#### `ARCHITECTURE.md` - Criado
- Documentação completa da arquitetura
- Explicação de cada camada
- Princípios SOLID aplicados
- Exemplos de uso

## Benefícios da Implementação

### Separação de Responsabilidades
- Domain não conhece banco de dados
- Infrastructure não conhece regras de negócio
- Presentation não conhece detalhes de persistência

### Testabilidade
- Domain pode ser testado sem banco
- Use Cases podem ser testados com mocks
- Fácil criar testes unitários

### Manutenibilidade
- Código organizado e limpo
- Fácil localizar funcionalidades
- Mudanças isoladas em camadas

### Flexibilidade
- Trocar banco de dados sem afetar domínio
- Adicionar novos endpoints facilmente
- Substituir implementações

## Como Usar

### 1. Instalar Dependências
```bash
poetry install
```

### 2. Executar a Aplicação
```bash
poetry run uvicorn app:app --reload
```

### 3. Acessar Documentação
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 4. Testar Endpoints

#### Criar Item
```bash
curl -X POST "http://localhost:8000/api/v1/items/" \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Carteira de couro",
    "categoria": "documentos",
    "data_encontro": "2026-02-12T14:30:00",
    "descricao": "Carteira de couro marrom encontrada na biblioteca",
    "status": "disponivel",
    "local_id": 1,
    "responsavel_id": 1
  }'
```

#### Listar Todos
```bash
curl -X GET "http://localhost:8000/api/v1/items/"
```

#### Buscar por ID
```bash
curl -X GET "http://localhost:8000/api/v1/items/1"
```

#### Atualizar
```bash
curl -X PUT "http://localhost:8000/api/v1/items/1" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "devolvido"
  }'
```

#### Deletar
```bash
curl -X DELETE "http://localhost:8000/api/v1/items/1"
```

## Próximos Passos

### Fase Atual - Entidade Item (Concluída)
A primeira entidade foi implementada completamente seguindo a Arquitetura Diplomata. As foreign keys foram temporariamente removidas para permitir o funcionamento isolado nesta fase inicial.

### Entidades a Implementar
1. **Local** - Onde o item foi encontrado
   - Após implementação, adicionar FK: `items.local_id` → `locais.id`
2. **Responsável** - Quem registrou o item
   - Após implementação, adicionar FK: `items.responsavel_id` → `responsaveis.id`
3. **Reclamante** - Quem reivindica o item
4. **Devolução** - Registro da devolução
   - Relacionamento com Item e Reclamante

### Funcionalidades Adicionais
- Relacionamentos entre entidades
- Testes unitários e integração
- Autenticação JWT
- Paginação avançada
- Filtros e buscas
- Migrations com Alembic
- Docker e Docker Compose
- CI/CD

## Conceitos Aplicados

### Clean Architecture / Arquitetura Diplomata
- Separação em camadas
- Regra de dependência
- Inversão de dependências

### SOLID Principles
- **S**ingle Responsibility
- **O**pen/Closed
- **L**iskov Substitution
- **I**nterface Segregation
- **D**ependency Inversion

### Design Patterns
- Repository Pattern
- Dependency Injection
- DTO (Data Transfer Object)
- Use Case Pattern

## Referências

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Clean Architecture (Robert C. Martin)](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Arquitetura Diplomata](https://github.com/MatheusRabetti/clean-architecture-python)

---

**Grupo Ditko.br**
Projeto Frameworks Full Stack - Prof. Giovani Bontempo - Faculdade Impacta
