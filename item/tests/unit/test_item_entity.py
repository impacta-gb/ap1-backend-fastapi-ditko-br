"""
Testes unitários para a entidade Item
"""
import pytest
from datetime import datetime, timedelta
from item.src.domain.entities.item import Item


class TestItemEntity:
    """Testes para a entidade Item"""
    
    def test_criar_item_valido(self):
        """Testa a criação de um item válido"""
        data_encontro = datetime.now() - timedelta(days=1)
        
        item = Item(
            nome="Carteira de couro",
            categoria="Documentos",
            data_encontro=data_encontro,
            descricao="Carteira de couro marrom com documentos",
            status="disponivel",
            local_id=1,
            responsavel_id=1
        )
        
        assert item.nome == "Carteira de couro"
        assert item.categoria == "Documentos"
        assert item.data_encontro == data_encontro
        assert item.descricao == "Carteira de couro marrom com documentos"
        assert item.status == "disponivel"
        assert item.local_id == 1
        assert item.responsavel_id == 1
        assert item.id is None
        assert item.created_at is None
        assert item.updated_at is None
    
    def test_criar_item_sem_nome(self):
        """Testa que não é possível criar item sem nome"""
        with pytest.raises(ValueError, match="Nome do item é obrigatório"):
            Item(
                nome="",
                categoria="Documentos",
                data_encontro=datetime.now(),
                descricao="Descrição teste",
                status="disponivel",
                local_id=1,
                responsavel_id=1
            )
    
    def test_criar_item_com_nome_apenas_espacos(self):
        """Testa que não é possível criar item com nome contendo apenas espaços"""
        with pytest.raises(ValueError, match="Nome do item é obrigatório"):
            Item(
                nome="   ",
                categoria="Documentos",
                data_encontro=datetime.now(),
                descricao="Descrição teste",
                status="disponivel",
                local_id=1,
                responsavel_id=1
            )
    
    def test_criar_item_sem_categoria(self):
        """Testa que não é possível criar item sem categoria"""
        with pytest.raises(ValueError, match="Categoria do item é obrigatória"):
            Item(
                nome="Item teste",
                categoria="",
                data_encontro=datetime.now(),
                descricao="Descrição teste",
                status="disponivel",
                local_id=1,
                responsavel_id=1
            )
    
    def test_criar_item_sem_descricao(self):
        """Testa que não é possível criar item sem descrição"""
        with pytest.raises(ValueError, match="Descrição do item é obrigatória"):
            Item(
                nome="Item teste",
                categoria="Documentos",
                data_encontro=datetime.now(),
                descricao="",
                status="disponivel",
                local_id=1,
                responsavel_id=1
            )
    
    def test_criar_item_com_status_invalido(self):
        """Testa que não é possível criar item com status inválido"""
        with pytest.raises(ValueError, match="Status deve ser: disponivel, devolvido ou em_analise"):
            Item(
                nome="Item teste",
                categoria="Documentos",
                data_encontro=datetime.now(),
                descricao="Descrição teste",
                status="invalido",
                local_id=1,
                responsavel_id=1
            )
    
    def test_status_normalizado_disponivel_com_acento(self):
        """Testa que status 'disponível' é normalizado para 'disponivel'"""
        item = Item(
            nome="Item teste",
            categoria="Documentos",
            data_encontro=datetime.now(),
            descricao="Descrição teste",
            status="disponível",
            local_id=1,
            responsavel_id=1
        )
        
        assert item.status == "disponivel"
    
    def test_status_normalizado_em_analise_com_acento(self):
        """Testa que status 'em_análise' é normalizado para 'em_analise'"""
        item = Item(
            nome="Item teste",
            categoria="Documentos",
            data_encontro=datetime.now(),
            descricao="Descrição teste",
            status="em_análise",
            local_id=1,
            responsavel_id=1
        )
        
        assert item.status == "em_analise"
    
    def test_status_normalizado_maiusculas(self):
        """Testa que status em maiúsculas é normalizado para minúsculas"""
        item = Item(
            nome="Item teste",
            categoria="Documentos",
            data_encontro=datetime.now(),
            descricao="Descrição teste",
            status="DISPONIVEL",
            local_id=1,
            responsavel_id=1
        )
        
        assert item.status == "disponivel"
    
    def test_marcar_como_devolvido(self):
        """Testa o método para marcar item como devolvido"""
        item = Item(
            nome="Item teste",
            categoria="Documentos",
            data_encontro=datetime.now(),
            descricao="Descrição teste",
            status="disponivel",
            local_id=1,
            responsavel_id=1
        )
        
        assert item.status == "disponivel"
        
        item.marcar_como_devolvido()
        
        assert item.status == "devolvido"
    
    def test_atualizar_descricao_valida(self):
        """Testa atualização de descrição com valor válido"""
        item = Item(
            nome="Item teste",
            categoria="Documentos",
            data_encontro=datetime.now(),
            descricao="Descrição original",
            status="disponivel",
            local_id=1,
            responsavel_id=1
        )
        
        nova_descricao = "Nova descrição atualizada"
        item.atualizar_descricao(nova_descricao)
        
        assert item.descricao == nova_descricao
    
    def test_atualizar_descricao_vazia(self):
        """Testa que não é possível atualizar descrição para valor vazio"""
        item = Item(
            nome="Item teste",
            categoria="Documentos",
            data_encontro=datetime.now(),
            descricao="Descrição original",
            status="disponivel",
            local_id=1,
            responsavel_id=1
        )
        
        with pytest.raises(ValueError, match="Nova descrição não pode estar vazia"):
            item.atualizar_descricao("")
    
    def test_atualizar_descricao_apenas_espacos(self):
        """Testa que não é possível atualizar descrição para valor com apenas espaços"""
        item = Item(
            nome="Item teste",
            categoria="Documentos",
            data_encontro=datetime.now(),
            descricao="Descrição original",
            status="disponivel",
            local_id=1,
            responsavel_id=1
        )
        
        with pytest.raises(ValueError, match="Nova descrição não pode estar vazia"):
            item.atualizar_descricao("   ")
    
    def test_item_com_id_e_timestamps(self):
        """Testa criação de item com ID e timestamps (simulando item do banco)"""
        data_encontro = datetime.now() - timedelta(days=1)
        created_at = datetime.now() - timedelta(hours=1)
        updated_at = datetime.now()
        
        item = Item(
            id=1,
            nome="Item teste",
            categoria="Documentos",
            data_encontro=data_encontro,
            descricao="Descrição teste",
            status="disponivel",
            local_id=1,
            responsavel_id=1,
            created_at=created_at,
            updated_at=updated_at
        )
        
        assert item.id == 1
        assert item.created_at == created_at
        assert item.updated_at == updated_at
