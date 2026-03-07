"""Schemas Pydantic do módulo Local"""
from local.src.application.schemas.local_schema import (
    LocalBase,
    LocalCreate,
    LocalUpdate,
    LocalResponse,
    LocalListResponse,
)

__all__ = [
    "LocalBase",
    "LocalCreate",
    "LocalUpdate",
    "LocalResponse",
    "LocalListResponse",
]