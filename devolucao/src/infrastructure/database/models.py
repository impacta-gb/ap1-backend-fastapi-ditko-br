from sqlalchemy import Column, Integer, DateTime, Text
from sqlalchemy.sql import func
from item.src.infrastructure.database.config import Base


class DevolucaoModel(Base):
    """Modelo SQLAlchemy para a tabela de devoluções"""

    __tablename__ = "devolucoes"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    data_devolucao = Column(DateTime, nullable=False)
    observacao = Column(Text, nullable=False)
    reclamante_id = Column(Integer, nullable=False)
    item_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, onupdate=func.now())


    def __repr__(self):
        return f"<Devolucao(id={self.id}, data_devolucao={self.data_devolucao}, observacao={self.observacao}, reclamante_id={self.reclamante_id}, item_id={self.item_id})>"
    