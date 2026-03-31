from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from .config import Base


class ReclamanteModel(Base):
    """Modelo SQLAlchemy para a tabela de reclamantes"""

    __tablename__ = "reclamantes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome = Column(String(255), nullable=False, index=True)
    documento = Column(String(255), nullable=False, index=True)
    telefone = Column(String(100), nullable=False, index=True)
    

    def __repr__(self):
        return f"<ReclamanteModel(id={self.id}, nome='{self.nome}')>"