from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.presentation.api.routes import item_routes
from src.infrastructure.database.config import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação"""
    # Inicializa o banco de dados
    await init_db()
    yield

app = FastAPI(
    title="Sistema de Achados e Perdidos",
    description="API para gerenciamento de itens perdidos e encontrados",
    version="1.0.0",
    lifespan=lifespan
)

# Inclui as rotas
app.include_router(item_routes.router, prefix="/api/v1")


@app.get("/")
def read_root():
    return {
        'message': 'Bem-vindo ao Sistema de Achados e Perdidos',
        'docs': '/docs',
        'version': '1.0.0'
    }