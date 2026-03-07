# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [Não Lançado]

### Adicionado

#### 27. Entidade Devolucao com Clean Architecture
- **Descrição**: Implementação completa da entidade Devolucao seguindo padrões de Clean Architecture (Arquitetura Diplomata)
- **Componentes**:
  - **Domain Layer**:
    - Entidade `Devolucao` com validações de domínio (`reclamante_id` e `item_id` positivos, `observacao` não vazia)
    - Campo `data_devolucao` com `default_factory=datetime.now` (registra data/hora atual automaticamente)
    - Método de domínio `atualizar_observacao()` com validação
    - Interface `DevolucaoRepository` com métodos CRUD + `get_by_data()` + `count()`
  - **Application Layer**:
    - Schemas Pydantic: `DevolucaoBase`, `DevolucaoCreate`, `DevolucaoUpdate`, `DevolucaoPatch`, `DevolucaoResponse` (com `created_at`/`updated_at`), `DevolucaoListResponse`
    - Use Cases: `CreateDevolucaoUseCase`, `GetDevolucaoByIdUseCase`, `GetAllDevolucoesUseCase`, `UpdateDevolucaoUseCase`, `DeleteDevolucaoUseCase`, `GetDevolucoesByDataUseCase`, `CountDevolucoesUseCase`
    - Regra de negócio: data da devolução não pode ser futura
  - **Infrastructure Layer**:
    - `DevolucaoRepositoryImpl` com implementação assíncrona usando SQLAlchemy
    - `DevolucaoModel` com colunas `created_at` (server_default) e `updated_at` (onupdate)
    - `get_by_data()` compara apenas a parte da data usando `func.date()`, sem considerar hora
    - Configuração de banco de dados independente (`devolucao.db`)
  - **Presentation Layer**:
    - Rotas REST completas: POST `/`, GET `/`, GET `/data/{data}`, GET `/{id}`, PUT `/{id}`, PATCH `/{id}`, DELETE `/{id}`
    - PATCH reutiliza `UpdateDevolucaoUseCase` com merge dos campos na camada de apresentação
- **Arquivos criados**:
  - `devolucao/__init__.py`
  - `devolucao/src/domain/entities/devolucao.py`
  - `devolucao/src/domain/repositories/devolucao_repository.py`
  - `devolucao/src/application/schemas/devolucao_schema.py`
  - `devolucao/src/application/use_cases/devolucao_use_cases.py`
  - `devolucao/src/infrastructure/database/config.py`
  - `devolucao/src/infrastructure/database/models.py`
  - `devolucao/src/infrastructure/repositories/devolucao_repository_impl.py`
  - `devolucao/src/presentation/api/routes/devolucao_routes.py`
  - `docs/ENTIDADE-DEVOLUCAO.md`
- **Arquivos modificados**:
  - `app.py` — adicionadas importações de `devolucao_routes` e `init_db_devolucao`, inclusão da rota `/api/v1/devolucoes` e chamada `init_db_devolucao()` no lifespan
- **Impacto**: Sistema agora possui gerenciamento completo de devoluções de itens perdidos

### Corrigido

#### 28. `__post_init__` Fora da Classe em `devolucao.py`
- **Problema**: Método `__post_init__` estava fora do escopo da classe `Devolucao` por indentação incorreta, fazendo com que nunca fosse chamado
- **Solução**: Método movido para dentro da classe com indentação correta; validações também corrigidas de `if not self.id_x` para `if self.id_x <= 0`
- **Arquivos**:
  - `devolucao/src/domain/entities/devolucao.py`
- **Impacto**: Validações de domínio passam a funcionar corretamente na instanciação

#### 29. `data_devolucao` com Tipo Opcional Contradizendo Validação
- **Problema**: Campo `data_devolucao` era `Optional[datetime] = None`, mas o `__post_init__` rejeitava `None` gerando erro ao criar com o valor padrão
- **Solução**: Alterado para `datetime = field(default_factory=datetime.now)` — nunca é `None` e registra a data/hora atual automaticamente
- **Arquivos**:
  - `devolucao/src/domain/entities/devolucao.py`
  - `devolucao/src/application/schemas/devolucao_schema.py`
- **Impacto**: Criação de devoluções sem informar data funciona corretamente

#### 30. `DevolucaoCreate` e `DevolucaoUpdate` Não Herdando `DevolucaoBase`
- **Problema**: Ambos os schemas redeclaravam todos os campos em vez de herdar de `DevolucaoBase`, gerando duplicação
- **Solução**: `DevolucaoCreate` e `DevolucaoUpdate` passaram a herdar de `DevolucaoBase`
- **Arquivos**:
  - `devolucao/src/application/schemas/devolucao_schema.py`
- **Impacto**: Código sem duplicação; mudanças na base refletem automaticamente nos schemas derivados

#### 31. `DevolucaoResponse` sem `created_at` e `updated_at`
- **Problema**: Schema de resposta não incluía timestamps, diferindo do padrão das demais entidades
- **Solução**: Adicionados `created_at: datetime` e `updated_at: Optional[datetime] = None` ao `DevolucaoResponse`
- **Arquivos**:
  - `devolucao/src/application/schemas/devolucao_schema.py`
- **Impacto**: Respostas da API incluem timestamps, alinhado com `ItemResponse` e `LocalResponse`

#### 32. `DevolucaoModel` Importando `Base` do Módulo `item`
- **Problema**: `models.py` da devolução importava `Base` de `item.src.infrastructure.database.config`, fazendo o modelo se registrar no banco `achados_perdidos.db` enquanto `get_session()` consultava `devolucao.db`
- **Solução**: Corrigido o import para `devolucao.src.infrastructure.database.config`
- **Arquivos**:
  - `devolucao/src/infrastructure/database/models.py`
- **Impacto**: Tabela `devolucoes` criada e consultada no banco correto; eliminado erro 500 nas requisições

#### 33. Referências a Atributos Inexistentes nas Routes
- **Problema**: Routes referenciavam `devolucao_data.id_reclamante` e `devolucao_data.id_item`, mas o schema usa `reclamante_id` e `item_id`, causando `AttributeError` e erro 500
- **Solução**: Todas as ocorrências nos endpoints POST, PUT e PATCH corrigidas para os nomes corretos
- **Arquivos**:
  - `devolucao/src/presentation/api/routes/devolucao_routes.py`
- **Impacto**: Endpoints de criação e atualização de devolução funcionam corretamente

#### 34. `DeleteDevolucaoUseCase` sem Chamar `repository.delete()`
- **Problema**: O use case buscava a devolução, verificava existência, mas não chamava `repository.delete()`, nunca removendo o registro
- **Solução**: Adicionado `return await self.repository.delete(devolucao_id)`
- **Arquivos**:
  - `devolucao/src/application/use_cases/devolucao_use_cases.py`
- **Impacto**: Endpoint DELETE passa a remover os registros corretamente

#### 35. `get_all()` Incompleto no Repositório de Devolucao
- **Problema**: Método `get_all()` estava declarado mas sem implementação; métodos `update()`, `delete()`, `get_by_data()` e `count()` estavam completamente ausentes
- **Solução**: Todos os métodos implementados seguindo o padrão de `ItemRepositoryImpl`
- **Arquivos**:
  - `devolucao/src/infrastructure/repositories/devolucao_repository_impl.py`
- **Impacto**: Todas as operações CRUD e de consulta funcionam corretamente

---

### Adicionado (anterior)

#### 18. Entidade Local com Clean Architecture
- **Descrição**: Implementação completa da entidade Local seguindo padrões de Clean Architecture (Arquitetura Diplomata)
- **Componentes**:
  - **Domain Layer**:
    - Entidade `Local` com validações de domínio (tipo, descrição e bairro não podem ser vazios)
    - Método de domínio `atualizar_descricao()` com validação
    - Interface `LocalRepository` com métodos CRUD + `get_by_bairro()` + `count()`
  - **Application Layer**:
    - Schemas Pydantic: `LocalBase`, `LocalCreate`, `LocalUpdate`, `LocalResponse` (com `created_at`/`updated_at`), `LocalListResponse`
    - Use Cases: `CreateLocalUseCase`, `GetLocalByIdUseCase`, `GetAllLocalsUseCase`, `UpdateLocalUseCase`, `DeleteLocalUseCase`, `GetLocalsByBairroUseCase`
  - **Infrastructure Layer**:
    - `LocalRepositoryImpl` com implementação assíncrona usando SQLAlchemy
    - `LocalModel` com colunas `created_at` (server_default) e `updated_at` (onupdate)
    - Configuração de banco de dados independente (`local.db`)
    - `get_session()` com tipo de retorno `AsyncGenerator[AsyncSession, None]`
  - **Presentation Layer**:
    - Rotas REST completas: POST `/`, GET `/`, GET `/bairro/{bairro}`, GET `/{local_id}`, PUT `/{local_id}`, DELETE `/{local_id}`
- **Arquivos criados**:
  - `local/__init__.py`
  - `local/src/domain/entities/local.py`
  - `local/src/domain/repositories/local_repository.py`
  - `local/src/application/schemas/local_schema.py`
  - `local/src/application/use_cases/local_use_cases.py`
  - `local/src/infrastructure/database/config.py`
  - `local/src/infrastructure/database/models.py`
  - `local/src/infrastructure/repositories/local_repository_impl.py`
  - `local/src/presentation/api/routes/local_routes.py`
  - `docs/ENTIDADE-LOCAL.md`
- **Arquivos modificados**:
  - `app.py` — adicionadas importações de `local_routes` e `init_db_local`, inclusão da rota `/api/v1/local` e chamada `init_db_local()` no lifespan
- **Impacto**: Sistema agora possui gerenciamento completo de locais onde itens são encontrados

### Corrigido

#### 19. Indentação e Estrutura da Entidade Local
- **Problema**: Arquivo `local.py` da entidade possuía indentação incorreta no docstring, método `__post_init__` fora do escopo da classe e método `atualizar_descricao` aninhado incorretamente dentro de `__post_init__`
- **Solução**: Reestruturado o arquivo com indentação correta; `__post_init__` e `atualizar_descricao` movidos para dentro da classe
- **Arquivos**:
  - `local/src/domain/entities/local.py`
- **Impacto**: Entidade instanciável e validações de domínio funcionando corretamente

#### 20. Campos Sem Default na Entidade Local
- **Problema**: Campos `id`, `created_at` e `updated_at` não possuíam valor default, tornando impossível criar instâncias sem informá-los
- **Solução**: Alterados para `Optional[...] = None` permitindo criação com apenas `tipo`, `descricao` e `bairro`
- **Arquivos**:
  - `local/src/domain/entities/local.py`
- **Impacto**: Criação de locais via POST funciona corretamente sem fornecer `id` ou timestamps

#### 21. Import Incorreto em `local_repository.py`
- **Problema**: Interface usava `from src.domain.entities.local import Local` (caminho relativo inválido)
- **Solução**: Corrigido para `from local.src.domain.entities.local import Local`
- **Arquivos**:
  - `local/src/domain/repositories/local_repository.py`
- **Impacto**: Elimina `ModuleNotFoundError` na importação do repositório

#### 22. Nome Incorreto do Arquivo de Repositório
- **Problema**: Arquivo nomeado `local_repositories.py` (plural) enquanto todos os módulos importavam `local_repository` (singular)
- **Solução**: Arquivo renomeado para `local_repository.py`
- **Arquivos**:
  - `local/src/domain/repositories/local_repository.py` (renomeado de `local_repositories.py`)
- **Impacto**: Importações funcionam sem `ModuleNotFoundError`

#### 23. Colunas `created_at` e `updated_at` Ausentes no Model ORM
- **Problema**: `LocalModel` não possuía as colunas de timestamp, mas `LocalResponse` e a entidade esperavam esses campos
- **Solução**: Adicionadas colunas `created_at` (com `server_default=func.now()`) e `updated_at` (com `onupdate=func.now()`) ao `LocalModel`
- **Arquivos**:
  - `local/src/infrastructure/database/models.py`
- **Impacto**: Respostas da API incluem timestamps corretos; sem mais erros de atributo ao serializar

#### 24. Tipo de Retorno Incorreto em `get_session()`
- **Problema**: Função geradora assíncrona `get_session()` declarava retorno `-> AsyncSession` mas retorna um generator
- **Solução**: Alterado para `-> AsyncGenerator[AsyncSession, None]` com import de `AsyncGenerator` do `typing`
- **Arquivos**:
  - `local/src/infrastructure/database/config.py`
- **Impacto**: Elimina erro de tipo e compatibilidade com Dependency Injection do FastAPI

#### 25. Vírgula Faltando e Campo Errado em `_model_to_entity()`
- **Problema**: Faltava vírgula após `tipo=model.tipo` e o campo `descricao` era mapeado erroneamente como `model.tipo`
- **Solução**: Adicionada vírgula e corrigido para `descricao=model.descricao`; adicionados `created_at` e `updated_at` ao mapeamento
- **Arquivos**:
  - `local/src/infrastructure/repositories/local_repository_impl.py`
- **Impacto**: Entidades retornadas têm todos os campos corretos

#### 26. Indentação Incorreta e Variável Errada em `get_by_bairro()`
- **Problema**: Método `get_by_bairro` tinha 5 espaços de indentação (fora do escopo da classe) e usava variável `categoria` inexistente no filtro WHERE
- **Solução**: Corrigida indentação para 4 espaços e variável trocada para `bairro`
- **Arquivos**:
  - `local/src/infrastructure/repositories/local_repository_impl.py`
- **Impacto**: Método pertence corretamente à classe e busca por bairro retorna resultados corretos

#### 27. Método `count()` Faltando na Implementação
- **Problema**: Interface `LocalRepository` declarava `count()` como `@abstractmethod` mas `LocalRepositoryImpl` não o implementava, causando erro ao instanciar a classe
- **Solução**: Implementado `count()` usando `select(func.count()).select_from(LocalModel)`
- **Arquivos**:
  - `local/src/infrastructure/repositories/local_repository_impl.py`
- **Impacto**: Classe pode ser instanciada; endpoint `GET /` retorna o `total` correto na listagem

#### 28. Import `datetime` Faltando no Schema
- **Problema**: `LocalResponse` usava `datetime` sem importá-lo, causando `NameError`
- **Solução**: Adicionado `from datetime import datetime` e `from typing import List`
- **Arquivos**:
  - `local/src/application/schemas/local_schema.py`
- **Impacto**: Schema importa e valida corretamente

#### 29. `LocalResponse` Incompleto e `LocalListResponse` Ausente
- **Problema**: `LocalResponse` não incluía os campos `tipo`, `descricao` e `bairro`; classe `LocalListResponse` não existia mas era usada nas rotas
- **Solução**: Adicionados os campos faltantes em `LocalResponse`; criada classe `LocalListResponse`
- **Arquivos**:
  - `local/src/application/schemas/local_schema.py`
- **Impacto**: Respostas da API retornam todos os dados do local; endpoint `GET /` funciona sem `NameError`

#### 30. Nomes de Classes Incorretos nos Use Cases
- **Problema**: `getLocalByIdUseCase` (minúsculo) e `GetItemsByBairroUseCase` (nome errado) não correspondiam ao que as rotas importavam
- **Solução**: Renomeados para `GetLocalByIdUseCase` e `GetLocalsByBairroUseCase`
- **Arquivos**:
  - `local/src/application/use_cases/local_use_cases.py`
- **Impacto**: Importações nas rotas funcionam sem `ImportError`

#### 31. Múltiplos Erros em `local_routes.py`
- **Problema**: Arquivo continha diversos erros de importação e lógica:
  - Import `from local.src.domain.entities.item import Local` (módulo inexistente)
  - Import `from local.src.infrastructure.repositories.item_repository_impl` (arquivo inexistente)  
  - `LocalListResponse` não importado
  - Router com `prefix="/locals"` duplicando o prefixo do `app.include_router()`
  - Todas as rotas com paths `/locals/xxx` em vez de `/`, `/{local_id}`, etc.
  - Path param `{local}` no PUT em vez de `{local_id}`
  - `return update_local` (nome da função) em vez de `return updated_local` (variável)
  - Indentação incorreta no docstring de `get_all_locals`
- **Solução**: Corrigidos todos os imports, removido prefixo duplicado, padronizados os paths, corrigido path param e variável de retorno
- **Arquivos**:
  - `local/src/presentation/api/routes/local_routes.py`
- **Impacto**: Todas as rotas da entidade Local respondem nos endpoints corretos sem erros de importação ou execução

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
