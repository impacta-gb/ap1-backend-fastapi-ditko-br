import pytest
from pydantic import ValidationError
from reclamante.src.application.schemas.reclamante_schema import ReclamanteCreate, ReclamanteUpdate, ReclamanteResponse, ReclamanteListResponse

def test_reclamante_create_schema():
    data = {"nome": "João Silva", "documento": "123.456.789-00", "telefone": "11999999999"}
    schema = ReclamanteCreate(**data)
    assert schema.nome == data["nome"]
    assert schema.documento == data["documento"]
    assert schema.telefone == data["telefone"]

def test_reclamante_create_schema_nome_invalido():
    with pytest.raises(ValidationError):
        ReclamanteCreate(nome="", documento="123.456.789-00", telefone="11999999999")

def test_reclamante_update_schema():
    data = {"nome": "João Silva", "documento": "123.456.789-00", "telefone": "11999999999"}
    schema = ReclamanteUpdate(**data)
    assert schema.nome == data["nome"]
    assert schema.documento == data["documento"]
    assert schema.telefone == data["telefone"]

def test_reclamante_response_schema():
    data = {"id": 1, "nome": "João Silva", "documento": "123.456.789-00", "telefone": "11999999999"}
    schema = ReclamanteResponse(**data)
    assert schema.id == data["id"]
    assert schema.nome == data["nome"]
    assert schema.documento == data["documento"]
    assert schema.telefone == data["telefone"]

def test_reclamante_list_response_schema():
    reclamante_data = {"id": 1, "nome": "João Silva", "documento": "123.456.789-00", "telefone": "11999999999"}
    reclamante = ReclamanteResponse(**reclamante_data)
    list_data = {"reclamantes": [reclamante], "total": 1, "skip": 0, "limit": 10}
    schema = ReclamanteListResponse(**list_data)
    assert len(schema.reclamantes) == 1
    assert schema.reclamantes[0].nome == "João Silva"
    assert schema.total == 1
    assert schema.skip == 0
    assert schema.limit == 10
