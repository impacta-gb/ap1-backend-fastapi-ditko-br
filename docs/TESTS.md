# Guia de Testes do Projeto

Documentação prática para implementação e execução de testes no projeto.

## Estrutura de Testes

```
item/tests/
├── unit/                 # Entidade, use cases, schemas, exceptions, performance
└── integration/          # Repository, end-to-end, API e consumers de eventos

local/tests/
├── unit/
└── integration/

responsavel/tests/
├── unit/
└── integration/

reclamante/tests/
├── unit/
└── integration/

devolucao/tests/
├── unit/
└── integration/

tests/
└── integration/          # Testes transversais de Kafka entre módulos
```

## Comandos Principais

### Executar Todos os Testes
```bash
pytest -v
```

### Por Categoria
```bash
pytest item/tests/unit/ -v              # Apenas unitários
pytest item/tests/integration/ -v       # Integração do módulo item
pytest item/tests/integration/test_item_api.py -v  # Apenas API do item
pytest tests/integration/ -v            # Integração transversal (Kafka)
```

### Com Cobertura
```bash
pytest item/tests/ --cov=item/src --cov-report=html
```

### Teste Específico
```bash
pytest item/tests/unit/test_item_entity.py::test_criar_item_valido -v
```

---

## Entidade: Item

### Testes Unitários

**Arquivo:** `item/tests/unit/test_item_entity.py`

| Teste | Descrição |
|-------|-----------|
| `test_criar_item_valido` | Cria item com dados válidos |
| `test_criar_item_sem_nome` | Valida obrigatoriedade do nome |
| `test_criar_item_sem_categoria` | Valida obrigatoriedade da categoria |
| `test_criar_item_sem_descricao` | Valida obrigatoriedade da descrição |
| `test_criar_item_com_status_invalido` | Valida status permitidos |
| `test_status_normalizado` | Testa normalização de status (lowercase, sem acentos) |
| `test_marcar_como_devolvido` | Testa método de negócio |
| `test_atualizar_descricao` | Testa método de atualização |

**Executar:**
```bash
pytest item/tests/unit/test_item_entity.py -v
```

---

**Arquivo:** `item/tests/unit/test_item_use_cases.py`

#### CreateItemUseCase
| Teste | Descrição |
|-------|-----------|
| `test_criar_item_com_sucesso` | Criação válida |
| `test_criar_item_com_data_futura` | Bloqueia data futura |
| `test_criar_item_com_local_id_invalido` | Valida local_id > 0 |
| `test_criar_item_com_responsavel_id_invalido` | Valida responsavel_id > 0 |
| `test_criar_item_sempre_define_status_disponivel` | Força status inicial |

#### GetItemByIdUseCase
| Teste | Descrição |
|-------|-----------|
| `test_buscar_item_existente` | Retorna item encontrado |
| `test_buscar_item_inexistente` | Retorna None |
| `test_buscar_item_com_id_invalido` | Valida ID > 0 |

#### GetAllItemsUseCase
| Teste | Descrição |
|-------|-----------|
| `test_listar_todos_itens` | Lista com paginação padrão |
| `test_listar_itens_com_paginacao_customizada` | Testa skip/limit customizado |
| `test_listar_itens_com_skip_negativo` | Bloqueia skip < 0 |
| `test_listar_itens_com_limit_zero` | Bloqueia limit ≤ 0 |
| `test_listar_itens_com_limit_maior_que_1000` | Bloqueia limit > 1000 |

#### UpdateItemUseCase
| Teste | Descrição |
|-------|-----------|
| `test_atualizar_item_com_sucesso` | Atualização válida |
| `test_atualizar_item_inexistente` | Retorna None se não encontrar |
| `test_atualizar_item_nao_pode_marcar_como_devolvido` | Bloqueia mudança direta para "devolvido" |
| `test_atualizar_item_com_data_futura` | Bloqueia data futura |

#### DeleteItemUseCase
| Teste | Descrição |
|-------|-----------|
| `test_deletar_item_disponivel` | Exclui item disponível |
| `test_deletar_item_inexistente` | Retorna False |
| `test_deletar_item_devolvido_nao_permitido` | Bloqueia exclusão de devolvidos |

#### GetItemsByCategoriaUseCase
| Teste | Descrição |
|-------|-----------|
| `test_buscar_por_categoria` | Filtra por categoria |
| `test_buscar_por_categoria_vazia` | Valida categoria não vazia |

#### GetItemsByStatusUseCase
| Teste | Descrição |
|-------|-----------|
| `test_buscar_por_status_disponivel` | Filtra por status |
| `test_buscar_por_status_invalido` | Valida status permitidos |
| `test_buscar_por_status_com_acento_normalizado` | Normaliza acentos |

**Executar:**
```bash
pytest item/tests/unit/test_item_use_cases.py -v
```

---

**Arquivo:** `item/tests/unit/test_item_exceptions.py`

| Escopo | Descrição |
|-------|-----------|
| Exceções de domínio | Valida erros customizados do módulo Item |

**Executar:**
```bash
pytest item/tests/unit/test_item_exceptions.py -v
```

---

**Arquivo:** `item/tests/unit/test_item_performance.py`

| Escopo | Descrição |
|-------|-----------|
| Performance | Mede tempo de operações do módulo Item |

**Executar:**
```bash
pytest item/tests/unit/test_item_performance.py -v
```

---

### Testes de Integração

**Arquivo:** `item/tests/integration/test_item_repository.py`

| Teste | Descrição |
|-------|-----------|
| `test_criar_item` | CRUD: Create |
| `test_buscar_item_por_id` | CRUD: Read |
| `test_buscar_item_por_id_inexistente` | Read retorna None |
| `test_listar_todos_itens` | Lista todos |
| `test_listar_itens_com_paginacao` | Paginação funcional |
| `test_atualizar_item` | CRUD: Update |
| `test_atualizar_item_inexistente` | Update retorna None |
| `test_deletar_item` | CRUD: Delete |
| `test_deletar_item_inexistente` | Delete retorna False |
| `test_buscar_por_categoria` | Filtro categoria |
| `test_buscar_por_status` | Filtro status |
| `test_contar_total_de_itens` | Método count() |
| `test_conversao_model_to_entity` | Conversão ORM ↔ Domain |

**Executar:**
```bash
pytest item/tests/integration/test_item_repository.py -v
```

---

**Arquivo:** `item/tests/integration/test_item_end_to_end.py`

| Teste | Descrição |
|-------|-----------|
| `test_fluxo_completo_criar_buscar_atualizar_deletar` | CRUD completo |
| `test_fluxo_nao_pode_deletar_item_devolvido` | Regra de negócio |
| `test_fluxo_listar_com_paginacao` | Paginação end-to-end |
| `test_fluxo_buscar_por_categoria` | Filtro categoria |
| `test_fluxo_buscar_por_status` | Filtro status |
| `test_fluxo_validacao_data_futura_na_criacao` | Validação data |
| `test_fluxo_validacao_ids_invalidos` | Validação IDs |
| `test_fluxo_metodo_entidade_marcar_como_devolvido` | Método domain |
| `test_fluxo_metodo_entidade_atualizar_descricao` | Método domain |
| `test_fluxo_contar_total_de_itens` | Count end-to-end |

**Executar:**
```bash
pytest item/tests/integration/test_item_end_to_end.py -v
```

---

**Arquivo:** `item/tests/integration/test_devolucao_event_consumer.py`

| Escopo | Descrição |
|-------|-----------|
| Consumer de devolução | Valida processamento de eventos de devolução no módulo Item |

**Executar:**
```bash
pytest item/tests/integration/test_devolucao_event_consumer.py -v
```

---

### Testes de API

**Arquivo:** `item/tests/integration/test_item_api.py`

#### POST /api/v1/items
| Teste | Status | Descrição |
|-------|--------|-----------|
| `test_criar_item_com_sucesso` | 201 | Cria item válido |
| `test_criar_item_com_dados_invalidos` | 422 | Valida campos obrigatórios |
| `test_criar_item_com_nome_vazio` | 400 | Valida nome não vazio |
| `test_criar_item_com_data_futura` | 400 | Bloqueia data futura |
| `test_criar_item_com_local_id_invalido` | 400 | Valida local_id |

#### GET /api/v1/items/{id}
| Teste | Status | Descrição |
|-------|--------|-----------|
| `test_buscar_item_existente` | 200 | Retorna item |
| `test_buscar_item_inexistente` | 404 | Item não encontrado |
| `test_buscar_item_com_id_invalido` | 400 | ID inválido |
| `test_buscar_item_com_id_string` | 422 | Tipo inválido |

#### GET /api/v1/items
| Teste | Status | Descrição |
|-------|--------|-----------|
| `test_listar_todos_itens` | 200 | Lista itens |
| `test_listar_itens_com_paginacao` | 200 | Paginação |
| `test_listar_itens_com_skip_negativo` | 400 | Valida skip |
| `test_listar_itens_com_limit_invalido` | 400 | Valida limit |

#### PUT /api/v1/items/{id}
| Teste | Status | Descrição |
|-------|--------|-----------|
| `test_atualizar_item_com_sucesso` | 200 | Atualiza item |
| `test_atualizar_item_inexistente` | 404 | Item não encontrado |
| `test_atualizar_item_nao_pode_marcar_como_devolvido` | 400 | Regra de negócio |

#### DELETE /api/v1/items/{id}
| Teste | Status | Descrição |
|-------|--------|-----------|
| `test_deletar_item_com_sucesso` | 204/200 | Exclui item |
| `test_deletar_item_inexistente` | 404 | Item não encontrado |
| `test_deletar_item_devolvido_nao_permitido` | 400 | Regra de negócio |

#### Filtros
| Teste | Endpoint | Descrição |
|-------|----------|-----------|
| `test_buscar_por_categoria` | GET /api/v1/items/categoria/{cat} | Filtro categoria |
| `test_buscar_por_status` | GET /api/v1/items/status/{status} | Filtro status |

**Executar:**
```bash
pytest item/tests/integration/test_item_api.py -v
```

---

**Arquivo:** `item/tests/unit/test_item_schema.py`

| Teste | Schema | Descrição |
|-------|--------|-----------|
| `test_criar_schema_com_dados_validos` | ItemCreate | Validação sucesso |
| `test_schema_com_nome_vazio_falha` | ItemCreate | Valida nome |
| `test_schema_com_categoria_vazia_falha` | ItemCreate | Valida categoria |
| `test_schema_com_campo_faltando_falha` | ItemCreate | Campos obrigatórios |
| `test_update_schema_com_dados_validos` | ItemUpdate | Update válido |
| `test_response_schema_com_todos_campos` | ItemResponse | Serialização |
| `test_list_response_schema_com_itens` | ItemListResponse | Lista paginada |

**Executar:**
```bash
pytest item/tests/unit/test_item_schema.py -v
```

---

## Entidade: Responsável

### Testes Unitários

**Arquivo:** `responsavel/tests/unit/test_responsavel_entity.py`

| Teste | Descrição |
|-------|-----------|
| `test_criar_responsavel_valido` | Cria responsável com dados válidos |
| `test_criar_responsavel_ativo_false` | Criação com ativo=False |
| `test_criar_responsavel_com_id` | Criação simulando objeto do banco |
| `test_criar_responsavel_sem_nome` | Valida obrigatoriedade do nome |
| `test_criar_responsavel_com_nome_apenas_espacos` | Valida nome com apenas espaços |
| `test_criar_responsavel_sem_cargo` | Valida obrigatoriedade do cargo |
| `test_criar_responsavel_com_cargo_apenas_espacos` | Valida cargo com apenas espaços |
| `test_criar_responsavel_sem_telefone` | Valida obrigatoriedade do telefone |
| `test_criar_responsavel_com_telefone_apenas_espacos` | Valida telefone com apenas espaços |
| `test_criar_responsavel_com_ativo_nao_booleano` | Valida que ativo deve ser booleano |
| `test_desativar_responsavel` | Testa método de negócio desativar |
| `test_desativar_responsavel_ja_inativo` | Desativar responsável já inativo |
| `test_responsavel_representacao` | Testa instanciação com todos os campos |

**Executar:**
```bash
pytest responsavel/tests/unit/test_responsavel_entity.py -v
```

---

**Arquivo:** `responsavel/tests/unit/test_responsavel_use_cases.py`

#### CreateResponsavelUseCase
| Teste | Descrição |
|-------|-----------|
| `test_criar_responsavel_com_sucesso` | Criação válida |
| `test_criar_responsavel_sempre_define_ativo_como_true` | Força ativo=True na criação |
| `test_criar_responsavel_com_telefone_invalido` | Bloqueia telefone muito curto |
| `test_criar_responsavel_com_telefone_letras` | Bloqueia telefone com letras |
| `test_criar_responsavel_com_telefone_formatado` | Aceita telefone com formatação válida |

#### GetResponsavelByIdUseCase
| Teste | Descrição |
|-------|-----------|
| `test_buscar_responsavel_existente` | Retorna responsável encontrado |
| `test_buscar_responsavel_inexistente` | Retorna None |
| `test_buscar_responsavel_com_id_invalido` | Valida ID > 0 |
| `test_buscar_responsavel_com_id_negativo` | Valida ID negativo |

#### GetAllResponsaveisUseCase
| Teste | Descrição |
|-------|-----------|
| `test_listar_todos_responsaveis` | Lista com paginação padrão |
| `test_listar_responsaveis_com_paginacao_customizada` | Testa skip/limit customizado |
| `test_listar_responsaveis_com_skip_negativo` | Bloqueia skip < 0 |
| `test_listar_responsaveis_com_limit_zero` | Bloqueia limit ≤ 0 |
| `test_listar_responsaveis_com_limit_maior_que_1000` | Bloqueia limit > 1000 |

#### UpdateResponsavelUseCase
| Teste | Descrição |
|-------|-----------|
| `test_atualizar_responsavel_com_sucesso` | Atualização válida |
| `test_atualizar_responsavel_inexistente` | Retorna None se não encontrar |
| `test_atualizar_responsavel_com_telefone_invalido` | Bloqueia telefone inválido |
| `test_atualizar_responsavel_mesmo_telefone_nao_valida` | Mesmo telefone não revalida |

#### DeleteResponsavelUseCase
| Teste | Descrição |
|-------|-----------|
| `test_deletar_responsavel_existente` | Exclui responsável existente |
| `test_deletar_responsavel_inexistente` | Retorna False |
| `test_deletar_responsavel_com_id_invalido` | Valida ID > 0 |

#### DesativarResponsavelUseCase
| Teste | Descrição |
|-------|-----------|
| `test_desativar_responsavel_ativo` | Desativa responsável ativo |
| `test_desativar_responsavel_ja_inativo` | Retorna sem erro se já inativo |
| `test_desativar_responsavel_inexistente` | Retorna None |
| `test_desativar_responsavel_com_id_invalido` | Valida ID > 0 |

#### ReativarResponsavelUseCase
| Teste | Descrição |
|-------|-----------|
| `test_reativar_responsavel_inativo` | Reativa responsável inativo |
| `test_reativar_responsavel_ja_ativo` | Retorna sem erro se já ativo |
| `test_reativar_responsavel_inexistente` | Retorna None |
| `test_reativar_responsavel_com_id_invalido` | Valida ID > 0 |

#### GetResponsaveisByAtivoUseCase
| Teste | Descrição |
|-------|-----------|
| `test_buscar_responsaveis_ativos` | Filtra responsáveis ativos |
| `test_buscar_responsaveis_inativos` | Filtra responsáveis inativos |
| `test_buscar_responsaveis_com_ativo_nao_booleano` | Valida parâmetro booleano |

**Executar:**
```bash
pytest responsavel/tests/unit/test_responsavel_use_cases.py -v
```

---

**Arquivo:** `responsavel/tests/unit/test_responsavel_schema.py`

| Teste | Schema | Descrição |
|-------|--------|-----------|
| `test_criar_schema_com_dados_validos` | ResponsavelCreate | Validação sucesso |
| `test_schema_com_nome_vazio_falha` | ResponsavelCreate | Valida nome |
| `test_schema_com_cargo_vazio_falha` | ResponsavelCreate | Valida cargo |
| `test_schema_com_telefone_vazio_falha` | ResponsavelCreate | Valida telefone |
| `test_schema_com_campo_faltando_falha` | ResponsavelCreate | Campos obrigatórios |
| `test_schema_com_telefone_invalido_falha` | ResponsavelCreate | Formato inválido |
| `test_schema_com_telefone_com_letras_falha` | ResponsavelCreate | Telefone com letras |
| `test_schema_sem_campo_ativo` | ResponsavelCreate | Ativo ausente do schema |
| `test_schema_serializa_para_dict` | ResponsavelCreate | Serialização dict |
| `test_schema_serializa_para_json` | ResponsavelCreate | Serialização JSON |
| `test_schema_com_nome_longo_demais_falha` | ResponsavelCreate | Nome muito longo |
| `test_update_schema_com_dados_validos` | ResponsavelUpdate | Update válido |
| `test_update_schema_sem_campo_ativo` | ResponsavelUpdate | Ativo ausente no update |
| `test_update_schema_com_telefone_invalido_falha` | ResponsavelUpdate | Telefone inválido |
| `test_patch_schema_com_apenas_nome` | ResponsavelPatch | Patch parcial nome |
| `test_patch_schema_com_apenas_cargo` | ResponsavelPatch | Patch parcial cargo |
| `test_patch_schema_com_todos_campos` | ResponsavelPatch | Patch com todos campos |
| `test_patch_schema_vazio` | ResponsavelPatch | Patch sem campos |
| `test_patch_schema_com_telefone_invalido_falha` | ResponsavelPatch | Telefone inválido |
| `test_response_schema_com_todos_campos` | ResponsavelResponse | Serialização |
| `test_response_schema_sem_id_falha` | ResponsavelResponse | ID obrigatório |
| `test_response_schema_serializa_para_json` | ResponsavelResponse | JSON serialização |
| `test_list_response_schema_vazio` | ResponsavelListResponse | Lista vazia |
| `test_list_response_schema_com_responsaveis` | ResponsavelListResponse | Lista com dados |
| `test_list_response_schema_paginacao` | ResponsavelListResponse | Paginação |
| `test_status_update_com_ativo_true` | ResponsavelStatusUpdate | ativo=True |
| `test_status_update_com_ativo_false` | ResponsavelStatusUpdate | ativo=False |
| `test_status_update_sem_ativo_falha` | ResponsavelStatusUpdate | Ativo obrigatório |

**Executar:**
```bash
pytest responsavel/tests/unit/test_responsavel_schema.py -v
```

---

### Testes de Integração

**Arquivo:** `responsavel/tests/integration/test_responsavel_repository.py`

| Teste | Descrição |
|-------|-----------|
| `test_criar_responsavel` | CRUD: Create |
| `test_buscar_responsavel_por_id` | CRUD: Read |
| `test_buscar_responsavel_por_id_inexistente` | Read retorna None |
| `test_listar_todos_responsaveis` | Lista todos |
| `test_listar_responsaveis_com_paginacao` | Paginação funcional |
| `test_atualizar_responsavel` | CRUD: Update |
| `test_atualizar_responsavel_inexistente` | Update retorna None |
| `test_deletar_responsavel` | CRUD: Delete |
| `test_deletar_responsavel_inexistente` | Delete retorna False |
| `test_buscar_por_ativo_true` | Filtro ativo/inativo |
| `test_contar_total_de_responsaveis` | Método count() |
| `test_conversao_model_to_entity` | Conversão ORM ↔ Domain |
| `test_desativar_responsavel_via_update` | Desativar via update |

**Executar:**
```bash
pytest responsavel/tests/integration/test_responsavel_repository.py -v
```

---

**Arquivo:** `responsavel/tests/integration/test_responsavel_end_to_end.py`

| Teste | Descrição |
|-------|-----------|
| `test_fluxo_completo_criar_buscar_atualizar_deletar` | CRUD completo |
| `test_fluxo_desativar_e_reativar_responsavel` | Fluxo desativar/reativar |
| `test_fluxo_listar_com_paginacao` | Paginação end-to-end |
| `test_fluxo_buscar_por_status_ativo` | Filtro ativo/inativo |
| `test_fluxo_validacao_telefone_invalido_na_criacao` | Validação telefone |
| `test_fluxo_desativar_ja_inativo_sem_erro` | Idempotência desativar |
| `test_fluxo_reativar_ja_ativo_sem_erro` | Idempotência reativar |
| `test_fluxo_contar_total_de_responsaveis` | Count end-to-end |
| `test_fluxo_metodo_entidade_desativar_responsavel` | Método domain |
| `test_fluxo_validacao_id_invalido_nas_buscas` | Validação IDs |

**Executar:**
```bash
pytest responsavel/tests/integration/test_responsavel_end_to_end.py -v
```

---

**Arquivo:** `responsavel/tests/integration/test_item_event_consumer.py`

| Escopo | Descrição |
|-------|-----------|
| Consumer de item | Valida processamento de eventos de item no módulo Responsável |

**Executar:**
```bash
pytest responsavel/tests/integration/test_item_event_consumer.py -v
```

---

### Testes de API

**Arquivo:** `responsavel/tests/integration/test_responsavel_api.py`

#### POST /api/v1/responsaveis
| Teste | Status | Descrição |
|-------|--------|-----------|
| `test_criar_responsavel_com_sucesso` | 201 | Cria responsável válido |
| `test_criar_responsavel_com_dados_invalidos` | 422 | Valida campos obrigatórios |
| `test_criar_responsavel_com_nome_vazio` | 400/422 | Valida nome não vazio |
| `test_criar_responsavel_com_telefone_invalido` | 400/422 | Valida telefone |
| `test_criar_responsavel_ativo_sempre_true` | 201 | Sempre inicia como ativo |

#### GET /api/v1/responsaveis/{id}
| Teste | Status | Descrição |
|-------|--------|-----------|
| `test_buscar_responsavel_existente` | 200 | Retorna responsável |
| `test_buscar_responsavel_inexistente` | 404 | Não encontrado |
| `test_buscar_responsavel_com_id_string` | 422 | Tipo inválido |

#### GET /api/v1/responsaveis
| Teste | Status | Descrição |
|-------|--------|-----------|
| `test_listar_todos_responsaveis` | 200 | Lista responsáveis |
| `test_listar_responsaveis_com_paginacao` | 200 | Paginação |
| `test_listar_responsaveis_com_skip_negativo` | 400/500 | Valida skip |
| `test_listar_responsaveis_com_limit_invalido` | 400/500 | Valida limit |

#### PUT /api/v1/responsaveis/{id}
| Teste | Status | Descrição |
|-------|--------|-----------|
| `test_atualizar_responsavel_com_sucesso` | 200 | Atualiza responsável |
| `test_atualizar_responsavel_inexistente` | 404 | Não encontrado |
| `test_atualizar_responsavel_com_telefone_invalido` | 400/422 | Telefone inválido |

#### DELETE /api/v1/responsaveis/{id}
| Teste | Status | Descrição |
|-------|--------|-----------|
| `test_deletar_responsavel_com_sucesso` | 204 | Exclui responsável |
| `test_deletar_responsavel_inexistente` | 404 | Não encontrado |

#### Status / Ativo
| Teste | Endpoint | Descrição |
|-------|----------|-----------|
| `test_buscar_responsaveis_ativos` | GET /api/v1/responsaveis/ativo/true | Filtro ativos |
| `test_buscar_responsaveis_inativos` | GET /api/v1/responsaveis/ativo/false | Filtro inativos |
| `test_alterar_status_responsavel` | PATCH /api/v1/responsaveis/{id}/status | Altera status |
| `test_alterar_status_responsavel_inexistente` | PATCH /api/v1/responsaveis/{id}/status | Não encontrado |

**Executar:**
```bash
pytest responsavel/tests/integration/test_responsavel_api.py -v
```

---

## Entidade: Local

### Testes Unitários

**Arquivo:** `local/tests/unit/test_local_entity.py`

| Teste | Descrição |
|-------|-----------|
| `test_criar_local_valido` | Cria local com dados válidos |
| `test_criar_local_com_id` | Criação simulando objeto do banco |
| `test_criar_local_sem_tipo` | Valida obrigatoriedade do tipo |
| `test_criar_local_com_tipo_apenas_espacos` | Valida tipo com apenas espaços |
| `test_criar_local_sem_descricao` | Valida obrigatoriedade da descrição |
| `test_criar_local_com_descricao_apenas_espacos` | Valida descrição com apenas espaços |
| `test_criar_local_sem_bairro` | Valida obrigatoriedade do bairro |
| `test_criar_local_com_bairro_apenas_espacos` | Valida bairro com apenas espaços |
| `test_atualizar_descricao_com_sucesso` | Testa método de atualização de descrição |
| `test_atualizar_descricao_com_valor_vazio_falha` | Valida que descrição vazia lança erro |
| `test_atualizar_descricao_com_apenas_espacos_falha` | Valida que espaços em branco lançam erro |
| `test_local_representacao_completa` | Testa instanciação com todos os campos |

**Executar:**
```bash
pytest local/tests/unit/test_local_entity.py -v
```

---

**Arquivo:** `local/tests/unit/test_local_use_cases.py`

#### CreateLocalUseCase
| Teste | Descrição |
|-------|-----------|
| `test_criar_local_com_sucesso` | Criação válida |
| `test_criar_local_chama_repositorio` | Garante delegação ao repositório |

#### GetLocalByIdUseCase
| Teste | Descrição |
|-------|-----------|
| `test_buscar_local_existente` | Retorna local encontrado |
| `test_buscar_local_inexistente` | Retorna None |
| `test_buscar_local_com_id_invalido` | Valida ID > 0 |
| `test_buscar_local_com_id_negativo` | Valida ID negativo |

#### GetAllLocalsUseCase
| Teste | Descrição |
|-------|-----------|
| `test_listar_todos_locais` | Lista com paginação padrão |
| `test_listar_locais_com_paginacao_customizada` | Testa skip/limit customizado |
| `test_listar_locais_com_skip_negativo` | Bloqueia skip < 0 |
| `test_listar_locais_com_limit_zero` | Bloqueia limit ≤ 0 |
| `test_listar_locais_com_limit_maior_que_1000` | Bloqueia limit > 1000 |

#### UpdateLocalUseCase
| Teste | Descrição |
|-------|-----------|
| `test_atualizar_local_com_sucesso` | Atualização válida |
| `test_atualizar_local_inexistente` | Retorna None se não encontrar |

#### DeleteLocalUseCase
| Teste | Descrição |
|-------|-----------|
| `test_deletar_local_existente` | Exclui local existente |
| `test_deletar_local_inexistente` | Retorna False |

#### GetLocalsByBairroUseCase
| Teste | Descrição |
|-------|-----------|
| `test_buscar_por_bairro_com_sucesso` | Filtra por bairro |
| `test_buscar_por_bairro_vazio` | Valida bairro não vazio |
| `test_buscar_por_bairro_apenas_espacos` | Valida espaços em branco |
| `test_buscar_por_bairro_sem_resultados` | Retorna lista vazia sem resultados |

**Executar:**
```bash
pytest local/tests/unit/test_local_use_cases.py -v
```

---

**Arquivo:** `local/tests/unit/test_local_schema.py`

| Teste | Schema | Descrição |
|-------|--------|-----------|
| `test_criar_schema_com_dados_validos` | LocalCreate | Validação sucesso |
| `test_schema_com_tipo_vazio_falha` | LocalCreate | Valida tipo |
| `test_schema_com_descricao_vazia_falha` | LocalCreate | Valida descrição |
| `test_schema_com_bairro_vazio_falha` | LocalCreate | Valida bairro |
| `test_schema_com_campo_faltando_falha` | LocalCreate | Campos obrigatórios |
| `test_schema_serializa_para_dict` | LocalCreate | Serialização dict |
| `test_schema_serializa_para_json` | LocalCreate | Serialização JSON |
| `test_update_schema_com_dados_validos` | LocalUpdate | Update válido |
| `test_update_schema_com_campos_opcionais` | LocalUpdate | Campos opcionais |
| `test_update_schema_apenas_tipo` | LocalUpdate | Patch parcial tipo |
| `test_update_schema_apenas_bairro` | LocalUpdate | Patch parcial bairro |
| `test_update_schema_com_tipo_vazio_falha` | LocalUpdate | Tipo vazio inválido |
| `test_response_schema_com_todos_campos` | LocalResponse | Serialização |
| `test_response_schema_sem_id_falha` | LocalResponse | ID obrigatório |
| `test_response_schema_serializa_para_json` | LocalResponse | JSON serialização |
| `test_list_response_schema_vazio` | LocalListResponse | Lista vazia |
| `test_list_response_schema_com_locais` | LocalListResponse | Lista com dados |
| `test_list_response_schema_paginacao` | LocalListResponse | Paginação |

**Executar:**
```bash
pytest local/tests/unit/test_local_schema.py -v
```

---

### Testes de Integração

**Arquivo:** `local/tests/integration/test_local_repository.py`

| Teste | Descrição |
|-------|-----------|
| `test_criar_local` | CRUD: Create |
| `test_buscar_local_por_id` | CRUD: Read |
| `test_buscar_local_por_id_inexistente` | Read retorna None |
| `test_listar_todos_locais` | Lista todos |
| `test_listar_locais_com_paginacao` | Paginação funcional |
| `test_atualizar_local` | CRUD: Update |
| `test_atualizar_local_inexistente` | Update retorna None |
| `test_deletar_local` | CRUD: Delete |
| `test_deletar_local_inexistente` | Delete retorna False |
| `test_buscar_por_bairro` | Filtro bairro |
| `test_contar_total_de_locais` | Método count() |
| `test_conversao_model_to_entity` | Conversão ORM ↔ Domain |

**Executar:**
```bash
pytest local/tests/integration/test_local_repository.py -v
```

---

**Arquivo:** `local/tests/integration/test_local_end_to_end.py`

| Teste | Descrição |
|-------|-----------|
| `test_fluxo_completo_criar_buscar_atualizar_deletar` | CRUD completo |
| `test_fluxo_listar_com_paginacao` | Paginação end-to-end |
| `test_fluxo_buscar_por_bairro` | Filtro bairro |
| `test_fluxo_validacao_bairro_vazio_na_busca` | Validação bairro vazio |
| `test_fluxo_validacao_id_invalido_nas_buscas` | Validação IDs |
| `test_fluxo_skip_negativo_na_listagem` | Validação skip negativo |
| `test_fluxo_limit_invalido_na_listagem` | Validação limit inválido |
| `test_fluxo_metodo_entidade_atualizar_descricao` | Método domain |
| `test_fluxo_contar_total_de_locais` | Count end-to-end |
| `test_fluxo_buscar_local_inexistente_retorna_none` | Read inexistente |
| `test_fluxo_deletar_local_inexistente` | Delete inexistente |

**Executar:**
```bash
pytest local/tests/integration/test_local_end_to_end.py -v
```

---

**Arquivo:** `local/tests/integration/test_item_event_consumer.py`

| Escopo | Descrição |
|-------|-----------|
| Consumer de item | Valida processamento de eventos de item no módulo Local |

**Executar:**
```bash
pytest local/tests/integration/test_item_event_consumer.py -v
```

---

### Testes de API

**Arquivo:** `local/tests/integration/test_local_api.py`

#### POST /api/v1/local
| Teste | Status | Descrição |
|-------|--------|-----------|
| `test_criar_local_com_sucesso` | 201 | Cria local válido |
| `test_criar_local_com_dados_invalidos` | 422 | Valida campos obrigatórios |
| `test_criar_local_com_tipo_vazio` | 400/422 | Valida tipo não vazio |
| `test_criar_local_com_descricao_vazia` | 400/422 | Valida descrição não vazia |
| `test_criar_local_com_bairro_vazio` | 400/422 | Valida bairro não vazio |

#### GET /api/v1/local/{local_id}
| Teste | Status | Descrição |
|-------|--------|-----------|
| `test_buscar_local_existente` | 200 | Retorna local |
| `test_buscar_local_inexistente` | 404 | Local não encontrado |
| `test_buscar_local_com_id_string` | 422 | Tipo inválido |

#### GET /api/v1/local
| Teste | Status | Descrição |
|-------|--------|-----------|
| `test_listar_todos_locais` | 200 | Lista locais |
| `test_listar_locais_com_paginacao` | 200 | Paginação |
| `test_listar_locais_com_skip_negativo` | 400/500 | Valida skip |
| `test_listar_locais_com_limit_invalido` | 400/500 | Valida limit |

#### PUT /api/v1/local/{local_id}
| Teste | Status | Descrição |
|-------|--------|-----------|
| `test_atualizar_local_com_sucesso` | 200 | Atualiza local |
| `test_atualizar_local_inexistente` | 404 | Local não encontrado |

#### DELETE /api/v1/local/{local_id}
| Teste | Status | Descrição |
|-------|--------|-----------|
| `test_deletar_local_com_sucesso` | 204/200 | Exclui local |
| `test_deletar_local_inexistente` | 404 | Local não encontrado |

#### Filtros
| Teste | Endpoint | Descrição |
|-------|----------|-----------|
| `test_buscar_por_bairro` | GET /api/v1/local/bairro/{bairro} | Filtro bairro |
| `test_buscar_por_bairro_sem_resultados` | GET /api/v1/local/bairro/{bairro} | Lista vazia |

**Executar:**
```bash
pytest local/tests/integration/test_local_api.py -v
```

---

## Entidade: Devolução

### Testes Unitários

**Arquivo:** `devolucao/tests/unit/test_devolucao_entity.py`

| Teste | Descrição |
|-------|-----------|
| `test_criar_devolucao_valida` | Cria devolução com dados válidos |
| `test_criar_devolucao_com_id` | Criação simulando objeto do banco |
| `test_criar_devolucao_com_data_devolucao` | Verifica data_devolucao customizada |
| `test_criar_devolucao_com_datas_de_auditoria` | Verifica campos created_at/updated_at |
| `test_criar_devolucao_com_reclamante_id_negativo` | Valida reclamante_id negativo |
| `test_criar_devolucao_com_reclamante_id_zero` | Valida reclamante_id zero |
| `test_criar_devolucao_com_item_id_negativo` | Valida item_id negativo |
| `test_criar_devolucao_com_item_id_zero` | Valida item_id zero |
| `test_criar_devolucao_sem_observacao` | Valida obrigatoriedade da observação |
| `test_criar_devolucao_com_observacao_apenas_espacos` | Valida observação com apenas espaços |
| `test_atualizar_observacao_com_sucesso` | Testa método atualizar_observacao |
| `test_atualizar_observacao_com_valor_vazio_falha` | Valida que observação vazia lança erro |
| `test_atualizar_observacao_com_apenas_espacos_falha` | Valida que espaços em branco lançam erro |
| `test_devolucao_representacao_completa` | Testa instanciação com todos os campos |

**Executar:**
```bash
pytest devolucao/tests/unit/test_devolucao_entity.py -v
```

---

**Arquivo:** `devolucao/tests/unit/test_devolucao_use_cases.py`

#### CreateDevolucaoUseCase
| Teste | Descrição |
|-------|-----------|
| `test_criar_devolucao_com_sucesso` | Criação válida |
| `test_criar_devolucao_com_data_futura_falha` | Bloqueia data futura |
| `test_criar_devolucao_com_reclamante_id_invalido_falha` | Valida reclamante_id > 0 |
| `test_criar_devolucao_com_item_id_invalido_falha` | Valida item_id > 0 |

#### GetDevolucaoByIdUseCase
| Teste | Descrição |
|-------|-----------|
| `test_buscar_por_id_existente` | Retorna devolução encontrada |
| `test_buscar_por_id_inexistente` | Retorna None |
| `test_buscar_por_id_invalido_falha` | Valida ID > 0 |
| `test_buscar_por_id_negativo_falha` | Valida ID negativo |

#### GetAllDevolucoesUseCase
| Teste | Descrição |
|-------|-----------|
| `test_listar_com_paginacao_padrao` | Lista com paginação padrão |
| `test_listar_com_skip_negativo_falha` | Bloqueia skip < 0 |
| `test_listar_com_limit_zero_falha` | Bloqueia limit ≤ 0 |
| `test_listar_com_limit_acima_do_maximo_falha` | Bloqueia limit > 1000 |
| `test_listar_com_paginacao_customizada` | Testa skip/limit customizado |
| `test_listar_com_limit_maximo_permitido` | Testa limit = 1000 |

#### UpdateDevolucaoUseCase
| Teste | Descrição |
|-------|-----------|
| `test_atualizar_devolucao_existente` | Atualização válida |
| `test_atualizar_devolucao_inexistente_retorna_none` | Retorna None se não encontrar |
| `test_atualizar_com_data_futura_falha` | Bloqueia data futura |

#### DeleteDevolucaoUseCase
| Teste | Descrição |
|-------|-----------|
| `test_deletar_devolucao_existente` | Exclui devolução existente |
| `test_deletar_devolucao_inexistente_retorna_false` | Retorna False |
| `test_deletar_com_id_invalido_falha` | Valida ID > 0 |
| `test_deletar_com_id_negativo_falha` | Valida ID negativo |

#### GetDevolucoesByDataUseCase
| Teste | Descrição |
|-------|-----------|
| `test_buscar_por_data_com_sucesso` | Filtra por data |
| `test_buscar_por_data_nula_falha` | Valida data não nula |
| `test_buscar_por_data_sem_resultados` | Retorna lista vazia |

#### CountDevolucoesUseCase
| Teste | Descrição |
|-------|-----------|
| `test_contar_total_com_registros` | Retorna contagem correta |
| `test_contar_total_sem_registros` | Retorna zero |

**Executar:**
```bash
pytest devolucao/tests/unit/test_devolucao_use_cases.py -v
```

---

**Arquivo:** `devolucao/tests/unit/test_devolucao_schema.py`

| Teste | Schema | Descrição |
|-------|--------|-----------|
| `test_criar_schema_com_dados_validos` | DevolucaoCreate | Validação sucesso |
| `test_schema_com_reclamante_id_zero_falha` | DevolucaoCreate | Valida reclamante_id |
| `test_schema_com_reclamante_id_negativo_falha` | DevolucaoCreate | Valida negativo |
| `test_schema_com_item_id_zero_falha` | DevolucaoCreate | Valida item_id |
| `test_schema_com_item_id_negativo_falha` | DevolucaoCreate | Valida negativo |
| `test_schema_com_observacao_vazia_falha` | DevolucaoCreate | Valida observação |
| `test_schema_com_campo_faltando_falha` | DevolucaoCreate | Campos obrigatórios |
| `test_schema_data_devolucao_default` | DevolucaoCreate | Default data_devolucao |
| `test_schema_serializa_para_dict` | DevolucaoCreate | Serialização dict |
| `test_schema_serializa_para_json` | DevolucaoCreate | Serialização JSON |
| `test_update_schema_com_dados_validos` | DevolucaoUpdate | Update válido |
| `test_update_schema_com_reclamante_id_invalido_falha` | DevolucaoUpdate | Valida reclamante_id |
| `test_patch_schema_com_apenas_observacao` | DevolucaoPatch | Patch parcial |
| `test_patch_schema_com_apenas_reclamante_id` | DevolucaoPatch | Patch reclamante_id |
| `test_patch_schema_com_todos_campos` | DevolucaoPatch | Patch completo |
| `test_patch_schema_vazio` | DevolucaoPatch | Patch sem campos |
| `test_patch_schema_com_reclamante_id_invalido_falha` | DevolucaoPatch | Valida ID inválido |
| `test_response_schema_com_todos_campos` | DevolucaoResponse | Serialização |
| `test_response_schema_sem_id_falha` | DevolucaoResponse | ID obrigatório |
| `test_response_schema_serializa_para_json` | DevolucaoResponse | JSON serialização |
| `test_list_response_schema_vazio` | DevolucaoListResponse | Lista vazia |
| `test_list_response_schema_com_devolucoes` | DevolucaoListResponse | Lista com dados |
| `test_list_response_schema_paginacao` | DevolucaoListResponse | Paginação |

**Executar:**
```bash
pytest devolucao/tests/unit/test_devolucao_schema.py -v
```

---

### Testes de Integração

**Arquivo:** `devolucao/tests/integration/test_devolucao_repository.py`

| Teste | Descrição |
|-------|-----------|
| `test_criar_devolucao` | CRUD: Create |
| `test_buscar_devolucao_por_id` | CRUD: Read |
| `test_buscar_devolucao_por_id_inexistente` | Read retorna None |
| `test_listar_todas_devolucoes` | Lista todos |
| `test_listar_devolucoes_com_paginacao` | Paginação funcional |
| `test_atualizar_devolucao` | CRUD: Update |
| `test_atualizar_devolucao_inexistente` | Update retorna None |
| `test_deletar_devolucao` | CRUD: Delete |
| `test_deletar_devolucao_inexistente` | Delete retorna False |
| `test_buscar_por_data` | Filtro data |
| `test_contar_total_devolucoes` | Método count() |
| `test_conversao_model_to_entity` | Conversão ORM ↔ Domain |

**Executar:**
```bash
pytest devolucao/tests/integration/test_devolucao_repository.py -v
```

---

**Arquivo:** `devolucao/tests/integration/test_devolucao_end_to_end.py`

| Teste | Descrição |
|-------|-----------|
| `test_fluxo_completo_criar_buscar_atualizar_deletar` | CRUD completo |
| `test_fluxo_listar_com_paginacao` | Paginação end-to-end |
| `test_fluxo_buscar_por_data` | Filtro data |
| `test_fluxo_validacao_data_nula_na_busca` | Validação data nula |
| `test_fluxo_validacao_id_invalido_nas_buscas` | Validação IDs |
| `test_fluxo_skip_negativo_na_listagem` | Validação skip negativo |
| `test_fluxo_limit_invalido_na_listagem` | Validação limit inválido |
| `test_fluxo_metodo_entidade_atualizar_observacao` | Método domain |
| `test_fluxo_contar_total_de_devolucoes` | Count end-to-end |
| `test_fluxo_buscar_devolucao_inexistente_retorna_none` | Read inexistente |
| `test_fluxo_deletar_devolucao_inexistente` | Delete inexistente |
| `test_fluxo_data_futura_ao_criar_falha` | Regra de negócio data futura |

**Executar:**
```bash
pytest devolucao/tests/integration/test_devolucao_end_to_end.py -v
```

---

**Arquivo:** `devolucao/tests/integration/test_item_event_consumer.py`

| Escopo | Descrição |
|-------|-----------|
| Consumer de item | Valida processamento de eventos de item no módulo Devolução |

**Executar:**
```bash
pytest devolucao/tests/integration/test_item_event_consumer.py -v
```

---

### Testes de API

**Arquivo:** `devolucao/tests/integration/test_devolucao_api.py`

#### POST /api/v1/devolucoes
| Teste | Status | Descrição |
|-------|--------|-----------|
| `test_criar_devolucao_com_sucesso` | 201 | Cria devolução válida |
| `test_criar_devolucao_com_dados_invalidos` | 422 | Valida campos obrigatórios |
| `test_criar_devolucao_com_reclamante_id_invalido` | 400/422 | Valida reclamante_id |
| `test_criar_devolucao_com_item_id_invalido` | 400/422 | Valida item_id |
| `test_criar_devolucao_com_data_futura` | 400/500 | Bloqueia data futura |

#### GET /api/v1/devolucoes/{id}
| Teste | Status | Descrição |
|-------|--------|-----------|
| `test_buscar_devolucao_existente` | 200 | Retorna devolução |
| `test_buscar_devolucao_inexistente` | 404 | Não encontrada |
| `test_buscar_devolucao_com_id_string` | 422 | Tipo inválido |

#### GET /api/v1/devolucoes
| Teste | Status | Descrição |
|-------|--------|-----------|
| `test_listar_todas_devolucoes` | 200 | Lista devoluções |
| `test_listar_devolucoes_com_paginacao` | 200 | Paginação |
| `test_listar_devolucoes_com_skip_negativo` | 400/500 | Valida skip |
| `test_listar_devolucoes_com_limit_invalido` | 400/500 | Valida limit |

#### PUT /api/v1/devolucoes/{id}
| Teste | Status | Descrição |
|-------|--------|-----------|
| `test_atualizar_devolucao_com_sucesso` | 200 | Atualiza devolução |
| `test_atualizar_devolucao_inexistente` | 404 | Não encontrada |

#### PATCH /api/v1/devolucoes/{id}
| Teste | Status | Descrição |
|-------|--------|-----------|
| `test_patch_devolucao_com_sucesso` | 200 | Atualização parcial |
| `test_patch_devolucao_inexistente` | 404 | Não encontrada |

#### DELETE /api/v1/devolucoes/{id}
| Teste | Status | Descrição |
|-------|--------|-----------|
| `test_deletar_devolucao_com_sucesso` | 204/200 | Exclui devolução |
| `test_deletar_devolucao_inexistente` | 404 | Não encontrada |

#### GET /api/v1/devolucoes/data/{data}
| Teste | Status | Descrição |
|-------|--------|-----------|
| `test_buscar_por_data_com_resultados` | 200 | Filtra por data |
| `test_buscar_por_data_sem_resultados` | 200 | Lista vazia |

**Executar:**
```bash
pytest devolucao/tests/integration/test_devolucao_api.py -v
```

---

## Template para Nova Entidade

### 1. Criar Estrutura
```bash
mkdir -p entidade/tests/{unit,integration,api}
touch entidade/tests/conftest.py
```

### 2. Testes Unitários da Entidade
**Arquivo:** `entidade/tests/unit/test_entidade_entity.py`

```python
import pytest
from entidade.src.domain.entities.entidade import Entidade

class TestEntidadeEntity:
    def test_criar_entidade_valida(self):
        """Testa criação com dados válidos"""
        entidade = Entidade(campo1="valor1", campo2="valor2")
        assert entidade.campo1 == "valor1"
    
    def test_criar_entidade_sem_campo_obrigatorio(self):
        """Testa validação de campo obrigatório"""
        with pytest.raises(ValueError):
            Entidade(campo1="")
```

### 3. Testes Unitários dos Use Cases
**Arquivo:** `entidade/tests/unit/test_entidade_use_cases.py`

```python
import pytest
from unittest.mock import AsyncMock
from entidade.src.application.use_cases.entidade_use_cases import CreateEntidadeUseCase

class TestCreateEntidadeUseCase:
    @pytest.mark.asyncio
    async def test_criar_entidade_com_sucesso(self):
        """Testa criação via use case"""
        repository_mock = AsyncMock()
        use_case = CreateEntidadeUseCase(repository_mock)
        
        entidade = Entidade(...)
        repository_mock.create.return_value = entidade
        
        resultado = await use_case.execute(entidade)
        
        assert resultado is not None
        repository_mock.create.assert_called_once()
```

### 4. Testes de Integração
**Arquivo:** `entidade/tests/integration/test_entidade_repository.py`

```python
import pytest
from entidade.src.infrastructure.repositories.entidade_repository_impl import EntidadeRepositoryImpl

class TestEntidadeRepositoryImpl:
    @pytest.mark.asyncio
    async def test_criar_entidade(self, test_session):
        """Testa criação no banco de dados"""
        repository = EntidadeRepositoryImpl(test_session)
        
        entidade = Entidade(...)
        resultado = await repository.create(entidade)
        
        assert resultado.id is not None
```

### 5. Testes de API
**Arquivo:** `entidade/tests/integration/test_entidade_api.py`

```python
import pytest

class TestEntidadeAPI:
    def test_criar_entidade_via_api(self, client):
        """Testa POST /api/v1/entidades"""
        response = client.post("/api/v1/entidades", json={
            "campo1": "valor1",
            "campo2": "valor2"
        })
        
        assert response.status_code == 201
        assert response.json()["campo1"] == "valor1"
```

---

## Estatísticas do Projeto

### Item (Implementado)
- **Total:** 113 testes
- **Unitários:** 39 (Entidade: 14, Use Cases: 25)
- **Integração:** 33 (Repository: 13, E2E: 10, Exceptions: 10)
- **API:** 36 (Routes: 26, Schemas: 10)
- **Performance:** 5

### Responsável (Implementado)
- **Total:** 117 testes
- **Unitários:** 73 (Entidade: 13, Use Cases: 32, Schemas: 28)
- **Integração:** 44 (Repository: 13, E2E: 10, API: 21)

### Local (Implementado)
- **Total:** 90 testes
- **Unitários:** 49 (Entidade: 12, Use Cases: 19, Schemas: 18)
- **Integração:** 41 (Repository: 12, E2E: 11, API: 18)

### Devolução (Implementado)
- **Total:** 107 testes
- **Unitários:** 52 (Entidade: 15, Use Cases: 25, Schemas: 12)
- **Integração:** 55 (Repository: 13, E2E: 12, API: 20)

### Reclamante (Implementado)
- **Total:** 85 testes
- **Unitários:** 45 (Entidade: 10, Use Cases: 20, Schemas: 15)
- **Integração:** 40 (Repository: 12, E2E: 10, API: 18)

---

## Entidade: Reclamante

### Testes Unitários

**Arquivo:** `reclamante/tests/unit/test_reclamante_entity.py`

| Teste | Descrição |
|-------|-----------|
| `test_criar_reclamante_valido` | Cria reclamante com dados válidos |
| `test_criar_reclamante_com_id` | Criação simulando objeto do banco |
| `test_criar_reclamante_sem_nome` | Valida obrigatoriedade do nome |
| `test_criar_reclamante_sem_telefone` | Valida obrigatoriedade do telefone |
| `test_criar_reclamante_sem_documento` | Valida obrigatoriedade do documento |
| `test_criar_reclamante_com_documento_vazio` | Valida documento vazio |
| `test_criar_reclamante_com_telefone_invalido` | Valida formato do telefone |
| `test_atualizar_dados_pessoais` | Testa método de atualização de dados |
| `test_atualizar_dados_com_documento` | Valida atualização com documento |
| `test_reclamante_representacao` | Testa a representação em string da entidade |

**Executar:**
```bash
pytest reclamante/tests/unit/test_reclamante_entity.py -v
```

---

**Arquivo:** `reclamante/tests/unit/test_reclamante_use_cases.py`

#### CreateReclamanteUseCase
| Teste | Descrição |
|-------|-----------|
| `test_criar_reclamante_com_sucesso` | Criação válida |
| `test_criar_reclamante_com_documento_existente` | Cenário de documento já existente, quando aplicável |
| `test_criar_reclamante_com_telefone_invalido` | Valida formato do telefone |

#### GetReclamanteByIdUseCase
| Teste | Descrição |
|-------|-----------|
| `test_buscar_reclamante_existente` | Retorna reclamante encontrado |
| `test_buscar_reclamante_inexistente` | Retorna None |
| `test_buscar_reclamante_com_id_invalido` | Valida ID > 0 |

#### GetAllReclamantesUseCase
| Teste | Descrição |
|-------|-----------|
| `test_listar_todos_reclamantes` | Lista com paginação padrão |
| `test_listar_reclamantes_com_paginacao_customizada` | Testa skip/limit customizado |
| `test_listar_reclamantes_com_skip_negativo` | Bloqueia skip < 0 |
| `test_listar_reclamantes_com_limit_invalido` | Bloqueia limit ≤ 0 |

#### UpdateReclamanteUseCase
| Teste | Descrição |
|-------|-----------|
| `test_atualizar_reclamante_com_sucesso` | Atualização válida |
| `test_atualizar_reclamante_inexistente` | Retorna None se não encontrar |
| `test_atualizar_reclamante_com_payload_invalido` | Valida payload na atualização |

#### DeleteReclamanteUseCase
| Teste | Descrição |
|-------|-----------|
| `test_deletar_reclamante_existente` | Exclui reclamante |
| `test_deletar_reclamante_inexistente` | Retorna False |

#### GetReclamanteByIdUseCase e listagem
| Teste | Descrição |
|-------|-----------|
| `test_buscar_reclamante_existente` | Busca por ID |
| `test_buscar_reclamante_inexistente` | Retorna None |
| `test_listar_todos_reclamantes` | Lista com paginação |

**Executar:**
```bash
pytest reclamante/tests/unit/test_reclamante_use_cases.py -v
```

---

**Arquivo:** `reclamante/tests/unit/test_reclamante_schema.py`

| Teste | Schema | Descrição |
|-------|--------|-----------|
| `test_criar_schema_com_dados_validos` | ReclamanteCreate | Validação sucesso |
| `test_schema_sem_nome_falha` | ReclamanteCreate | Valida nome |
| `test_schema_sem_telefone_falha` | ReclamanteCreate | Valida telefone |
| `test_schema_sem_documento_falha` | ReclamanteCreate | Valida documento |
| `test_schema_com_documento_vazio` | ReclamanteCreate | Valida documento vazio |
| `test_update_schema_com_dados_validos` | ReclamanteUpdate | Update válido |
| `test_update_schema_com_payload_incompleto` | ReclamanteUpdate | Valida campos obrigatórios |
| `test_response_schema_com_todos_campos` | ReclamanteResponse | Serialização |
| `test_response_schema_sem_id_falha` | ReclamanteResponse | ID obrigatório |
| `test_list_response_schema_com_reclamantes` | ReclamanteListResponse | Lista com dados |
| `test_list_response_schema_paginacao` | ReclamanteListResponse | Paginação |

**Executar:**
```bash
pytest reclamante/tests/unit/test_reclamante_schema.py -v
```

---

### Testes de Integração

**Arquivo:** `reclamante/tests/integration/test_reclamante_repository.py`

| Teste | Descrição |
|-------|-----------|
| `test_criar_reclamante` | CRUD: Create |
| `test_buscar_reclamante_por_id` | CRUD: Read |
| `test_listar_todos_reclamantes` | Lista todos |
| `test_listar_reclamantes_com_paginacao` | Paginação funcional |
| `test_atualizar_reclamante` | CRUD: Update |
| `test_deletar_reclamante` | CRUD: Delete |
| `test_contar_total_de_reclamantes` | Método count() |
| `test_conversao_model_to_entity` | Conversão ORM ↔ Domain |
| `test_validacoes_de_documento` | Valida regras de documento |

**Executar:**
```bash
pytest reclamante/tests/integration/test_reclamante_repository.py -v
```

---

**Arquivo:** `reclamante/tests/integration/test_reclamante_end_to_end.py`

| Teste | Descrição |
|-------|-----------|
| `test_fluxo_completo_criar_buscar_atualizar_deletar` | CRUD completo |
| `test_fluxo_listar_com_paginacao` | Paginação end-to-end |
| `test_fluxo_buscar_por_id` | Busca por ID |
| `test_fluxo_validacao_documento_vazio_na_criacao` | Validação de documento |
| `test_fluxo_validacao_id_invalido_nas_buscas` | Validação de IDs |
| `test_fluxo_contar_total_de_reclamantes` | Count end-to-end |
| `test_fluxo_metodo_entidade_atualizar_dados` | Método de domínio |
| `test_fluxo_validacoes_de_documento` | Regras de documento |

**Executar:**
```bash
pytest reclamante/tests/integration/test_reclamante_end_to_end.py -v
```

---

**Arquivo:** `reclamante/tests/integration/test_item_event_consumer.py`

| Escopo | Descrição |
|-------|-----------|
| Consumer de item | Valida processamento de eventos de item no módulo Reclamante |

**Executar:**
```bash
pytest reclamante/tests/integration/test_item_event_consumer.py -v
```

---

**Arquivo:** `reclamante/tests/integration/test_devolucao_event_consumer.py`

| Escopo | Descrição |
|-------|-----------|
| Consumer de devolução | Valida processamento de eventos de devolução no módulo Reclamante |

**Executar:**
```bash
pytest reclamante/tests/integration/test_devolucao_event_consumer.py -v
```

---

**Arquivo:** `reclamante/tests/integration/test_responsavel_event_consumer.py`

| Escopo | Descrição |
|-------|-----------|
| Consumer de responsável | Valida processamento de eventos de responsável no módulo Reclamante |

**Executar:**
```bash
pytest reclamante/tests/integration/test_responsavel_event_consumer.py -v
```

---

### Testes de API

**Arquivo:** `reclamante/tests/integration/test_reclamante_api.py`

#### POST /api/v1/reclamantes
| Teste | Status | Descrição |
|-------|--------|-----------|
| `test_criar_reclamante_com_sucesso` | 201 | Cria reclamante válido |
| `test_criar_reclamante_com_dados_invalidos` | 422 | Valida campos obrigatórios |
| `test_criar_reclamante_com_documento_vazio` | 400/422 | Valida documento |
| `test_criar_reclamante_com_campo_faltando` | 422 | Valida payload obrigatório |

#### GET /api/v1/reclamantes/{id}
| Teste | Status | Descrição |
|-------|--------|-----------|
| `test_buscar_reclamante_existente` | 200 | Retorna reclamante |
| `test_buscar_reclamante_inexistente` | 404 | Não encontrado |
| `test_buscar_reclamante_com_id_string` | 422 | Tipo inválido |

#### GET /api/v1/reclamantes
| Teste | Status | Descrição |
|-------|--------|-----------|
| `test_listar_todos_reclamantes` | 200 | Lista reclamantes |
| `test_listar_reclamantes_com_paginacao` | 200 | Paginação |

#### PUT /api/v1/reclamantes/{id}
| Teste | Status | Descrição |
|-------|--------|-----------|
| `test_atualizar_reclamante_com_sucesso` | 200 | Atualiza reclamante |
| `test_atualizar_reclamante_inexistente` | 404 | Não encontrado |
| `test_atualizar_reclamante_com_payload_incompleto` | 422 | Valida payload |

#### DELETE /api/v1/reclamantes/{id}
| Teste | Status | Descrição |
|-------|--------|-----------|
| `test_deletar_reclamante_com_sucesso` | 204 | Exclui reclamante |
| `test_deletar_reclamante_inexistente` | 404 | Não encontrado |

#### Observação de contrato

- O fluxo atual de API de Reclamante é orientado a `documento`.
- Referências antigas a busca por email devem ser consideradas legadas e fora do contrato atual.

**Executar:**
```bash
pytest reclamante/tests/integration/test_reclamante_api.py -v
```

---

## Integração Transversal (Raiz)

### Testes de Kafka entre Módulos

**Arquivo:** `tests/integration/test_kafka_messaging.py`

| Escopo | Descrição |
|-------|-----------|
| Mensageria Kafka | Valida publicação e consumo no broker |

**Executar:**
```bash
pytest tests/integration/test_kafka_messaging.py -v
```

---

**Arquivo:** `tests/integration/test_kafka_producers.py`

| Escopo | Descrição |
|-------|-----------|
| Producers | Valida produtores Kafka dos módulos |

**Executar:**
```bash
pytest tests/integration/test_kafka_producers.py -v
```

---

**Arquivo:** `tests/integration/test_kafka_cross_module_integration.py`

| Escopo | Descrição |
|-------|-----------|
| Fluxo cross-module | Valida integração orientada a eventos entre serviços |

**Executar:**
```bash
pytest tests/integration/test_kafka_cross_module_integration.py -v
```

---

## Boas Práticas

### Nomenclatura
```python
# ✅ Bom - nome descritivo
def test_criar_item_com_data_futura_deve_lancar_erro():

# ❌ Ruim - nome genérico
def test_item_1():
```

### Estrutura AAA
```python
def test_exemplo():
    # Arrange - Preparação
    item = Item(...)
    
    # Act - Ação
    resultado = funcao(item)
    
    # Assert - Verificação
    assert resultado.status == "disponivel"
```

### Independência
- Cada teste deve ser independente
- Usar fixtures para setup/teardown
- Não depender da ordem de execução

---

## Troubleshooting

### Testes sendo pulados (skipped)
```bash
pip install pytest-asyncio
```

### Erro de importação
```bash
# Adicionar ao PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Banco de dados bloqueado
```python
# Usar check_same_thread=False
engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    connect_args={"check_same_thread": False}
)
```

---

**Última atualização:** Março 2026 - Guia ampliado com consumers e testes transversais de Kafka
