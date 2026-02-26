from sqlalchemy import Column, Integer, String, Boolean
from responsavel.src.infrastructure.database.config import Base

class ResponsavelModel(Base):
    """Modelo SQLAlchemy para a tabela de responsáveis"""

    __tablename__ = "responsaveis"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    cargo = Column(String(255), nullable=False)
    telefone = Column(String(11), nullable=False)
    ativo = Column(Boolean, default=True)

    def __repr__(self):
        return f"<Responsavel(id={self.id}, nome='{self.nome}', cargo='{self.cargo}', telefone='{self.telefone}', ativo={self.ativo})>"
    