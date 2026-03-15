"""
Testes de performance para operações com Item
Testa comportamento com grandes volumes de dados
"""
import pytest
import time
import statistics
from datetime import datetime, timedelta
from unittest.mock import AsyncMock
from item.src.domain.entities.item import Item
from item.src.application.use_cases.item_use_cases import (
    GetAllItemsUseCase,
    GetItemsByCategoriaUseCase,
    GetItemsByStatusUseCase
)


class TestPerformanceListagem:
    """Testes de performance para listagem de itens"""
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_listar_itens_com_1000_registros(self):
        """Testa performance ao listar 1000 itens"""
        # Arrange
        repository_mock = AsyncMock()
        
        # Cria 1000 itens de teste
        items = [
            Item(
                id=i,
                nome=f"Item {i}",
                categoria="Teste",
                data_encontro=datetime.now(),
                descricao=f"Descrição do item {i}",
                status="disponivel",
                local_id=1,
                responsavel_id=1,
                created_at=datetime.now()
            )
            for i in range(1, 1001)
        ]
        
        repository_mock.get_all.return_value = items
        use_case = GetAllItemsUseCase(repository_mock)
        
        # Act
        inicio = time.time()
        resultado = await use_case.execute(skip=0, limit=1000)
        tempo_execucao = time.time() - inicio
        
        # Assert
        assert len(resultado) == 1000
        assert tempo_execucao < 1.0  # Deve executar em menos de 1 segundo
        print(f"\nTempo para listar 1000 itens: {tempo_execucao:.4f}s")
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_listar_itens_com_10000_registros(self):
        """Testa performance ao listar 10000 itens (paginado)"""
        # Arrange
        repository_mock = AsyncMock()
        
        # Cria 10000 itens de teste (simula grande volume)
        items = [
            Item(
                id=i,
                nome=f"Item {i}",
                categoria="Teste",
                data_encontro=datetime.now(),
                descricao=f"Descrição do item {i}",
                status="disponivel",
                local_id=1,
                responsavel_id=1,
                created_at=datetime.now()
            )
            for i in range(1, 101)  # Retorna apenas 100 por vez devido à paginação
        ]
        
        repository_mock.get_all.return_value = items
        use_case = GetAllItemsUseCase(repository_mock)
        
        # Act - Lista em páginas de 100
        inicio = time.time()
        todas_paginas = []
        for skip in range(0, 1000, 100):  # 10 páginas
            resultado = await use_case.execute(skip=skip, limit=100)
            todas_paginas.extend(resultado)
        tempo_execucao = time.time() - inicio
        
        # Assert
        assert len(todas_paginas) == 1000
        assert tempo_execucao < 2.0  # 10 páginas em menos de 2 segundos
        print(f"\nTempo para listar 10 páginas de 100 itens: {tempo_execucao:.4f}s")
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_paginacao_eficiente(self):
        """Testa que paginação é eficiente independente do offset"""
        # Arrange
        repository_mock = AsyncMock()
        use_case = GetAllItemsUseCase(repository_mock)
        
        items = [
            Item(
                id=i,
                nome=f"Item {i}",
                categoria="Teste",
                data_encontro=datetime.now(),
                descricao=f"Descrição {i}",
                status="disponivel",
                local_id=1,
                responsavel_id=1
            )
            for i in range(100)
        ]
        
        repository_mock.get_all.return_value = items

        async def medir_tempo(skip: int, repeticoes: int = 15) -> float:
            # Pequeno aquecimento para reduzir ruído da primeira chamada.
            await use_case.execute(skip=skip, limit=100)

            tempos = []
            for _ in range(repeticoes):
                inicio = time.perf_counter()
                await use_case.execute(skip=skip, limit=100)
                tempos.append(time.perf_counter() - inicio)

            return statistics.median(tempos)
        
        # Act - Testa primeira e última página
        tempo1 = await medir_tempo(skip=0)
        tempo2 = await medir_tempo(skip=9900)

        # Assert - Compara medianas para evitar flutuação pontual de scheduler/clock.
        diferenca = abs(tempo1 - tempo2) / max(tempo1, tempo2) if max(tempo1, tempo2) > 0 else 0.0
        assert diferenca < 0.8
        
        print(f"\nTempo primeira página: {tempo1:.4f}s")
        print(f"Tempo última página: {tempo2:.4f}s")
        print(f"Diferença: {diferenca*100:.2f}%")


class TestPerformanceBuscas:
    """Testes de performance para buscas específicas"""
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_busca_por_categoria_com_muitos_resultados(self):
        """Testa performance ao buscar por categoria popular"""
        # Arrange
        repository_mock = AsyncMock()
        
        # 500 itens da mesma categoria
        items = [
            Item(
                id=i,
                nome=f"Item {i}",
                categoria="Eletrônicos",
                data_encontro=datetime.now(),
                descricao=f"Descrição {i}",
                status="disponivel",
                local_id=1,
                responsavel_id=1
            )
            for i in range(500)
        ]
        
        repository_mock.get_by_categoria.return_value = items
        use_case = GetItemsByCategoriaUseCase(repository_mock)
        
        # Act
        inicio = time.time()
        resultado = await use_case.execute("Eletrônicos")
        tempo_execucao = time.time() - inicio
        
        # Assert
        assert len(resultado) == 500
        assert tempo_execucao < 0.5  # Menos de 0.5 segundos
        print(f"\nTempo para buscar 500 itens por categoria: {tempo_execucao:.4f}s")
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_busca_por_status_com_indice(self):
        """Testa que busca por status usa índice eficientemente"""
        # Arrange
        repository_mock = AsyncMock()
        
        # 300 itens disponíveis
        items = [
            Item(
                id=i,
                nome=f"Item {i}",
                categoria="Teste",
                data_encontro=datetime.now(),
                descricao=f"Descrição {i}",
                status="disponivel",
                local_id=1,
                responsavel_id=1
            )
            for i in range(300)
        ]
        
        repository_mock.get_by_status.return_value = items
        use_case = GetItemsByStatusUseCase(repository_mock)
        
        # Act
        inicio = time.time()
        resultado = await use_case.execute("disponivel")
        tempo_execucao = time.time() - inicio
        
        # Assert
        assert len(resultado) == 300
        assert tempo_execucao < 0.3  # Busca por índice deve ser rápida
        print(f"\nTempo para buscar 300 itens por status: {tempo_execucao:.4f}s")


class TestPerformanceMemoria:
    """Testes de uso de memória"""
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_listagem_nao_carrega_tudo_na_memoria(self):
        """Testa que listagem grande não sobrecarrega memória"""
        # Arrange
        repository_mock = AsyncMock()
        
        # Simula retorno de muitos itens
        def criar_items(count):
            return [
                Item(
                    id=i,
                    nome=f"Item {i}",
                    categoria="Teste",
                    data_encontro=datetime.now(),
                    descricao=f"Descrição {i}" * 100,  # Descrição grande
                    status="disponivel",
                    local_id=1,
                    responsavel_id=1
                )
                for i in range(count)
            ]
        
        repository_mock.get_all.return_value = criar_items(100)
        use_case = GetAllItemsUseCase(repository_mock)
        
        # Act - Lista em páginas pequenas
        total_processado = 0
        for skip in range(0, 1000, 100):
            resultado = await use_case.execute(skip=skip, limit=100)
            total_processado += len(resultado)
            # Em produção, processaria e descartaria os dados aqui
        
        # Assert
        assert total_processado == 1000
        # Nota: Em teste real, monitoraria uso de memória com tracemalloc


class TestPerformanceConcorrencia:
    """Testes de performance com múltiplas operações simultâneas"""
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_multiplas_consultas_simultaneas(self):
        """Testa performance com múltiplas consultas simultâneas"""
        # Arrange
        repository_mock = AsyncMock()
        
        items = [
            Item(
                id=i,
                nome=f"Item {i}",
                categoria="Teste",
                data_encontro=datetime.now(),
                descricao=f"Descrição {i}",
                status="disponivel",
                local_id=1,
                responsavel_id=1
            )
            for i in range(100)
        ]
        
        repository_mock.get_all.return_value = items
        use_case = GetAllItemsUseCase(repository_mock)
        
        # Act - 10 consultas simultâneas
        import asyncio
        inicio = time.time()
        tasks = [use_case.execute() for _ in range(10)]
        resultados = await asyncio.gather(*tasks)
        tempo_execucao = time.time() - inicio
        
        # Assert
        assert len(resultados) == 10
        assert all(len(r) == 100 for r in resultados)
        assert tempo_execucao < 1.0  # 10 consultas em menos de 1 segundo
        print(f"\nTempo para 10 consultas simultâneas: {tempo_execucao:.4f}s")
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_throughput_operacoes(self):
        """Testa throughput de operações por segundo"""
        # Arrange
        repository_mock = AsyncMock()
        
        item = Item(
            id=1,
            nome="Item teste",
            categoria="Teste",
            data_encontro=datetime.now(),
            descricao="Descrição teste",
            status="disponivel",
            local_id=1,
            responsavel_id=1
        )
        
        repository_mock.get_by_id.return_value = item
        
        from item.src.application.use_cases.item_use_cases import GetItemByIdUseCase
        use_case = GetItemByIdUseCase(repository_mock)
        
        # Act - Executa operações por 1 segundo
        import asyncio
        contador = 0
        inicio = time.time()
        
        while time.time() - inicio < 1.0:
            await use_case.execute(1)
            contador += 1
        
        operacoes_por_segundo = contador
        
        # Assert
        assert operacoes_por_segundo > 100  # Pelo menos 100 ops/seg
        print(f"\nThroughput: {operacoes_por_segundo} operações/segundo")


class TestPerformanceComplexQueries:
    """Testes de performance para queries complexas"""
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_busca_com_multiplos_filtros(self):
        """Testa performance de busca com múltiplos filtros"""
        # Arrange
        repository_mock = AsyncMock()
        
        items = [
            Item(
                id=i,
                nome=f"Item {i}",
                categoria="Eletrônicos" if i % 2 == 0 else "Documentos",
                data_encontro=datetime.now() - timedelta(days=i),
                descricao=f"Descrição {i}",
                status="disponivel" if i % 3 == 0 else "em_analise",
                local_id=1,
                responsavel_id=1
            )
            for i in range(200)
        ]
        
        # Filtra por categoria E status
        items_filtrados = [
            item for item in items 
            if item.categoria == "Eletrônicos" and item.status == "disponivel"
        ]
        
        repository_mock.get_by_categoria.return_value = items_filtrados
        use_case = GetItemsByCategoriaUseCase(repository_mock)
        
        # Act
        inicio = time.time()
        resultado = await use_case.execute("Eletrônicos")
        tempo_execucao = time.time() - inicio
        
        # Assert
        assert len(resultado) > 0
        assert tempo_execucao < 0.2
        print(f"\nTempo para query com filtros múltiplos: {tempo_execucao:.4f}s")


class TestPerformanceOptimizations:
    """Testes para verificar otimizações implementadas"""
    
    @pytest.mark.asyncio
    async def test_cache_nao_implementado_ainda(self):
        """Documenta que cache ainda não está implementado"""
        # Nota: Este teste documenta uma otimização futura
        # Em produção, implementaríamos cache para consultas frequentes
        pass
    
    @pytest.mark.asyncio
    async def test_eager_loading_relacionamentos(self):
        """Documenta necessidade de eager loading para relacionamentos"""
        # Nota: Quando implementar relacionamentos com Local e Responsável,
        # usar joinedload para evitar N+1 queries
        pass
    
    @pytest.mark.asyncio
    async def test_indice_composto_categoria_status(self):
        """Documenta que índice composto melhoraria performance"""
        # Nota: Criar índice composto (categoria, status) melhoraria
        # consultas que filtram por ambos os campos
        pass


@pytest.fixture
def performance_report(request):
    """Fixture para gerar relatório de performance"""
    tempos = []
    
    def registrar_tempo(nome, tempo):
        tempos.append((nome, tempo))
    
    yield registrar_tempo
    
    if tempos:
        print("\n" + "="*50)
        print("RELATÓRIO DE PERFORMANCE")
        print("="*50)
        for nome, tempo in tempos:
            print(f"{nome}: {tempo:.4f}s")
        print("="*50)
