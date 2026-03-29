from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class ItemBase(BaseModel):
    """Schema base para Item"""
    nome: str = Field(..., min_length=1, max_length=255, description="Nome do item")
    categoria: str = Field(..., min_length=1, max_length=100, description="Categoria do item")
    data_encontro: datetime = Field(..., description="Data em que o item foi encontrado")
    descricao: str = Field(..., min_length=1, description="Descrição detalhada do item")
    status: str = Field(default="disponivel", description="Status do item")
    local_id: int = Field(..., gt=0, description="ID do local onde foi encontrado")
    responsavel_id: int = Field(..., gt=0, description="ID do responsável pelo registro")


class ItemCreate(ItemBase):
    """Schema para criação de Item"""
    # Remove status - novos itens sempre começam como 'disponivel'
    status: str = Field(default="disponivel", description="Status do item (sempre 'disponivel' na criação)")


class ItemUpdate(BaseModel):
    """Schema para atualização de Item"""
    nome: str = Field(..., min_length=1, max_length=255)
    categoria: str = Field(..., min_length=1, max_length=100)
    data_encontro: datetime = Field(...)
    descricao: str = Field(..., min_length=1)
    status: str = Field(...)
    local_id: int = Field(..., gt=0)
    responsavel_id: int = Field(..., gt=0)


class ItemPatch(BaseModel):
    """Schema para atualização parcial de Item"""
    nome: Optional[str] = Field(None, min_length=1, max_length=255)
    categoria: Optional[str] = Field(None, min_length=1, max_length=100)
    data_encontro: Optional[datetime] = None
    descricao: Optional[str] = Field(None, min_length=1)
    status: Optional[str] = None
    local_id: Optional[int] = Field(None, gt=0)
    responsavel_id: Optional[int] = Field(None, gt=0)


class ItemResponse(ItemBase):
    """Schema de resposta para Item"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class ItemListResponse(BaseModel):
    """Schema de resposta para lista de itens"""
    items: list[ItemResponse]
    total: int
    skip: int
    limit: int
