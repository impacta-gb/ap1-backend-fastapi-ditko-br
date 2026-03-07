"""Configuração do banco de dados do módulo Local"""
from local.src.infrastructure.database.config import Base, get_session, init_db
from local.src.infrastructure.database.models import LocalModel

__all__ = ["Base", "get_session", "init_db", "LocalModel"]
