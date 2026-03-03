from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from local.src.infrastructure.database.config import Base


class LocalModel(Base):
    """Modelo SQLAlchemy para a tabela de locais"""

    __tablename__ = "locais"

    id = Column(Integer, primary_key=True, index= True, autoincrement = True)
    tipo = Column(String(255), nullable=False, index=True)
    descricao = Column(String(255), nullable=False, index=True)
    bairro  = Column(String(100), nullable=False, index=True)


    def __repr__(self):
        return f"<local(id={self.id}, tipo='{self.tipo}', descricao='{self.descricao}', bairro='{self.bairro}')"