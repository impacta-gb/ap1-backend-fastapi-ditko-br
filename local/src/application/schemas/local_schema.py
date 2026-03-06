from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

class LocalBase(BaseModel):
    """Schema base para item"""
    tipo: str = Field(..., min_length = 1, max_length = 255, description = "Tipo do local")
    descricao: str = Field(..., min_length = 1, max_length = 255, description = "Descrição do local")
    bairro: str = Field(..., min_length = 1, max_length = 255, description = "Bairro onde foi encontrado")
    
class LocalCreate(LocalBase):
    """Schema para criação de Local"""

class LocalUpdate(LocalBase):
    tipo: Optional[str] = Field(None, min_length = 1, max_length = 255)
    descricao: Optional[str] = Field(None, min_length = 1, max_length = 255)
    bairro: Optional[str] = Field(None, min_length = 1, max_length = 255)

class LocalResponse(BaseModel):
    """Schema de resposta para local"""
    id: int
    tipo: str
    descricao: str
    bairro: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


class LocalListResponse(BaseModel):
    """Schema de resposta para listagem de locais"""
    locals: List[LocalResponse]
    total: int
    skip: int
    limit: int
