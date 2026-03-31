from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from .config import Base


class LocalModel(Base):
    """Modelo SQLAlchemy para a tabela de locais"""

    __tablename__ = "locais"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    tipo = Column(String(255), nullable=False, index=True)
    descricao = Column(String(255), nullable=False, index=True)
    bairro = Column(String(100), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    def __repr__(self):
        return f"<LocalModel(id={self.id}, tipo='{self.tipo}', bairro='{self.bairro}')>"