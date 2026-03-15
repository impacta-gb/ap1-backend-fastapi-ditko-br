from datetime import datetime
from typing import Optional
from dataclasses import dataclass


@dataclass
class Reclamante:
    """
    Entidade de domínio representando um Reclamante.
    
    Attributes:
        id: Identificador único do reclamante
        nome: Nome do reclamante
        telefone: Numero de telefone do reclamante
        documento: documento de identificação do reclamante
        
    """
    nome: str
    telefone: str
    documento: datetime
    id: Optional[int] = None
    
    
    def __post_init__(self):
        """Validações da entidade após inicialização"""
        if not self.nome or len(self.nome.strip()) == 0:
            raise ValueError("Nome do reclamante é obrigatório")
        
        if not self.telefone or len(self.telefone.strip()) == 0:
            raise ValueError("Telefone do reclamante é obrigatório")
        
        if not self.documento or len(self.documento.strip()) == 0:
            raise ValueError("Documento do reclamante é obrigatório")
        
        
    
    
    
    def atualizar_telefone(self, novo_telefone: str) -> None:
        """Atualiza a descrição do item"""
        if not novo_telefone or len(novo_telefone.strip()) == 0:
            raise ValueError("Novo telefone não pode estar vazio")
        self.telefone = novo_telefone
