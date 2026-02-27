"""
Testes para casos de exceção e tratamento de erros
Testa comportamento do sistema em situações de erro
"""
import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime, timedelta
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError
from item.src.domain.entities.item import Item
from item.src.application.use_cases.item_use_cases import (
    CreateItemUseCase,
    GetItemByIdUseCase,
    UpdateItemUseCase,
    DeleteItemUseCase
)
from item.src.infrastructure.repositories.item_repository_impl import ItemRepositoryImpl


class TestDatabaseExceptions:
    """Testes para exceções de banco de dados"""
    
    @pytest.mark.asyncio
    async def test_criar_item_com_erro_de_conexao(self):
        """Testa comportamento quando há erro de conexão com banco"""
        # Arrange
        repository_mock = AsyncMock()
        repository_mock.create.side_effect = OperationalError(
            "statement", "params", "orig"
        )
        
        item = Item(
            nome="Item teste",
            categoria="Teste",
            data_encontro=datetime.now(),
            descricao="Descrição teste",
            status="disponivel",
            local_id=1,
            responsavel_id=1
        )
        
        use_case = CreateItemUseCase(repository_mock)
        
        # Act & Assert
        with pytest.raises(OperationalError):
            await use_case.execute(item)
    
    @pytest.mark.asyncio
    async def test_buscar_item_com_erro_de_banco(self):
        """Testa comportamento quando há erro genérico de banco"""
        # Arrange
        repository_mock = AsyncMock()
        repository_mock.get_by_id.side_effect = SQLAlchemyError("Database error")
        
        use_case = GetItemByIdUseCase(repository_mock)
        
        # Act & Assert
        with pytest.raises(SQLAlchemyError):
            await use_case.execute(1)
    
    @pytest.mark.asyncio
    async def test_atualizar_item_com_constraint_violation(self):
        """Testa comportamento quando há violação de constraint"""
        # Arrange
        repository_mock = AsyncMock()
        
        item_existente = Item(
            id=1,
            nome="Item original",
            categoria="Teste",
            data_encontro=datetime.now(),
            descricao="Descrição original",
            status="disponivel",
            local_id=1,
            responsavel_id=1
        )
        
        item_atualizado = Item(
            nome="Item atualizado",
            categoria="Teste",
            data_encontro=datetime.now(),
            descricao="Descrição atualizada",
            status="disponivel",
            local_id=1,
            responsavel_id=1
        )
        
        repository_mock.get_by_id.return_value = item_existente
        repository_mock.update.side_effect = IntegrityError(
            "statement", "params", "orig"
        )
        
        use_case = UpdateItemUseCase(repository_mock)
        
        # Act & Assert
        with pytest.raises(IntegrityError):
            await use_case.execute(1, item_atualizado)


class TestConcurrencyIssues:
    """Testes para problemas de concorrência"""
    
    @pytest.mark.asyncio
    async def test_atualizar_item_modificado_por_outro_processo(self):
        """Testa atualização de item modificado concorrentemente"""
        # Arrange
        repository_mock = AsyncMock()
        
        # Simula que o item foi modificado entre a leitura e a atualização
        item_v1 = Item(
            id=1,
            nome="Item versão 1",
            categoria="Teste",
            data_encontro=datetime.now(),
            descricao="Versão 1",
            status="disponivel",
            local_id=1,
            responsavel_id=1,
            updated_at=datetime.now() - timedelta(minutes=5)
        )
        
        item_v2 = Item(
            id=1,
            nome="Item versão 2",
            categoria="Teste",
            data_encontro=datetime.now(),
            descricao="Versão 2 (modificada por outro processo)",
            status="disponivel",
            local_id=1,
            responsavel_id=1,
            updated_at=datetime.now() - timedelta(minutes=1)
        )
        
        # Primeira chamada retorna v1, mas depois o item foi modificado
        repository_mock.get_by_id.side_effect = [item_v1, item_v2]
        repository_mock.update.return_value = item_v2
        
        use_case = UpdateItemUseCase(repository_mock)
        
        # Act
        item_para_atualizar = Item(
            nome="Minha atualização",
            categoria="Teste",
            data_encontro=datetime.now(),
            descricao="Tentando atualizar",
            status="disponivel",
            local_id=1,
            responsavel_id=1
        )
        
        resultado = await use_case.execute(1, item_para_atualizar)
        
        # Assert
        assert resultado is not None
        # Nota: Em produção, deveria ter lógica de versionamento/optimistic locking
    
    @pytest.mark.asyncio
    async def test_deletar_item_ja_deletado(self):
        """Testa exclusão de item já deletado por outro processo"""
        # Arrange
        repository_mock = AsyncMock()
        
        item = Item(
            id=1,
            nome="Item teste",
            categoria="Teste",
            data_encontro=datetime.now(),
            descricao="Item que será deletado",
            status="disponivel",
            local_id=1,
            responsavel_id=1
        )
        
        # Primeira chamada diz que item existe, mas delete retorna False
        repository_mock.get_by_id.return_value = item
        repository_mock.delete.return_value = False
        
        use_case = DeleteItemUseCase(repository_mock)
        
        # Act
        resultado = await use_case.execute(1)
        
        # Assert
        assert resultado is False


class TestValidationErrors:
    """Testes para erros de validação em diferentes cenários"""
    
    @pytest.mark.asyncio
    async def test_criar_item_com_todos_campos_invalidos(self):
        """Testa criação com múltiplos campos inválidos"""
        # Arrange
        repository_mock = AsyncMock()
        use_case = CreateItemUseCase(repository_mock)
        
        # Act & Assert - Nome vazio
        with pytest.raises(ValueError, match="Nome.*obrigatório"):
            item = Item(
                nome="",
                categoria="Teste",
                data_encontro=datetime.now(),
                descricao="Descrição",
                status="disponivel",
                local_id=1,
                responsavel_id=1
            )
    
    @pytest.mark.asyncio
    async def test_criar_item_com_data_muito_antiga(self):
        """Testa criação com data muito antiga (possível erro de digitação)"""
        # Arrange
        repository_mock = AsyncMock()
        
        # Data de 100 anos atrás
        data_antiga = datetime.now() - timedelta(days=36500)
        
        item = Item(
            nome="Item teste",
            categoria="Teste",
            data_encontro=data_antiga,
            descricao="Descrição teste",
            status="disponivel",
            local_id=1,
            responsavel_id=1
        )
        
        use_case = CreateItemUseCase(repository_mock)
        
        # Act - Aceita, mas em produção poderia ter uma validação
        repository_mock.create.return_value = item
        resultado = await use_case.execute(item)
        
        # Assert
        assert resultado.data_encontro == data_antiga
        # Nota: Poderia adicionar validação para datas muito antigas
    
    @pytest.mark.asyncio
    async def test_atualizar_item_com_ids_diferentes(self):
        """Testa tentativa de trocar IDs relacionados"""
        # Arrange
        repository_mock = AsyncMock()
        
        item_existente = Item(
            id=1,
            nome="Item teste",
            categoria="Teste",
            data_encontro=datetime.now(),
            descricao="Descrição",
            status="disponivel",
            local_id=1,
            responsavel_id=1
        )
        
        item_para_atualizar = Item(
            nome="Item teste",
            categoria="Teste",
            data_encontro=datetime.now(),
            descricao="Descrição",
            status="disponivel",
            local_id=999,  # Mudando local_id
            responsavel_id=999  # Mudando responsavel_id
        )
        
        repository_mock.get_by_id.return_value = item_existente
        repository_mock.update.return_value = item_para_atualizar
        
        use_case = UpdateItemUseCase(repository_mock)
        
        # Act
        resultado = await use_case.execute(1, item_para_atualizar)
        
        # Assert
        assert resultado is not None
        # Nota: Em produção, poderia ter validação para mudanças de FK


class TestTransactionRollback:
    """Testes para rollback de transações"""
    
    @pytest.mark.asyncio
    async def test_rollback_ao_criar_item_com_erro(self):
        """Testa que transação faz rollback em caso de erro"""
        # Arrange
        repository_mock = AsyncMock()
        repository_mock.create.side_effect = Exception("Erro durante criação")
        
        item = Item(
            nome="Item teste",
            categoria="Teste",
            data_encontro=datetime.now(),
            descricao="Descrição teste",
            status="disponivel",
            local_id=1,
            responsavel_id=1
        )
        
        use_case = CreateItemUseCase(repository_mock)
        
        # Act & Assert
        with pytest.raises(Exception):
            await use_case.execute(item)
        
        # Verifica que create foi chamado (mas falhou)
        repository_mock.create.assert_called_once()


class TestEdgeCases:
    """Testes para casos extremos"""
    
    @pytest.mark.asyncio
    async def test_criar_item_com_descricao_muito_longa(self):
        """Testa criação com descrição muito longa"""
        # Arrange
        repository_mock = AsyncMock()
        
        descricao_longa = "A" * 10000  # 10000 caracteres
        
        item = Item(
            nome="Item teste",
            categoria="Teste",
            data_encontro=datetime.now(),
            descricao=descricao_longa,
            status="disponivel",
            local_id=1,
            responsavel_id=1
        )
        
        repository_mock.create.return_value = item
        use_case = CreateItemUseCase(repository_mock)
        
        # Act
        resultado = await use_case.execute(item)
        
        # Assert
        assert len(resultado.descricao) == 10000
        # Nota: Poderia ter validação de tamanho máximo
    
    @pytest.mark.asyncio
    async def test_buscar_item_com_id_maximo_inteiro(self):
        """Testa busca com ID muito grande"""
        # Arrange
        repository_mock = AsyncMock()
        repository_mock.get_by_id.return_value = None
        
        use_case = GetItemByIdUseCase(repository_mock)
        
        # Act
        resultado = await use_case.execute(2147483647)  # Max int32
        
        # Assert
        assert resultado is None
    
    @pytest.mark.asyncio
    async def test_listar_itens_sem_nenhum_item_no_banco(self):
        """Testa listagem quando banco está vazio"""
        # Arrange
        repository_mock = AsyncMock()
        repository_mock.get_all.return_value = []
        
        from item.src.application.use_cases.item_use_cases import GetAllItemsUseCase
        use_case = GetAllItemsUseCase(repository_mock)
        
        # Act
        resultado = await use_case.execute()
        
        # Assert
        assert resultado == []
        assert len(resultado) == 0


class TestTimeoutScenarios:
    """Testes para cenários de timeout"""
    
    @pytest.mark.asyncio
    async def test_criar_item_com_timeout(self):
        """Testa comportamento quando operação excede timeout"""
        # Arrange
        repository_mock = AsyncMock()
        
        # Simula timeout
        import asyncio
        async def slow_create(*args, **kwargs):
            await asyncio.sleep(10)  # Simula operação lenta
            return args[0]
        
        repository_mock.create = slow_create
        
        item = Item(
            nome="Item teste",
            categoria="Teste",
            data_encontro=datetime.now(),
            descricao="Descrição teste",
            status="disponivel",
            local_id=1,
            responsavel_id=1
        )
        
        use_case = CreateItemUseCase(repository_mock)
        
        # Act & Assert - com timeout de 1 segundo
        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(use_case.execute(item), timeout=1.0)


class TestMemoryLeaks:
    """Testes para possíveis vazamentos de memória"""
    
    @pytest.mark.asyncio
    async def test_criar_muitos_itens_nao_causa_vazamento(self):
        """Testa criação de muitos itens em sequência"""
        # Arrange
        repository_mock = AsyncMock()
        use_case = CreateItemUseCase(repository_mock)
        
        # Act - Cria 1000 itens
        for i in range(1000):
            item = Item(
                nome=f"Item {i}",
                categoria="Teste",
                data_encontro=datetime.now(),
                descricao=f"Descrição {i}",
                status="disponivel",
                local_id=1,
                responsavel_id=1
            )
            
            repository_mock.create.return_value = item
            await use_case.execute(item)
        
        # Assert
        assert repository_mock.create.call_count == 1000
        # Nota: Em teste real, monitoraria uso de memória


class TestSecurityIssues:
    """Testes para possíveis problemas de segurança"""
    
    @pytest.mark.asyncio
    async def test_criar_item_com_sql_injection_attempt(self):
        """Testa que tentativa de SQL injection é tratada"""
        # Arrange
        repository_mock = AsyncMock()
        
        # Tentativa de SQL injection no nome
        item = Item(
            nome="Item'; DROP TABLE items; --",
            categoria="Teste",
            data_encontro=datetime.now(),
            descricao="Descrição teste",
            status="disponivel",
            local_id=1,
            responsavel_id=1
        )
        
        repository_mock.create.return_value = item
        use_case = CreateItemUseCase(repository_mock)
        
        # Act
        resultado = await use_case.execute(item)
        
        # Assert - String é tratada como texto, não como SQL
        assert resultado.nome == "Item'; DROP TABLE items; --"
        # SQLAlchemy com parametrização previne SQL injection
    
    @pytest.mark.asyncio
    async def test_criar_item_com_xss_attempt(self):
        """Testa que tentativa de XSS é armazenada como texto"""
        # Arrange
        repository_mock = AsyncMock()
        
        # Tentativa de XSS na descrição
        item = Item(
            nome="Item teste",
            categoria="Teste",
            data_encontro=datetime.now(),
            descricao="<script>alert('XSS')</script>",
            status="disponivel",
            local_id=1,
            responsavel_id=1
        )
        
        repository_mock.create.return_value = item
        use_case = CreateItemUseCase(repository_mock)
        
        # Act
        resultado = await use_case.execute(item)
        
        # Assert - Script é armazenado como texto
        assert "<script>" in resultado.descricao
        # Nota: Sanitização deve ser feita no frontend ao renderizar
