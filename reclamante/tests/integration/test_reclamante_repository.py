import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os
from reclamante.src.domain.entities.reclamante import Reclamante
from reclamante.src.infrastructure.database.models import ReclamanteModel
from reclamante.src.infrastructure.repositories.reclamante_repository_impl import ReclamanteRepositoryImpl

# Configuração do banco de dados de teste
DATABASE_URL_TEST = "sqlite+aiosqlite:///./test_reclamante_repo.db"
engine_test = create_async_engine(DATABASE_URL_TEST, echo=True)
async_session_maker_test = sessionmaker(engine_test, class_=AsyncSession, expire_on_commit=False)

@pytest.fixture(scope="module", autouse=True)
async def setup_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(ReclamanteModel.metadata.create_all)
    yield
    os.remove("test_reclamante_repo.db")

@pytest.fixture
async def db_session() -> AsyncSession:
    async with async_session_maker_test() as session:
        yield session

@pytest.fixture
def repository(db_session: AsyncSession) -> ReclamanteRepositoryImpl:
    return ReclamanteRepositoryImpl(db_session)

@pytest.mark.asyncio
async def test_create_reclamante(repository: ReclamanteRepositoryImpl):
    reclamante = Reclamante(nome="Repo Test", documento="555", telefone="444")
    created_reclamante = await repository.create(reclamante)
    assert created_reclamante.id is not None
    assert created_reclamante.nome == "Repo Test"

@pytest.mark.asyncio
async def test_get_reclamante_by_id(repository: ReclamanteRepositoryImpl):
    reclamante = Reclamante(nome="Get Test", documento="666", telefone="333")
    created_reclamante = await repository.create(reclamante)
    
    found_reclamante = await repository.get_by_id(created_reclamante.id)
    assert found_reclamante is not None
    assert found_reclamante.id == created_reclamante.id
    assert found_reclamante.nome == "Get Test"

@pytest.mark.asyncio
async def test_get_all_reclamantes(repository: ReclamanteRepositoryImpl):
    # Limpa a tabela para garantir um estado limpo
    async with repository.session.begin():
        await repository.session.execute(ReclamanteModel.__table__.delete())

    reclamante1 = Reclamante(nome="List Test 1", documento="777", telefone="222")
    reclamante2 = Reclamante(nome="List Test 2", documento="888", telefone="111")
    await repository.create(reclamante1)
    await repository.create(reclamante2)

    reclamantes = await repository.get_all(0, 10)
    assert len(reclamantes) == 2
    assert reclamantes[0].nome == "List Test 1"
    assert reclamantes[1].nome == "List Test 2"

@pytest.mark.asyncio
async def test_update_reclamante(repository: ReclamanteRepositoryImpl):
    reclamante = Reclamante(nome="Update Old", documento="999", telefone="000")
    created_reclamante = await repository.create(reclamante)

    reclamante_atualizado = Reclamante(id=created_reclamante.id, nome="Update New", documento="999", telefone="123")
    updated_reclamante = await repository.update(created_reclamante.id, reclamante_atualizado)

    assert updated_reclamante is not None
    assert updated_reclamante.nome == "Update New"
    assert updated_reclamante.telefone == "123"

@pytest.mark.asyncio
async def test_delete_reclamante(repository: ReclamanteRepositoryImpl):
    reclamante = Reclamante(nome="Delete Test", documento="101", telefone="212")
    created_reclamante = await repository.create(reclamante)

    deleted = await repository.delete(created_reclamante.id)
    assert deleted is True

    not_found_reclamante = await repository.get_by_id(created_reclamante.id)
    assert not_found_reclamante is None
