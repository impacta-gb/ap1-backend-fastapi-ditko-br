# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [Não Lançado]

### Corrigido

#### 1. Normalização de Status na Busca
- **Problema**: Busca por status não retornava todos os itens devido à falta de normalização do parâmetro de busca
- **Solução**: Adicionada normalização do parâmetro de busca (lowercase e remoção de acentos) no método `get_by_status()` do repositório
- **Arquivos**: 
  - `src/infrastructure/repositories/item_repository_impl.py`
- **Impacto**: Agora buscar por "disponivel", "Disponivel" ou "disponível" retorna todos os itens com esse status

#### 2. Conflito de Rotas
- **Problema**: Rotas específicas (`/categoria/{categoria}` e `/status/{status}`) após rota genérica (`/{item_id}`) causavam conflitos de roteamento
- **Solução**: Reordenadas as rotas para que rotas específicas venham antes da rota genérica
- **Arquivos**:
  - `src/presentation/api/routes/item_routes.py`
- **Impacto**: Evita que o FastAPI interprete erroneamente URLs específicas como IDs

#### 3. Contagem Incorreta para Paginação
- **Problema**: Campo `total` na listagem retornava apenas o tamanho da página atual ao invés do total real de itens
- **Solução**: 
  - Adicionado método `count()` na interface `ItemRepository`
  - Implementado `count()` usando `func.count()` do SQLAlchemy em `ItemRepositoryImpl`
  - Atualizada rota `GET /items/` para usar contagem real
- **Arquivos**:
  - `src/domain/repositories/item_repository.py`
  - `src/infrastructure/repositories/item_repository_impl.py`
  - `src/presentation/api/routes/item_routes.py`
- **Impacto**: Paginação no frontend agora funciona corretamente com total real de registros

#### 4. Falta de Validação no Update
- **Problema**: Método PUT não revalidava a entidade após modificar campos via `setattr()`
- **Solução**: Adicionada chamada a `__post_init__()` após modificações para revalidar regras de negócio
- **Arquivos**:
  - `src/presentation/api/routes/item_routes.py`
- **Impacto**: Previne atualização com dados inválidos (status incorreto, campos vazios, etc)

#### 5. Tratamento de Exceção no Update
- **Problema**: Exceções do use case não eram capturadas, resultando em erro 500
- **Solução**: Expandido bloco try-catch para cobrir todo o fluxo de atualização
- **Arquivos**:
  - `src/presentation/api/routes/item_routes.py`
- **Impacto**: Erros de validação agora retornam 400 Bad Request com mensagem clara

#### 6. Nomenclatura Inconsistente
- **Problema**: Parâmetro de rota era `{status}` mas variável era `status_param`
- **Solução**: Renomeado path parameter para `{status_value}` e variável para `status_value`
- **Arquivos**:
  - `src/presentation/api/routes/item_routes.py`
- **Impacto**: Código mais legível e consistente

### Refatorado

#### 7. Gerenciamento de Timestamps
- **Problema**: Entidade de domínio manipulava diretamente `updated_at`, violando separação de responsabilidades
- **Solução**: Removida manipulação manual de timestamps dos métodos da entidade, delegando ao SQLAlchemy
- **Arquivos**:
  - `src/domain/entities/item.py`
- **Impacto**: Melhor aderência à Clean Architecture; timestamps gerenciados automaticamente pela infraestrutura

#### 8. Use Cases com Lógica de Negócio
- **Problema**: Use cases eram apenas "pass-through" sem justificar sua existência
- **Solução**: Implementadas validações e regras de negócio em todos os use cases:
  - **CreateItemUseCase**: 
    - Força status inicial como 'disponivel'
    - Valida que data de encontro não seja futura
    - Valida IDs positivos
    - Preparado para validar existência de Local e Responsável
  - **GetItemByIdUseCase**: Valida ID positivo
  - **GetAllItemsUseCase**: Valida parâmetros de paginação (skip >= 0, limit entre 1-1000)
  - **UpdateItemUseCase**: 
    - Impede mudança de status para 'devolvido' diretamente
    - Valida data de encontro
    - Busca item existente para comparação
  - **DeleteItemUseCase**: 
    - Impede deleção de itens já devolvidos (preserva histórico)
    - Valida existência do item
  - **GetItemsByCategoriaUseCase**: Valida categoria não vazia
  - **GetItemsByStatusUseCase**: Normaliza e valida status contra lista de valores permitidos
- **Arquivos**:
  - `src/application/use_cases/item_use_cases.py`
  - `src/application/schemas/item_schema.py`
  - `src/presentation/api/routes/item_routes.py`
- **Impacto**: Use cases agora coordenam lógica de negócio e validações, justificando a camada de aplicação

### Adicionado

#### 9. Documentação de Status na Criação
- **Descrição**: Adicionada documentação clara de que status na criação é sempre 'disponivel'
- **Arquivos**:
  - `src/application/schemas/item_schema.py`
- **Impacto**: API mais clara para desenvolvedores frontend

#### 10. Entidade Responsavel com Clean Architecture
- **Descrição**: Implementação completa da entidade Responsavel seguindo padrões de Clean Architecture
- **Componentes**:
  - **Domain Layer**:
    - Entidade `Responsavel` com validações de domínio (nome, cargo, telefone, status ativo)
    - Interface `ResponsavelRepository` com todos os métodos CRUD
  - **Application Layer**:
    - Schemas Pydantic: `ResponsavelCreate`, `ResponsavelResponse`, `ResponsavelUpdate`, `ResponsavelPatch`, `ResponsavelStatusUpdate`, `ResponsavelListResponse`
    - Use Cases: `CreateResponsavelUseCase`, `GetResponsavelByIdUseCase`, `GetAllResponsaveisUseCase`, `UpdateResponsavelUseCase`, `DeleteResponsavelUseCase`, `GetResponsaveisByAtivoUseCase`
  - **Infrastructure Layer**:
    - `ResponsavelRepositoryImpl` com implementação assíncrona usando SQLAlchemy
    - `ResponsavelModel` para mapeamento ORM
    - Configuração de banco de dados independente
  - **Presentation Layer**:
    - Rotas REST completas: POST, GET (listagem e por ID), PUT, PATCH, DELETE
    - Rota específica para busca por status ativo: `GET /ativo/{value}`
    - Endpoint dedicado para alteração de status: `PATCH /{id}/status`
- **Arquivos**:
  - `responsavel/src/domain/entities/responsavel.py`
  - `responsavel/src/domain/repositories/responsavel_repository.py`
  - `responsavel/src/application/schemas/responsavel_schema.py`
  - `responsavel/src/application/use_cases/responsavel_use_cases.py`
  - `responsavel/src/infrastructure/repositories/responsavel_repository_impl.py`
  - `responsavel/src/infrastructure/database/models.py`
  - `responsavel/src/infrastructure/database/config.py`
  - `responsavel/src/presentation/api/routes/responsavel_routes.py`
  - `app.py`
- **Impacto**: Sistema agora possui gerenciamento completo de responsáveis por itens perdidos/encontrados

#### 11. Regra de Negócio: Controle de Status Ativo
- **Descrição**: Implementada regra de negócio que impede modificação direta do campo "ativo" em operações de atualização comuns
- **Comportamento**:
  - `PUT /responsaveis/{id}`: Atualiza nome, cargo e telefone, **mantém** status ativo existente
  - `PATCH /responsaveis/{id}`: Atualização parcial de nome, cargo e/ou telefone, **mantém** status ativo existente
  - `PATCH /responsaveis/{id}/status`: Endpoint dedicado exclusivamente para alterar status ativo/inativo
  - `POST /responsaveis/`: Criação sempre define `ativo=True` automaticamente
- **Justificativa**: Separação de responsabilidades - alteração de status é operação crítica de negócio que deve ser explícita
- **Arquivos**:
  - `responsavel/src/application/schemas/responsavel_schema.py` (removido campo `ativo` de `ResponsavelUpdate` e `ResponsavelPatch`)
  - `responsavel/src/presentation/api/routes/responsavel_routes.py` (implementada lógica de preservação de status)
- **Impacto**: Maior controle e auditabilidade sobre mudanças de status de responsáveis

#### 12. Validação de Telefone
- **Descrição**: Validação customizada de formato de telefone brasileiro
- **Regras**:
  - Apenas dígitos numéricos permitidos
  - Comprimento: 10 ou 11 dígitos (DDD + número)
  - Remove caracteres de formatação antes de validar
- **Arquivos**:
  - `responsavel/src/application/schemas/responsavel_schema.py`
- **Impacto**: Garante consistência nos dados de contato

### Corrigido

#### 13. Estrutura de Módulos Python
- **Problema**: Módulo `responsavel` não era reconhecido como pacote Python importável
- **Solução**: Criado arquivo `responsavel/__init__.py` para tornar o diretório um módulo válido
- **Arquivos**:
  - `responsavel/__init__.py`
- **Impacto**: Permite importação correta do módulo responsavel em app.py

#### 14. Importações Relativas Incorretas
- **Problema**: Arquivos dentro de `responsavel/` usavam importação `from src.` ao invés de `from responsavel.src.`
- **Solução**: Corrigidas todas as importações para usar caminho absoluto correto
- **Arquivos**:
  - `responsavel/src/infrastructure/repositories/responsavel_repository_impl.py`
  - `responsavel/src/domain/repositories/responsavel_repository.py`
  - `responsavel/src/infrastructure/database/models.py`
  - `responsavel/src/application/use_cases/responsavel_use_cases.py`
  - `responsavel/src/presentation/api/routes/responsavel_routes.py`
- **Impacto**: Elimina erros de ModuleNotFoundError durante inicialização da aplicação

#### 15. Duplicação de Prefixo de Rotas
- **Problema**: Rotas definiam prefixo no router e novamente no `app.include_router()`, causando URLs como `/api/v1/items/items/`
- **Solução**: Removido prefixo dos routers (`APIRouter(tags=[...])`), mantendo apenas no app.py
- **Arquivos**:
  - `src/presentation/api/routes/item_routes.py` (removido `prefix="/items"`)
  - `responsavel/src/presentation/api/routes/responsavel_routes.py` (removido `prefix="/responsaveis"`)
- **Impacto**: URLs corretas: `/api/v1/items/` e `/api/v1/responsaveis/`

#### 16. Conflito de Nomes em Imports
- **Problema**: Importações duplicadas de `init_db` com mesmo nome causavam conflito
- **Solução**: Renomeadas importações com aliases: `init_db_item` e `init_db_responsavel`
- **Arquivos**:
  - `app.py`
- **Impacto**: Ambos os bancos de dados são inicializados corretamente no startup

### Refatorado

#### 17. Separação de Schemas de Update
- **Descrição**: Criados schemas distintos para diferentes tipos de atualização
- **Schemas**:
  - `ResponsavelUpdate`: PUT - atualização completa (nome, cargo, telefone - campos obrigatórios)
  - `ResponsavelPatch`: PATCH - atualização parcial (nome, cargo, telefone - campos opcionais)
  - `ResponsavelStatusUpdate`: PATCH /status - alteração de status ativo (campo único obrigatório)
- **Justificativa**: Seguir convenções REST (PUT vs PATCH) e isolar operação crítica de mudança de status
- **Arquivos**:
  - `responsavel/src/application/schemas/responsavel_schema.py`
  - `responsavel/src/presentation/api/routes/responsavel_routes.py`
- **Impacto**: API mais semântica e aderente a padrões REST

## [1.0.0] - 2026-02-26

### Implementado
- Sistema de Achados e Perdidos com arquitetura Clean Architecture (Arquitetura Diplomata)
- CRUD completo para entidade Item
- Busca por categoria e status
- Paginação de resultados
- Validações de domínio
- Integração com SQLite usando SQLAlchemy async
- API REST com FastAPI
- Documentação automática com Swagger/OpenAPI

### Estrutura
- **Domain Layer**: Entidades e interfaces de repositório
- **Application Layer**: Use cases e schemas
- **Infrastructure Layer**: Implementações de repositório e configuração de banco
- **Presentation Layer**: Rotas da API REST

---

## Legenda de Tipos de Mudança

- **Adicionado**: Novas funcionalidades
- **Corrigido**: Correções de bugs
- **Alterado**: Mudanças em funcionalidades existentes
- **Descontinuado**: Funcionalidades que serão removidas
- **Removido**: Funcionalidades removidas
- **Refatorado**: Melhorias de código sem alterar comportamento externo
- **Segurança**: Correções de vulnerabilidades
