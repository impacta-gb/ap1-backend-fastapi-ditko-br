from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
# rotas
from src.presentation.api.routes import devolucao_routes
from bootstrap import MessagingBootstrap
# banco de dados
from src.infrastructure.database.config import init_db as init_db_devolucao
from src.application.use_cases.sync_item_projection_use_case import sync_item_projection_for_devolucao
from src.application.use_cases.sync_reclamante_projection_use_case import sync_reclamante_projection_for_devolucao


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação"""
    # Inicializa os bancos de dados
    await init_db_devolucao()


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

# Inclui a rota
app.include_router(devolucao_routes.router, prefix="/api/v1/devolucoes")


@app.get("/")
def read_root():
    return {
        'message': 'Bem-vindo ao Sistema de Achados e Perdidos',
        'docs': '/docs',
        'version': '1.0.0'
    }
