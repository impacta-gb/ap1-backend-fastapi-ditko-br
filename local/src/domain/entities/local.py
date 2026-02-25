from datetime import datetime
from typing import Optional
from dataclasses import dataclass


@dataclass
class Local:
     """
    Entidade de domínio representando Local onde um item foi encontrado.
    
    Attributes:
        id: Identificador único do Local
        tipo: Descrição genérica do Local
        descricao: Descrição detalhada do Local
        bairro: bairro onde o Item foi encontrado
        created_at: Data de criação do registro do Local
        updated_at: Data de última atualização do registro do Local
    """
    id: int
    tipo: str
    descricao: str
    bairro: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
def __post_init__(self):
    """Validações da entidade após inicialização"""
    if not self.tipo or len(self.tipo.strip()) == 0:
        raise ValueError("Tipo do local é obrigatório")
    if not self.descricao or len(self.descricao.strip()) == 0:
        raise ValueError("Descrição do local é obrigatória")
    if not self.bairro or len(self.bairro.strip()) == 0:
        raise ValueError("Bairro do local é obrigatório")
    def atualizar_descricao(self, nova_descricao: str) -> None:
    """Atualiza a descrição do item"""
    if not nova_descricao or len(nova_descricao.strip()) == 0:
        raise ValueError("Nova descrição não pode estar vazia")
    self.descricao = nova_descricao
