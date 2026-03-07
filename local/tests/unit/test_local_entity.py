"""
Testes unitários para a entidade Local
"""
import pytest
from local.src.domain.entities.local import Local


class TestLocalEntity:
    """Testes para a entidade Local"""

    def test_criar_local_valido(self):
        """Testa a criação de um local válido com todos os campos obrigatórios"""
        # Arrange & Act
        local = Local(
            tipo="Metrô",
            descricao="Estação Sé - Plataforma Central",
            bairro="Centro"
        )

        # Assert
        assert local.tipo == "Metrô"
        assert local.descricao == "Estação Sé - Plataforma Central"
        assert local.bairro == "Centro"
        assert local.id is None
        assert local.created_at is None
        assert local.updated_at is None

    def test_criar_local_com_id(self):
        """Testa criação de local com ID (simulando objeto retornado do banco)"""
        # Arrange & Act
        local = Local(
            id=10,
            tipo="Ônibus",
            descricao="Linha 179 - sentido terminal",
            bairro="Mooca"
        )

        # Assert
        assert local.id == 10
        assert local.tipo == "Ônibus"
        assert local.bairro == "Mooca"

    def test_criar_local_sem_tipo(self):
        """Testa que não é possível criar local sem tipo"""
        # Act & Assert
        with pytest.raises(ValueError, match="Tipo do local é obrigatório"):
            Local(
                tipo="",
                descricao="Descrição válida",
                bairro="Centro"
            )

    def test_criar_local_com_tipo_apenas_espacos(self):
        """Testa que tipo com apenas espaços é inválido"""
        # Act & Assert
        with pytest.raises(ValueError, match="Tipo do local é obrigatório"):
            Local(
                tipo="   ",
                descricao="Descrição válida",
                bairro="Centro"
            )

    def test_criar_local_sem_descricao(self):
        """Testa que não é possível criar local sem descrição"""
        # Act & Assert
        with pytest.raises(ValueError, match="Descrição do local é obrigatória"):
            Local(
                tipo="Metrô",
                descricao="",
                bairro="Centro"
            )

    def test_criar_local_com_descricao_apenas_espacos(self):
        """Testa que descrição com apenas espaços é inválida"""
        # Act & Assert
        with pytest.raises(ValueError, match="Descrição do local é obrigatória"):
            Local(
                tipo="Metrô",
                descricao="   ",
                bairro="Centro"
            )

    def test_criar_local_sem_bairro(self):
        """Testa que não é possível criar local sem bairro"""
        # Act & Assert
        with pytest.raises(ValueError, match="Bairro do local é obrigatório"):
            Local(
                tipo="Metrô",
                descricao="Estação Central",
                bairro=""
            )

    def test_criar_local_com_bairro_apenas_espacos(self):
        """Testa que bairro com apenas espaços é inválido"""
        # Act & Assert
        with pytest.raises(ValueError, match="Bairro do local é obrigatório"):
            Local(
                tipo="Metrô",
                descricao="Estação Central",
                bairro="   "
            )

    def test_atualizar_descricao_com_sucesso(self):
        """Testa atualização de descrição com valor válido"""
        # Arrange
        local = Local(
            tipo="Parque",
            descricao="Descrição original",
            bairro="Liberdade"
        )

        # Act
        local.atualizar_descricao("Nova descrição atualizada")

        # Assert
        assert local.descricao == "Nova descrição atualizada"

    def test_atualizar_descricao_com_valor_vazio_falha(self):
        """Testa que atualizar descrição com valor vazio lança erro"""
        # Arrange
        local = Local(
            tipo="Parque",
            descricao="Descrição original",
            bairro="Liberdade"
        )

        # Act & Assert
        with pytest.raises(ValueError, match="Nova descrição não pode estar vazia"):
            local.atualizar_descricao("")

    def test_atualizar_descricao_com_apenas_espacos_falha(self):
        """Testa que atualizar descrição com apenas espaços lança erro"""
        # Arrange
        local = Local(
            tipo="Parque",
            descricao="Descrição original",
            bairro="Liberdade"
        )

        # Act & Assert
        with pytest.raises(ValueError, match="Nova descrição não pode estar vazia"):
            local.atualizar_descricao("   ")

    def test_local_representacao_completa(self):
        """Testa instanciação com todos os campos"""
        # Arrange & Act
        local = Local(
            id=5,
            tipo="Shopping",
            descricao="Shopping Center Norte - Piso 2",
            bairro="Vila Guilherme"
        )

        # Assert
        assert local.id == 5
        assert local.tipo == "Shopping"
        assert local.descricao == "Shopping Center Norte - Piso 2"
        assert local.bairro == "Vila Guilherme"
