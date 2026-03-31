from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import text
import os
from pathlib import Path

DEFAULT_DB_PATH = Path(__file__).resolve().parents[3] / "devolucao.db"
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite+aiosqlite:///{DEFAULT_DB_PATH.as_posix()}")

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True
)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

# Importa os modelos para registrar tabelas no metadata antes do create_all.
from . import models  # noqa: E402,F401

async def get_session() -> AsyncSession:
    """Dependency para obter sessão do banco de dados"""
    async with async_session_maker() as session:
        yield session

async def init_db():
    """Inicializa o banco de dados criando todas as tabelas"""
    async with engine.begin() as conn:
        # Migração leve para compatibilizar versões antigas da projeção.
        result = await conn.execute(text("PRAGMA table_info(reclamante_references)"))
        existing_columns = [row[1] for row in result.fetchall()]
        if "email" in existing_columns and "documento" not in existing_columns:
            await conn.execute(
                text("ALTER TABLE reclamante_references RENAME COLUMN email TO documento")
            )

        await conn.run_sync(Base.metadata.create_all)
        