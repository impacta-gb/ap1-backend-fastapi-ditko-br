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

### Responsável (Planejado)
- **Total:** ~100 testes (em desenvolvimento)

### Local (Planejado)
- **Total:** ~80 testes (em desenvolvimento)

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

**Última atualização:** Fevereiro 2026 - Item (113 testes implementados)
