from datetime import datetime
from typing import Optional
from dataclasses import dataclass


@dataclass
class Item:
    """
    Entidade de domínio representando um item perdido/encontrado.
    
    Attributes:
        id: Identificador único do item
        nome: Nome/descrição breve do item
        categoria: Classificação do item (eletrônicos, documentos, etc.)
        data_encontro: Data em que o item foi encontrado
        descricao: Descrição detalhada do item
        status: Status atual (disponível, devolvido, etc.)
        local_id: ID do local onde o item foi encontrado
        responsavel_id: ID do responsável que registrou o item
        created_at: Data de criação do registro
        updated_at: Data de última atualização do registro
    """
    nome: str
    categoria: str
    data_encontro: datetime
    descricao: str
    status: str
    local_id: int
    responsavel_id: int
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Validações da entidade após inicialização"""
        if not self.nome or len(self.nome.strip()) == 0:
            raise ValueError("Nome do item é obrigatório")
        
        if not self.categoria or len(self.categoria.strip()) == 0:
            raise ValueError("Categoria do item é obrigatória")
        
        if not self.descricao or len(self.descricao.strip()) == 0:
            raise ValueError("Descrição do item é obrigatória")
        
        # Normaliza o status removendo acentos e salvando em minúsculas
        self.status = self.status.lower().replace('í', 'i').replace('é', 'e').replace('á', 'a')
        if self.status not in ['disponivel', 'devolvido', 'em_analise']:
            raise ValueError("Status deve ser: disponivel, devolvido ou em_analise")
    
    def marcar_como_devolvido(self) -> None:
        """Marca o item como devolvido"""
        self.status = 'devolvido'
        self.updated_at = datetime.now()
    
    def atualizar_descricao(self, nova_descricao: str) -> None:
        """Atualiza a descrição do item"""
        if not nova_descricao or len(nova_descricao.strip()) == 0:
            raise ValueError("Nova descrição não pode estar vazia")
        self.descricao = nova_descricao
        self.updated_at = datetime.now()
