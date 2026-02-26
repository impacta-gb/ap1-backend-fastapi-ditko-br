from typing import Optional
from dataclasses import dataclass


@dataclass
class Responsavel:
    """
    Entidade de domínio que representa um responsável pelo registro de um item perdido.

    Attributes:
        id: Identificador único do responsável.
        nome: Nome do responsável.
        cargo: Cargo do responsável.
        telefone: Telefone de contato do responsável.
        ativo: Indica se o responsável está ativo ou inativo.
    """

    nome: str
    cargo: str
    telefone: str
    ativo: bool
    id: Optional[int] = None


    def __post_init__(self):
        """
        Validação pós-inicialização do objeto Responsavel.
        """
        if not self.nome or len(self.nome.strip()) == 0:
            raise ValueError("Nome do responsável é obrigatório.")
        
        if not self.cargo or len(self.cargo.strip()) == 0:
            raise ValueError("Cargo do responsável é obrigatório.")
        
        if not self.telefone or len(self.telefone.strip()) == 0:
            raise ValueError("Telefone do responsável é obrigatório.")
        
        if not isinstance(self.ativo, bool):
            raise ValueError("Campo 'ativo' deve ser booleano.")
        

    def desativar_responsavel(self):
        """
        Desativa o responsável.
        """
        self.ativo = False