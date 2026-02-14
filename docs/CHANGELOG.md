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

## [1.0.0] - 2026-02-14

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
