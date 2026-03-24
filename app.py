from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
# rotas
from item.src.presentation.api.routes import item_routes
from responsavel.src.presentation.api.routes import responsavel_routes
from local.src.presentation.api.routes import local_routes
from devolucao.src.presentation.api.routes import devolucao_routes
from reclamante.src.presentation.api.routes import reclamante_routes
from bootstrap import MessagingBootstrap
# banco de dados
from local.src.infrastructure.database.config import init_db as init_db_local
from item.src.infrastructure.database.config import init_db as init_db_item
from responsavel.src.infrastructure.database.config import init_db as init_db_responsavel
from devolucao.src.infrastructure.database.config import init_db as init_db_devolucao
from reclamante.src.infrastructure.database.config import init_db as init_db_reclamante
from item.src.application.use_cases.sync_local_projection_use_case import sync_local_projection_for_item
from item.src.application.use_cases.sync_responsavel_projection_use_case import sync_responsavel_projection_for_item
from devolucao.src.application.use_cases.sync_item_projection_use_case import sync_item_projection_for_devolucao
from devolucao.src.application.use_cases.sync_reclamante_projection_use_case import sync_reclamante_projection_for_devolucao


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação"""
    # Inicializa os bancos de dados
    await init_db_local()
    await init_db_responsavel()
    await init_db_item()
    await init_db_devolucao()
    await init_db_reclamante()

    # Reconstroi projeções críticas para evitar inconsistência após restart.
    await sync_local_projection_for_item()
    await sync_responsavel_projection_for_item()
    await sync_item_projection_for_devolucao()
    await sync_reclamante_projection_for_devolucao()

    # Inicializa mensageria (producers/consumers Kafka)
    messaging_bootstrap = MessagingBootstrap()
    app.state.messaging_bootstrap = messaging_bootstrap
    await messaging_bootstrap.start_producers()
    await messaging_bootstrap.start_consumers()

    try:
        yield
    finally:
        # Garante encerramento limpo da mensageria no shutdown
        await messaging_bootstrap.stop_consumers()
        await messaging_bootstrap.stop_producers()

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
app.include_router(local_routes.router, prefix="/api/v1/locais")
app.include_router(devolucao_routes.router, prefix="/api/v1/devolucoes")
app.include_router(reclamante_routes.router, prefix="/api/v1/reclamantes")

@app.get("/")
def read_root():
    return {
        'message': 'Bem-vindo ao Sistema de Achados e Perdidos',
        'docs': '/docs',
        'version': '1.0.0'
    }
