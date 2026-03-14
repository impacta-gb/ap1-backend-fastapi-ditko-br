import pytest
from unittest.mock import AsyncMock
from reclamante.src.domain.entities.reclamante import Reclamante
from reclamante.src.application.use_cases.reclamante_use_cases import (
    CreateReclamanteUseCase,
    GetReclamanteByIdUseCase,
    GetAllReclamantesUseCase,
    UpdateReclamanteUseCase,
    DeleteReclamanteUseCase,
)

@pytest.mark.asyncio
async def test_create_reclamante_use_case():
    repository = AsyncMock()
    repository.create.return_value = Reclamante(id=1, nome="João", documento="123", telefone="12345")
    use_case = CreateReclamanteUseCase(repository)
    reclamante = Reclamante(nome="João", documento="123", telefone="12345")
    result = await use_case.execute(reclamante)
    assert result.id == 1
    repository.create.assert_called_once_with(reclamante)

@pytest.mark.asyncio
async def test_get_reclamante_by_id_use_case():
    repository = AsyncMock()
    repository.get_by_id.return_value = Reclamante(id=1, nome="João", documento="123", telefone="12345")
    use_case = GetReclamanteByIdUseCase(repository)
    result = await use_case.execute(1)
    assert result.id == 1
    repository.get_by_id.assert_called_once_with(1)

@pytest.mark.asyncio
async def test_get_all_reclamantes_use_case():
    repository = AsyncMock()
    repository.get_all.return_value = [Reclamante(id=1, nome="João", documento="123", telefone="12345")]
    use_case = GetAllReclamantesUseCase(repository)
    result = await use_case.execute(0, 10)
    assert len(result) == 1
    repository.get_all.assert_called_once_with(0, 10)

@pytest.mark.asyncio
async def test_update_reclamante_use_case():
    repository = AsyncMock()
    repository.get_by_id.return_value = Reclamante(id=1, nome="João", documento="123", telefone="12345")
    repository.update.return_value = Reclamante(id=1, nome="João Silva", documento="123", telefone="54321")
    use_case = UpdateReclamanteUseCase(repository)
    reclamante_atualizado = Reclamante(nome="João Silva", documento="123", telefone="54321")
    result = await use_case.execute(1, reclamante_atualizado)
    assert result.nome == "João Silva"
    assert result.telefone == "54321"
    repository.update.assert_called_once_with(1, reclamante_atualizado)

@pytest.mark.asyncio
async def test_delete_reclamante_use_case():
    repository = AsyncMock()
    repository.get_by_id.return_value = Reclamante(id=1, nome="João", documento="123", telefone="12345")
    repository.delete.return_value = True
    use_case = DeleteReclamanteUseCase(repository)
    result = await use_case.execute(1)
    assert result is True
    repository.delete.assert_called_once_with(1)
