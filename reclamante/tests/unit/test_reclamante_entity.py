"""
Testes unitários para a entidade de domínio Reclamante
"""
import pytest
from reclamante.src.domain.entities.reclamante import Reclamante


class TestReclamanteEntity:
    """Testes para a entidade Reclamante"""

    def test_criar_reclamante_valido(self):
        """Testa criação de reclamante com dados válidos"""
        # Arrange & Act
        reclamante = Reclamante(
            id=1,
            nome="João Silva",
            telefone="11999999999",
            documento="123.456.789-00",
        )

        # Assert
        assert reclamante.id == 1
        assert reclamante.nome == "João Silva"
        assert reclamante.telefone == "11999999999"
        assert reclamante.documento == "123.456.789-00"

    def test_criar_reclamante_sem_id(self):
        """Testa criação de reclamante sem ID"""
        # Arrange & Act
        reclamante = Reclamante(
            nome="Maria Souza",
            telefone="11988887777",
            documento="987.654.321-00",
        )

        # Assert
        assert reclamante.id is None
        assert reclamante.nome == "Maria Souza"

    def test_criar_reclamante_sem_nome(self):
        """Testa que nome vazio gera erro"""
        # Act & Assert
        with pytest.raises(ValueError, match="Nome do reclamante é obrigatório"):
            Reclamante(nome="", telefone="11999999999", documento="123")

    def test_criar_reclamante_com_nome_apenas_espacos(self):
        """Testa que nome com apenas espaços gera erro"""
        # Act & Assert
        with pytest.raises(ValueError, match="Nome do reclamante é obrigatório"):
            Reclamante(nome="   ", telefone="11999999999", documento="123")

    def test_criar_reclamante_sem_telefone(self):
        """Testa que telefone vazio gera erro"""
        # Act & Assert
        with pytest.raises(ValueError, match="Telefone do reclamante é obrigatório"):
            Reclamante(nome="João", telefone="", documento="123")

    def test_criar_reclamante_com_telefone_apenas_espacos(self):
        """Testa que telefone com apenas espaços gera erro"""
        # Act & Assert
        with pytest.raises(ValueError, match="Telefone do reclamante é obrigatório"):
            Reclamante(nome="João", telefone="   ", documento="123")

    def test_criar_reclamante_sem_documento(self):
        """Testa que documento vazio gera erro"""
        # Act & Assert
        with pytest.raises(ValueError, match="Documento do reclamante é obrigatório"):
            Reclamante(nome="João", telefone="11999999999", documento="")

    def test_criar_reclamante_com_documento_apenas_espacos(self):
        """Testa que documento com apenas espaços gera erro"""
        # Act & Assert
        with pytest.raises(ValueError, match="Documento do reclamante é obrigatório"):
            Reclamante(nome="João", telefone="11999999999", documento="   ")

    def test_atualizar_telefone_com_sucesso(self):
        """Testa atualização de telefone via método de domínio"""
        # Arrange
        reclamante = Reclamante(
            nome="João Silva",
            telefone="11999999999",
            documento="123",
        )

        # Act
        reclamante.atualizar_telefone("11911112222")

        # Assert
        assert reclamante.telefone == "11911112222"

    def test_atualizar_telefone_vazio_falha(self):
        """Testa que atualização com telefone vazio falha"""
        # Arrange
        reclamante = Reclamante(
            nome="João Silva",
            telefone="11999999999",
            documento="123",
        )

        # Act & Assert
        with pytest.raises(ValueError, match="Novo telefone não pode estar vazio"):
            reclamante.atualizar_telefone("")

    def test_atualizar_telefone_apenas_espacos_falha(self):
        """Testa que atualização com telefone em branco falha"""
        # Arrange
        reclamante = Reclamante(
            nome="João Silva",
            telefone="11999999999",
            documento="123",
        )

        # Act & Assert
        with pytest.raises(ValueError, match="Novo telefone não pode estar vazio"):
            reclamante.atualizar_telefone("   ")

    def test_representacao_padrao_dataclass(self):
        """Testa representação textual padrão da entidade"""
        # Arrange & Act
        reclamante = Reclamante(
            id=10,
            nome="Repr Test",
            telefone="11999990000",
            documento="DOC-10",
        )

        # Assert
        representacao = repr(reclamante)
        assert "Reclamante(" in representacao
        assert "Repr Test" in representacao
