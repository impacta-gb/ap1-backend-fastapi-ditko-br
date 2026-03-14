from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
# rotas
from item.src.presentation.api.routes import item_routes
from responsavel.src.presentation.api.routes import responsavel_routes
from local.src.presentation.api.routes import local_routes
# banco de dados
from local.src.infrastructure.database.config import init_db as init_db_local
from item.src.infrastructure.database.config import init_db as init_db_item
from responsavel.src.infrastructure.database.config import init_db as init_db_responsavel


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação"""
    # Inicializa os bancos de dados
    await init_db_item()
    await init_db_responsavel()
    await init_db_local()
    yield

app = FastAPI(
    title="Sistema de Achados e Perdidos",
    description="API para gerenciamento de itens perdidos e encontrados",
    version="1.0.0",
    lifespan=lifespan
)

# Middleware para tratamento de exceções
@app.exception_handler(ValueError)
async def value_error_exception_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"message": str(exc)},
    )

# Inclui as rotas
app.include_router(item_routes.router, prefix="/api/v1/items")
app.include_router(responsavel_routes.router, prefix="/api/v1/responsaveis")
app.include_router(local_routes.router, prefix="/api/v1/local")


@app.get("/")
def read_root():
    return {
        'message': 'Bem-vindo ao Sistema de Achados e Perdidos',
        'docs': '/docs',
        'version': '1.0.0'
    }
