from sqlalchemy import Column, Integer, DateTime, Text, String
from sqlalchemy.sql import func
from devolucao.src.infrastructure.database.config import Base


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


class ItemReferenceModel(Base):
    """Projeção do item para sincronização com devolução
    Mantém estado sincronizado via eventos item_events
    """

    __tablename__ = "item_references"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    local_id = Column(Integer, nullable=False)
    responsavel_id = Column(Integer, nullable=False)
    status = Column(String(50), nullable=False, default="disponivel")
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, onupdate=func.now(), nullable=True)

    def __repr__(self):
        return f"<ItemReference(id={self.id}, status={self.status}, local_id={self.local_id}, responsavel_id={self.responsavel_id})>"


class ReclamanteReferenceModel(Base):
    """Projeção do reclamante para sincronização com devolução
    Mantém estado sincronizado via eventos reclamante_events
    """

    __tablename__ = "reclamante_references"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    documento = Column(String(255), nullable=True)
    telefone = Column(String(20), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, onupdate=func.now(), nullable=True)

    def __repr__(self):
        return f"<ReclamanteReference(id={self.id}, nome={self.nome})>"
    