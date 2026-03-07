"""
Testes unitários para a entidade Devolucao
"""
import pytest
from datetime import datetime, timedelta
from devolucao.src.domain.entities.devolucao import Devolucao


class TestDevolucaoEntity:
    """Testes para a entidade Devolucao"""

    def test_criar_devolucao_valida(self):
        """Testa a criação de uma devolução válida com todos os campos obrigatórios"""
        # Arrange & Act
        devolucao = Devolucao(
            reclamante_id=1,
            item_id=2,
            observacao="Item devolvido ao dono com sucesso"
        )

        # Assert
        assert devolucao.reclamante_id == 1
        assert devolucao.item_id == 2
        assert devolucao.observacao == "Item devolvido ao dono com sucesso"
        assert devolucao.id is None
        assert devolucao.created_at is None
        assert devolucao.updated_at is None

    def test_criar_devolucao_com_id(self):
        """Testa criação de devolução com ID (simulando objeto retornado do banco)"""
        # Arrange & Act
        devolucao = Devolucao(
            id=5,
            reclamante_id=10,
            item_id=3,
            observacao="Devolvido na recepção"
        )

        # Assert
        assert devolucao.id == 5
        assert devolucao.reclamante_id == 10
        assert devolucao.item_id == 3

    def test_criar_devolucao_com_data_devolucao(self):
        """Testa criação de devolução com data de devolução explícita"""
        # Arrange
        data = datetime.now() - timedelta(days=1)

        # Act
        devolucao = Devolucao(
            reclamante_id=1,
            item_id=1,
            observacao="Devolvido ontem",
            data_devolucao=data
        )

        # Assert
        assert devolucao.data_devolucao == data

    def test_criar_devolucao_com_datas_de_auditoria(self):
        """Testa criação de devolução com datas de auditoria (simulando retorno do banco)"""
        # Arrange
        now = datetime.now()

        # Act
        devolucao = Devolucao(
            id=1,
            reclamante_id=1,
            item_id=1,
            observacao="Devolvido",
            created_at=now,
            updated_at=now
        )

        # Assert
        assert devolucao.created_at == now
        assert devolucao.updated_at == now

    def test_criar_devolucao_com_reclamante_id_negativo(self):
        """Testa que reclamante_id negativo é inválido"""
        # Act & Assert
        with pytest.raises(ValueError, match="O ID do reclamante deve ser um número positivo"):
            Devolucao(
                reclamante_id=-1,
                item_id=1,
                observacao="Observação válida"
            )

    def test_criar_devolucao_com_reclamante_id_zero(self):
        """Testa que reclamante_id zero é inválido"""
        # Act & Assert
        with pytest.raises(ValueError, match="O ID do reclamante deve ser um número positivo"):
            Devolucao(
                reclamante_id=0,
                item_id=1,
                observacao="Observação válida"
            )

    def test_criar_devolucao_com_item_id_negativo(self):
        """Testa que item_id negativo é inválido"""
        # Act & Assert
        with pytest.raises(ValueError, match="O ID do item deve ser um número positivo"):
            Devolucao(
                reclamante_id=1,
                item_id=-1,
                observacao="Observação válida"
            )

    def test_criar_devolucao_com_item_id_zero(self):
        """Testa que item_id zero é inválido"""
        # Act & Assert
        with pytest.raises(ValueError, match="O ID do item deve ser um número positivo"):
            Devolucao(
                reclamante_id=1,
                item_id=0,
                observacao="Observação válida"
            )

    def test_criar_devolucao_sem_observacao(self):
        """Testa que não é possível criar devolução sem observação"""
        # Act & Assert
        with pytest.raises(ValueError, match="A observação é obrigatória"):
            Devolucao(
                reclamante_id=1,
                item_id=1,
                observacao=""
            )

    def test_criar_devolucao_com_observacao_apenas_espacos(self):
        """Testa que observação com apenas espaços é inválida"""
        # Act & Assert
        with pytest.raises(ValueError, match="A observação é obrigatória"):
            Devolucao(
                reclamante_id=1,
                item_id=1,
                observacao="   "
            )

    def test_atualizar_observacao_com_sucesso(self):
        """Testa atualização de observação com valor válido"""
        # Arrange
        devolucao = Devolucao(
            reclamante_id=1,
            item_id=1,
            observacao="Observação original"
        )

        # Act
        devolucao.atualizar_observacao("Nova observação atualizada")

        # Assert
        assert devolucao.observacao == "Nova observação atualizada"

    def test_atualizar_observacao_com_valor_vazio_falha(self):
        """Testa que atualizar observação com valor vazio lança erro"""
        # Arrange
        devolucao = Devolucao(
            reclamante_id=1,
            item_id=1,
            observacao="Observação original"
        )

        # Act & Assert
        with pytest.raises(ValueError, match="Nova observação não pode estar vazia"):
            devolucao.atualizar_observacao("")

    def test_atualizar_observacao_com_apenas_espacos_falha(self):
        """Testa que atualizar observação com apenas espaços lança erro"""
        # Arrange
        devolucao = Devolucao(
            reclamante_id=1,
            item_id=1,
            observacao="Observação original"
        )

        # Act & Assert
        with pytest.raises(ValueError, match="Nova observação não pode estar vazia"):
            devolucao.atualizar_observacao("   ")

    def test_devolucao_representacao_completa(self):
        """Testa instanciação com todos os campos"""
        # Arrange & Act
        now = datetime.now()
        devolucao = Devolucao(
            id=99,
            reclamante_id=7,
            item_id=4,
            observacao="Devolução completa registrada",
            data_devolucao=now,
            created_at=now,
            updated_at=now
        )

        # Assert
        assert devolucao.id == 99
        assert devolucao.reclamante_id == 7
        assert devolucao.item_id == 4
        assert devolucao.observacao == "Devolução completa registrada"
        assert devolucao.data_devolucao == now
        assert devolucao.created_at == now
        assert devolucao.updated_at == now
