# Implementação da Entidade Responsavel - Arquitetura Diplomata

## O que foi implementado

### 1. Estrutura de Diretórios (Arquitetura Diplomata)

```
responsavel/
├── src/
│   ├── domain/                           # Camada de Domínio
│   │   ├── entities/
│   │   │   └── responsavel.py           # Entidade Responsavel com validações
│   │   └── repositories/
│   │       └── responsavel_repository.py # Interface do repositório (Port)
│   │
│   ├── application/                      # Camada de Aplicação
│   │   ├── use_cases/
│   │   │   └── responsavel_use_cases.py # 6 casos de uso implementados
│   │   └── schemas/
│   │       └── responsavel_schema.py    # Schemas Pydantic
│   │
│   ├── infrastructure/                   # Camada de Infraestrutura
│   │   ├── database/
│   │   │   ├── config.py               # Configuração SQLAlchemy
│   │   │   └── models.py               # Modelo ORM ResponsavelModel
│   │   └── repositories/
│   │       └── responsavel_repository_impl.py # Implementação concreta
│   │
│   └── presentation/                     # Camada de Apresentação
│       └── api/
│           └── routes/
│               └── responsavel_routes.py # Endpoints FastAPI
└── __init__.py                          # Torna responsavel um módulo Python
```

### 2. Domain Layer (Domínio)

#### Entidade Responsavel (`responsavel.py`)
- Dataclass com todos os atributos do diagrama
- Validações de negócio no `__post_init__`:
  - Nome: mínimo 3 caracteres, máximo 255
  - Cargo: mínimo 3 caracteres, máximo 255
  - Telefone: formato brasileiro (10-11 dígitos)
  - Ativo: booleano (default True)
- Métodos de domínio:
  - `ativar()` - Marca responsável como ativo
  - `desativar()` - Marca responsável como inativo
- Independente de frameworks

#### Interface ResponsavelRepository (`responsavel_repository.py`)
- Abstração (Port) para acesso a dados
- Métodos definidos:
  - `create()` - Criar responsável
  - `get_by_id()` - Buscar por ID
  - `get_all()` - Listar todos
  - `update()` - Atualizar
  - `delete()` - Deletar
  - `get_by_ativo()` - Buscar por status ativo
  - `count()` - Contar total de registros

### 3. Application Layer (Aplicação)

#### Use Cases (`responsavel_use_cases.py`)
6 casos de uso implementados:
1. `CreateResponsavelUseCase` - Criar novo responsável
2. `GetResponsavelByIdUseCase` - Buscar responsável por ID
3. `GetAllResponsaveisUseCase` - Listar todos os responsáveis
4. `UpdateResponsavelUseCase` - Atualizar responsável
5. `DeleteResponsavelUseCase` - Deletar responsável
6. `GetResponsaveisByAtivoUseCase` - Buscar por status ativo

#### Schemas Pydantic (`responsavel_schema.py`)
- `ResponsavelCreate` - Para criação (nome, cargo, telefone)
- `ResponsavelUpdate` - Para atualização completa PUT (nome, cargo, telefone - campos obrigatórios)
- `ResponsavelPatch` - Para atualização parcial PATCH (campos opcionais)
- `ResponsavelStatusUpdate` - Para alteração de status ativo/inativo
- `ResponsavelResponse` - Para resposta da API
- `ResponsavelListResponse` - Para listagem paginada
- **Validação customizada de telefone**:
  - Remove caracteres de formatação
  - Valida apenas dígitos numéricos
  - Valida comprimento (10-11 dígitos)

### 4. Infrastructure Layer (Infraestrutura)

#### Database Config (`config.py`)
- Setup do SQLAlchemy com async
- Engine assíncrono para banco SQLite separado (`responsavel.db`)
- Session maker específico
- Função `get_session()` para dependency injection
- Função `init_db()` para criar tabelas

#### Model ORM (`models.py`)
- `ResponsavelModel` - Modelo SQLAlchemy
- Mapeamento completo da tabela `responsaveis`
- Campos:
  - `id` - INTEGER PRIMARY KEY
  - `nome` - VARCHAR(255) NOT NULL
  - `cargo` - VARCHAR(255) NOT NULL
  - `telefone` - VARCHAR(11) NOT NULL
  - `ativo` - BOOLEAN DEFAULT TRUE

#### Repository Implementation (`responsavel_repository_impl.py`)
- Implementação concreta de `ResponsavelRepository`
- Conversões entre Entity e Model:
  - `_model_to_entity()` - ORM → Domain
  - `_entity_to_model()` - Domain → ORM
- Implementação de todos os métodos da interface
- Uso de SQLAlchemy async
- Método `count()` usando `func.count()` para paginação correta

### 5. Presentation Layer (Apresentação)

#### API Routes (`responsavel_routes.py`)
Endpoints REST implementados:

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/v1/responsaveis/` | Criar novo responsável (sempre ativo=True) |
| GET | `/api/v1/responsaveis/{id}` | Buscar responsável por ID |
| GET | `/api/v1/responsaveis/` | Listar todos (paginado) |
| GET | `/api/v1/responsaveis/ativo/{value}` | Buscar por status ativo |
| PUT | `/api/v1/responsaveis/{id}` | Atualizar responsável (não altera ativo) |
| PATCH | `/api/v1/responsaveis/{id}` | Atualização parcial (não altera ativo) |
| PATCH | `/api/v1/responsaveis/{id}/status` | Alterar status ativo/inativo |
| DELETE | `/api/v1/responsaveis/{id}` | Deletar responsável |

**Características especiais:**
- Dependency Injection do repositório
- Tratamento de erros com HTTPException
- Validação automática via Pydantic
- Documentação automática (OpenAPI/Swagger)
- **Regra de negócio**: Campo `ativo` não pode ser alterado em PUT/PATCH comum

### 6. Arquivos de Configuração

#### `app.py` - Atualizado
- Importação do módulo responsavel
- Lifespan atualizado para inicializar ambos os bancos:
  - `init_db_item()` - Banco de items
  - `init_db_responsavel()` - Banco de responsaveis
- Inclusão das rotas de responsavel
- Prefixo: `/api/v1/responsaveis`

#### `responsavel/__init__.py` - Criado
- Torna o diretório `responsavel` um módulo Python importável
- Permite importação correta das rotas no app.py

## Regra de Negócio Implementada

### Controle de Status Ativo

**Problema**: O campo `ativo` é crítico para o sistema e não deve ser alterado inadvertidamente durante atualizações normais de dados.

**Solução**: Separação de responsabilidades através de endpoints específicos.

#### Comportamento por Endpoint:

1. **POST `/responsaveis/`** - Criação
   - Status `ativo` sempre definido como `True`
   - Não permite especificar na criação
   
2. **PUT `/responsaveis/{id}`** - Atualização Completa
   - Atualiza: nome, cargo, telefone (obrigatórios)
   - **Mantém**: status ativo existente
   - Schema: `ResponsavelUpdate` (sem campo ativo)
   
3. **PATCH `/responsaveis/{id}`** - Atualização Parcial
   - Atualiza: nome, cargo e/ou telefone (opcionais)
   - **Mantém**: status ativo existente
   - Schema: `ResponsavelPatch` (sem campo ativo)
   
4. **PATCH `/responsaveis/{id}/status`** - Alteração de Status
   - **Único endpoint** que pode alterar o status ativo
   - Schema dedicado: `ResponsavelStatusUpdate`
   - Campo único: `ativo` (obrigatório)

#### Justificativa:
- **Segurança**: Previne alterações acidentais de status
- **Auditabilidade**: Status só muda através de operação explícita
- **Separação de Responsabilidades**: Operações de dados vs operações de estado
- **Compatibilidade REST**: Uso semântico correto de PUT vs PATCH

## Benefícios da Implementação

### Modularidade
- Módulo `responsavel` completamente independente
- Pode ser reutilizado em outros projetos
- Banco de dados separado facilita escalabilidade

### Separação de Responsabilidades
- Domain não conhece banco de dados
- Infrastructure não conhece regras de negócio
- Presentation não conhece detalhes de persistência

### Validação em Múltiplas Camadas
- **Schema (Pydantic)**: Validação de formato e tipo
- **Entity (Domain)**: Validação de regras de negócio
- **Use Case**: Validação de fluxo e contexto

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

### 1. Executar a Aplicação
```bash
poetry run uvicorn app:app --reload
```

### 2. Acessar Documentação
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 3. Testar Endpoints

#### Criar Responsável
```bash
curl -X POST "http://localhost:8000/api/v1/responsaveis/" \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "João Silva",
    "cargo": "Recepcionista",
    "telefone": "11987654321"
  }'
```

**Resposta:**
```json
{
  "id": 1,
  "nome": "João Silva",
  "cargo": "Recepcionista",
  "telefone": "11987654321",
  "ativo": true
}
```

#### Listar Todos (Paginado)
```bash
curl -X GET "http://localhost:8000/api/v1/responsaveis/?skip=0&limit=10"
```

**Resposta:**
```json
{
  "responsaveis": [
    {
      "id": 1,
      "nome": "João Silva",
      "cargo": "Recepcionista",
      "telefone": "11987654321",
      "ativo": true
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 10
}
```

#### Buscar por ID
```bash
curl -X GET "http://localhost:8000/api/v1/responsaveis/1"
```

#### Buscar por Status Ativo
```bash
# Buscar apenas ativos
curl -X GET "http://localhost:8000/api/v1/responsaveis/ativo/true"

# Buscar apenas inativos
curl -X GET "http://localhost:8000/api/v1/responsaveis/ativo/false"
```

#### Atualizar Dados (PUT)
```bash
curl -X PUT "http://localhost:8000/api/v1/responsaveis/1" \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "João Pedro Silva",
    "cargo": "Supervisor de Recepção",
    "telefone": "11987654322"
  }'
```
**Nota**: Status `ativo` permanece inalterado.

#### Atualização Parcial (PATCH)
```bash
# Atualizar apenas o telefone
curl -X PATCH "http://localhost:8000/api/v1/responsaveis/1" \
  -H "Content-Type: application/json" \
  -d '{
    "telefone": "11999887766"
  }'
```
**Nota**: Outros campos permanecem inalterados.

#### Alterar Status (PATCH /status)
```bash
# Desativar responsável
curl -X PATCH "http://localhost:8000/api/v1/responsaveis/1/status" \
  -H "Content-Type: application/json" \
  -d '{
    "ativo": false
  }'

# Reativar responsável
curl -X PATCH "http://localhost:8000/api/v1/responsaveis/1/status" \
  -H "Content-Type: application/json" \
  -d '{
    "ativo": true
  }'
```

#### Deletar
```bash
curl -X DELETE "http://localhost:8000/api/v1/responsaveis/1"
```

## Validações Implementadas

### 1. Validação de Telefone

**Schema Layer (Pydantic)**:
```python
@field_validator('telefone')
@classmethod
def validate_telefone(cls, v: str) -> str:
    telefone_limpo = v.replace("(", "").replace(")", "").replace("-", "").replace(" ", "")
    
    if not telefone_limpo.isdigit():
        raise ValueError("Telefone deve conter apenas números")
    
    if len(telefone_limpo) < 10 or len(telefone_limpo) > 11:
        raise ValueError("Telefone deve ter 10 ou 11 dígitos (DDD + número)")
    
    return v
```

**Formatos Aceitos**:
- `11987654321` ✓
- `(11) 98765-4321` ✓
- `11 98765-4321` ✓
- `1234` ✗ (muito curto)
- `abc12345678` ✗ (contém letras)

### 2. Validação de Domínio

**Entity Layer**:
```python
def __post_init__(self):
    if len(self.nome) < 3 or len(self.nome) > 255:
        raise ValueError("Nome deve ter entre 3 e 255 caracteres")
    
    if len(self.cargo) < 3 or len(self.cargo) > 255:
        raise ValueError("Cargo deve ter entre 3 e 255 caracteres")
    
    telefone_limpo = self.telefone.replace("(", "").replace(")", "").replace("-", "").replace(" ", "")
    if not telefone_limpo.isdigit() or len(telefone_limpo) not in [10, 11]:
        raise ValueError("Telefone inválido")
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
  - PATCH: Atualização parcial (campos opcionais)
- **Resource-Oriented**: URLs representam recursos
- **HTTP Status Codes**: Uso apropriado (200, 201, 204, 400, 404)
- **Idempotência**: PUT e DELETE são idempotentes

## Diferenças da Entidade Item

### Estrutura Modular
- **Item**: Dentro de `src/`
- **Responsavel**: Módulo separado `responsavel/src/`
- **Motivo**: Demonstrar modularização e independência

### Banco de Dados
- **Item**: `items.db`
- **Responsavel**: `responsavel.db`
- **Motivo**: Isolamento e potencial para microserviços

### Regra de Negócio Específica
- **Item**: Status pode mudar entre disponível/devolvido
- **Responsavel**: Status ativo só muda via endpoint dedicado
- **Motivo**: Diferentes requisitos de negócio

### Schemas de Update
- **Item**: Schema único para PUT/PATCH
- **Responsavel**: Schemas separados (Update, Patch, StatusUpdate)
- **Motivo**: Maior controle e semântica REST

### Busca Adicional
- **Item**: Busca por categoria e status
- **Responsavel**: Busca por status ativo (booleano)
- **Motivo**: Casos de uso diferentes

## Integração Futura com Item

Quando as entidades forem relacionadas:

### 1. Foreign Key em Item
```python
# Em src/infrastructure/database/models.py (ItemModel)
responsavel_id = Column(Integer, ForeignKey('responsaveis.id'), nullable=False)
```

### 2. Relationship ORM
```python
# Em ItemModel
responsavel = relationship("ResponsavelModel", back_populates="items")

# Em ResponsavelModel
items = relationship("ItemModel", back_populates="responsavel")
```

### 3. Validação no Use Case
```python
# Em CreateItemUseCase
async def execute(self, item: Item, responsavel_repository: ResponsavelRepository):
    # Validar se responsável existe e está ativo
    responsavel = await responsavel_repository.get_by_id(item.responsavel_id)
    if not responsavel:
        raise ValueError("Responsável não encontrado")
    if not responsavel.ativo:
        raise ValueError("Responsável inativo não pode registrar itens")
    
    return await self.repository.create(item)
```

### 4. Response Expandido
```python
# Schema com responsável aninhado
class ItemResponseWithResponsavel(BaseModel):
    id: int
    nome: str
    # ... outros campos
    responsavel: ResponsavelResponse
```

## Próximos Passos

### Entidades a Implementar
1. **Local** - Onde o item foi encontrado
2. **Reclamante** - Quem reivindica o item
3. **Devolução** - Registro da devolução
   - Relacionamento com Item, Responsavel e Reclamante

### Melhorias Técnicas
- Testes unitários para todas as camadas
- Testes de integração
- Migrations com Alembic
- Logging estruturado
- Cache com Redis
- Rate limiting
- Autenticação e autorização (JWT)

### Funcionalidades Avançadas
- Upload de fotos de itens
- Notificações por email/SMS
- Dashboard de estatísticas
- Relatórios em PDF
- Busca full-text
- Exportação de dados (CSV, Excel)

## Arquivos Criados/Modificados

### Criados
```
responsavel/__init__.py
responsavel/src/domain/entities/responsavel.py
responsavel/src/domain/repositories/responsavel_repository.py
responsavel/src/application/schemas/responsavel_schema.py
responsavel/src/application/use_cases/responsavel_use_cases.py
responsavel/src/infrastructure/database/config.py
responsavel/src/infrastructure/database/models.py
responsavel/src/infrastructure/repositories/responsavel_repository_impl.py
responsavel/src/presentation/api/routes/responsavel_routes.py
docs/ENTIDADE-RESPONSAVEL.md
```

### Modificados
```
app.py                  # Inclusão de rotas e lifespan
docs/CHANGELOG.md       # Documentação de mudanças
```

## Referências

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Clean Architecture (Robert C. Martin)](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [REST API Best Practices](https://restfulapi.net/)
- [Pydantic Validation](https://docs.pydantic.dev/latest/concepts/validators/)

---

**Grupo Ditko.br**  
Projeto Frameworks Full Stack - Prof. Giovani Bontempo - Faculdade Impacta

**Data de Implementação**: 26 de Fevereiro de 2026
