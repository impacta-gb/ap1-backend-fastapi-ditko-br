from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from item.src.infrastructure.database.config import Base


class ItemModel(Base):
    """Modelo SQLAlchemy para a tabela de itens"""
    
    __tablename__ = "items"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome = Column(String(255), nullable=False, index=True)
    categoria = Column(String(100), nullable=False, index=True)
    data_encontro = Column(DateTime, nullable=False)
    descricao = Column(Text, nullable=False)
    status = Column(String(50), nullable=False, default="disponivel", index=True)
    # TODO: Adicionar ForeignKey quando implementar as entidades Local e Responsável
    local_id = Column(Integer, nullable=False)
    responsavel_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, onupdate=func.now())
    
    def __repr__(self):
        return f"<Item(id={self.id}, nome='{self.nome}', categoria='{self.categoria}', status='{self.status}')>"
