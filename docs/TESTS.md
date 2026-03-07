# Guia de Testes do Projeto

Documentação prática para implementação e execução de testes no projeto.

## Estrutura de Testes

```
tests/
├── conftest.py           # Fixtures compartilhadas
├── unit/                 # Testes unitários (sem dependências externas)
├── integration/          # Testes de integração (com banco de dados)
└── api/                  # Testes de endpoints HTTP
```

## Comandos Principais

### Executar Todos os Testes
```bash
pytest item/tests/ -v
```

### Por Categoria
```bash
pytest item/tests/unit/ -v              # Apenas unitários
pytest item/tests/integration/ -v       # Apenas integração
pytest item/tests/api/ -v               # Apenas API
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

### Reclamante (Planejado)
- **Total:** ~70 testes (em desenvolvimento)

### Devolução (Planejado)
- **Total:** ~90 testes (em desenvolvimento)

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

**Última atualização:** Março 2026 - Local (90 testes implementados)
