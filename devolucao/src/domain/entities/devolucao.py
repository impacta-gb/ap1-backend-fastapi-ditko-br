from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field


@dataclass
class Devolucao:
    """
    Entidade de domínio que representa uma devolução de um item perdido.

    Attributes:
        id: Identificador único da devolução.
        id_reclamante: ID do reclamante.
        id_item: ID do item devolvido.
        observacao: Observação sobre a devolução.
        data_devolucao: Data da devolução.
        created_at: Data de criação do registro.
        updated_at: Data da última atualização do registro.
    """

    id_reclamante: int
    id_item: int
    observacao: str
    data_devolucao: datetime = field(default_factory=datetime.now)
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """Validação pós-inicialização do objeto Devolucao."""
        if self.id_reclamante <= 0:
            raise ValueError("O ID do reclamante deve ser um número positivo.")
        if self.id_item <= 0:
            raise ValueError("O ID do item deve ser um número positivo.")
        if not self.observacao or len(self.observacao.strip()) == 0:
            raise ValueError("A observação é obrigatória.")

    def atualizar_observacao(self, nova_observacao: str) -> None:
        """Atualiza a observação da devolução."""
        if not nova_observacao or len(nova_observacao.strip()) == 0:
            raise ValueError("Nova observação não pode estar vazia.")
        self.observacao = nova_observacao
