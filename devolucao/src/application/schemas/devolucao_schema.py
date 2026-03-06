from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class DevolucaoBase(BaseModel):
    """Schema base para devolução."""
    id_reclamante: int = Field(..., gt=0, description="ID do reclamante")
    id_item: int = Field(..., gt=0, description="ID do item devolvido")
    observacao: str = Field(..., min_length=1, max_length=255, description="Observação sobre a devolução")
    data_devolucao: datetime = Field(default_factory=datetime.now, description="Data da devolução")


class DevolucaoCreate(DevolucaoBase):
    """Schema para criar uma nova devolução."""
    pass


class DevolucaoUpdate(DevolucaoBase):
    """Schema para atualizar uma devolução."""
    pass


class DevolucaoPatch(BaseModel):
    """Schema para atualizar parcialmente uma devolução."""
    id_reclamante: Optional[int] = Field(None, gt=0, description="ID do reclamante")
    id_item: Optional[int] = Field(None, gt=0, description="ID do item devolvido")
    observacao: Optional[str] = Field(None, min_length=1, max_length=255, description="Observação sobre a devolução")
    data_devolucao: Optional[datetime] = Field(None, description="Data da devolução")


class DevolucaoResponse(DevolucaoBase):
    """Schema de resposta para devolução."""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class DevolucaoListResponse(BaseModel):
    """Schema de resposta para lista de devoluções."""
    devolucoes: list[DevolucaoResponse]
    total: int
    skip: int
    limit: int
