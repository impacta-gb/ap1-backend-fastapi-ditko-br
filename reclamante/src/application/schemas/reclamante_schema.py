from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class ReclamanteBase(BaseModel):
    """Schema base para Reclamante"""
    nome: str = Field(..., min_length=1, max_length=255, description="Nome do Reclamante")
    telefone: str = Field(..., min_length=1, max_length=100, description="Telefone do Reclamante")
    documento: str = Field(..., description="Documento do Reclamante")


class ReclamanteCreate(ReclamanteBase):
    """Schema para criação de Reclamante"""


class ReclamanteUpdate(ReclamanteBase):
    """Schema para atualização completa de Reclamante (PUT).
    Todos os campos são obrigatórios — o recurso é substituído integralmente."""
    

class ReclamantePatch(BaseModel):
    """Schema para atualização parcial de Reclamante (PATCH)."""
    nome: Optional[str] = Field(None, min_length=1, max_length=255)
    telefone: Optional[str] = Field(None, min_length=1, max_length=100)
    documento: Optional[str] = None


class ReclamanteResponse(ReclamanteBase):
    """Schema de resposta para Reclamante"""
    id: int

    
    model_config = ConfigDict(from_attributes=True)


class ReclamanteListResponse(BaseModel):
    """Schema de resposta para lista de reclamantes"""
    reclamantes: list[ReclamanteResponse]
    total: int
    skip: int
    limit: int
