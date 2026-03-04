"""
Testes unitários para a entidade Responsavel
"""
import pytest
from responsavel.src.domain.entities.responsavel import Responsavel


class TestResponsavelEntity:
    """Testes para a entidade Responsavel"""

    def test_criar_responsavel_valido(self):
        """Testa a criação de um responsável válido"""
        responsavel = Responsavel(
            nome="João Silva",
            cargo="Segurança",
            telefone="11999999999",
            ativo=True
        )

        assert responsavel.nome == "João Silva"
        assert responsavel.cargo == "Segurança"
        assert responsavel.telefone == "11999999999"
        assert responsavel.ativo is True
        assert responsavel.id is None

    def test_criar_responsavel_ativo_false(self):
        """Testa criação de responsável com ativo=False"""
        responsavel = Responsavel(
            nome="Maria Souza",
            cargo="Recepcionista",
            telefone="11988887777",
            ativo=False
        )

        assert responsavel.ativo is False

    def test_criar_responsavel_com_id(self):
        """Testa criação de responsável com ID (simulando objeto do banco)"""
        responsavel = Responsavel(
            id=10,
            nome="Carlos Lima",
            cargo="Gerente",
            telefone="21977776666",
            ativo=True
        )

        assert responsavel.id == 10
        assert responsavel.nome == "Carlos Lima"

    def test_criar_responsavel_sem_nome(self):
        """Testa que não é possível criar responsável sem nome"""
        with pytest.raises(ValueError, match="Nome do responsável é obrigatório"):
            Responsavel(
                nome="",
                cargo="Segurança",
                telefone="11999999999",
                ativo=True
            )

    def test_criar_responsavel_com_nome_apenas_espacos(self):
        """Testa que não é possível criar responsável com nome contendo apenas espaços"""
        with pytest.raises(ValueError, match="Nome do responsável é obrigatório"):
            Responsavel(
                nome="   ",
                cargo="Segurança",
                telefone="11999999999",
                ativo=True
            )

    def test_criar_responsavel_sem_cargo(self):
        """Testa que não é possível criar responsável sem cargo"""
        with pytest.raises(ValueError, match="Cargo do responsável é obrigatório"):
            Responsavel(
                nome="João Silva",
                cargo="",
                telefone="11999999999",
                ativo=True
            )

    def test_criar_responsavel_com_cargo_apenas_espacos(self):
        """Testa que não é possível criar responsável com cargo contendo apenas espaços"""
        with pytest.raises(ValueError, match="Cargo do responsável é obrigatório"):
            Responsavel(
                nome="João Silva",
                cargo="   ",
                telefone="11999999999",
                ativo=True
            )

    def test_criar_responsavel_sem_telefone(self):
        """Testa que não é possível criar responsável sem telefone"""
        with pytest.raises(ValueError, match="Telefone do responsável é obrigatório"):
            Responsavel(
                nome="João Silva",
                cargo="Segurança",
                telefone="",
                ativo=True
            )

    def test_criar_responsavel_com_telefone_apenas_espacos(self):
        """Testa que não é possível criar responsável com telefone contendo apenas espaços"""
        with pytest.raises(ValueError, match="Telefone do responsável é obrigatório"):
            Responsavel(
                nome="João Silva",
                cargo="Segurança",
                telefone="   ",
                ativo=True
            )

    def test_criar_responsavel_com_ativo_nao_booleano(self):
        """Testa que campo ativo deve ser booleano"""
        with pytest.raises((ValueError, TypeError)):
            Responsavel(
                nome="João Silva",
                cargo="Segurança",
                telefone="11999999999",
                ativo="sim"  # type: ignore
            )

    def test_desativar_responsavel(self):
        """Testa o método para desativar um responsável"""
        responsavel = Responsavel(
            nome="João Silva",
            cargo="Segurança",
            telefone="11999999999",
            ativo=True
        )

        assert responsavel.ativo is True

        responsavel.desativar_responsavel()

        assert responsavel.ativo is False

    def test_desativar_responsavel_ja_inativo(self):
        """Testa desativar um responsável que já está inativo"""
        responsavel = Responsavel(
            nome="João Silva",
            cargo="Segurança",
            telefone="11999999999",
            ativo=False
        )

        # Não deve lançar erro
        responsavel.desativar_responsavel()

        assert responsavel.ativo is False

    def test_responsavel_representacao(self):
        """Testa que o responsável pode ser instanciado com todos os campos"""
        responsavel = Responsavel(
            id=1,
            nome="Ana Paula",
            cargo="Coordenadora",
            telefone="31966665555",
            ativo=True
        )

        assert responsavel.id == 1
        assert responsavel.nome == "Ana Paula"
        assert responsavel.cargo == "Coordenadora"
        assert responsavel.telefone == "31966665555"
        assert responsavel.ativo is True
