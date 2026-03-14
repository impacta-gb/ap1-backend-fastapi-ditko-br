from fastapi import FastAPI
from contextlib import asynccontextmanager
# rotas
from item.src.presentation.api.routes import item_routes
from responsavel.src.presentation.api.routes import responsavel_routes
from local.src.presentation.api.routes import local_routes
from devolucao.src.presentation.api.routes import devolucao_routes
from reclamante.src.presentation.api.routes import reclamante_routes
# banco de dados
from local.src.infrastructure.database.config import init_db as init_db_local
from item.src.infrastructure.database.config import init_db as init_db_item
from responsavel.src.infrastructure.database.config import init_db as init_db_responsavel
from devolucao.src.infrastructure.database.config import init_db as init_db_devolucao
from reclamante.src.infrastructure.database.config import init_db as init_db_reclamante


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação"""
    # Inicializa os bancos de dados
    await init_db_item()
    await init_db_responsavel()
    await init_db_local()
    await init_db_devolucao()
    await init_db_reclamante()
    yield

app = FastAPI(
    title="Sistema de Achados e Perdidos",
    description="API para gerenciamento de itens perdidos e encontrados",
    version="1.0.0",
    lifespan=lifespan
)

# Inclui as rotas
app.include_router(item_routes.router, prefix="/api/v1/items")
app.include_router(responsavel_routes.router, prefix="/api/v1/responsaveis")
app.include_router(local_routes.router, prefix="/api/v1/local")
app.include_router(devolucao_routes.router, prefix="/api/v1/devolucoes")
app.include_router(reclamante_routes.router, prefix="/api/v1/reclamantes")

@app.get("/")
def read_root():
    return {
        'message': 'Bem-vindo ao Sistema de Achados e Perdidos',
        'docs': '/docs',
        'version': '1.0.0'
    }
