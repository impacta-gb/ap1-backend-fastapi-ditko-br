from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator


class ResponsavelBase(BaseModel):
    """Schema base para responsável."""
    nome: str = Field(..., min_length=1, max_length=255, description="Nome do responsável")
    cargo: str = Field(..., min_length=1, max_length=255, description="Cargo do responsável")
    telefone: str = Field(..., min_length=10, max_length=11, description="Telefone do responsável (com DDD)")
    ativo: bool = Field(default=True, description="Indica se o responsável está ativo")
    
    @field_validator('telefone')
    @classmethod
    def validate_telefone(cls, v: str) -> str:
        """Valida formato básico do telefone."""
        # Remove caracteres especiais para validação
        telefone_limpo = v.replace("(", "").replace(")", "").replace("-", "").replace(" ", "")
        
        if not telefone_limpo.isdigit():
            raise ValueError("Telefone deve conter apenas números")
        
        if len(telefone_limpo) < 10 or len(telefone_limpo) > 11:
            raise ValueError("Telefone deve ter 10 ou 11 dígitos (DDD + número)")
        
        return v


class ResponsavelCreate(BaseModel):
    """Schema para criar um novo responsável."""
    nome: str = Field(..., min_length=1, max_length=255, description="Nome do responsável")
    cargo: str = Field(..., min_length=1, max_length=255, description="Cargo do responsável")
    telefone: str = Field(..., min_length=10, max_length=11, description="Telefone do responsável (com DDD)")
    # ativo não aparece aqui - sempre inicia como True conforme regra de negócio
    
    @field_validator('telefone')
    @classmethod
    def validate_telefone(cls, v: str) -> str:
        """Valida formato básico do telefone."""
        telefone_limpo = v.replace("(", "").replace(")", "").replace("-", "").replace(" ", "")
        
        if not telefone_limpo.isdigit():
            raise ValueError("Telefone deve conter apenas números")
        
        if len(telefone_limpo) < 10 or len(telefone_limpo) > 11:
            raise ValueError("Telefone deve ter 10 ou 11 dígitos (DDD + número)")
        
        return v


class ResponsavelUpdate(BaseModel):
    """Schema para atualizar um responsável existente (PUT - atualização completa)."""
    nome: str = Field(..., min_length=1, max_length=255, description="Nome do responsável")
    cargo: str = Field(..., min_length=1, max_length=255, description="Cargo do responsável")
    telefone: str = Field(..., min_length=10, max_length=11, description="Telefone do responsável")
    # ativo não pode ser alterado diretamente - use endpoint específico
    
    @field_validator('telefone')
    @classmethod
    def validate_telefone(cls, v: str) -> str:
        """Valida formato básico do telefone."""
        telefone_limpo = v.replace("(", "").replace(")", "").replace("-", "").replace(" ", "")
        
        if not telefone_limpo.isdigit():
            raise ValueError("Telefone deve conter apenas números")
        
        if len(telefone_limpo) < 10 or len(telefone_limpo) > 11:
            raise ValueError("Telefone deve ter 10 ou 11 dígitos (DDD + número)")
        
        return v


class ResponsavelPatch(BaseModel):
    """Schema para atualização parcial de responsável (PATCH - sem alterar ativo)."""
    nome: Optional[str] = Field(None, min_length=1, max_length=255, description="Nome do responsável")
    cargo: Optional[str] = Field(None, min_length=1, max_length=255, description="Cargo do responsável")
    telefone: Optional[str] = Field(None, min_length=10, max_length=11, description="Telefone do responsável")
    # ativo não pode ser alterado diretamente - use endpoint específico
    
    @field_validator('telefone')
    @classmethod
    def validate_telefone(cls, v: Optional[str]) -> Optional[str]:
        """Valida formato básico do telefone se fornecido."""
        if v is None:
            return v
        
        telefone_limpo = v.replace("(", "").replace(")", "").replace("-", "").replace(" ", "")
        
        if not telefone_limpo.isdigit():
            raise ValueError("Telefone deve conter apenas números")
        
        if len(telefone_limpo) < 10 or len(telefone_limpo) > 11:
            raise ValueError("Telefone deve ter 10 ou 11 dígitos (DDD + número)")
        
        return v


class ResponsavelStatusUpdate(BaseModel):
    """Schema para alterar status ativo/inativo do responsável."""
    ativo: bool = Field(..., description="Status ativo/inativo do responsável")


class ResponsavelResponse(ResponsavelBase):
    """Schema de resposta para um responsável."""
    id: int
    
    model_config = ConfigDict(from_attributes=True)


class ResponsavelListResponse(BaseModel):
    """Schema de resposta para lista de responsáveis."""
    responsaveis: list[ResponsavelResponse]
    total: int
    skip: int
    limit: int
    