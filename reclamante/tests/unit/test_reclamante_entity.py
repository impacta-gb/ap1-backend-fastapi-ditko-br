import pytest
from reclamante.src.domain.entities.reclamante import Reclamante

def test_reclamante_creation():
    reclamante = Reclamante(id=1, nome="João Silva", telefone="11999999999", documento="123.456.789-00")
    assert reclamante.id == 1
    assert reclamante.nome == "João Silva"
    assert reclamante.telefone == "11999999999"
    assert reclamante.documento == "123.456.789-00"

def test_reclamante_creation_sem_id():
    reclamante = Reclamante(nome="João Silva", telefone="11999999999", documento="123.456.789-00")
    assert reclamante.id is None
    assert reclamante.nome == "João Silva"
    assert reclamante.telefone == "11999999999"
    assert reclamante.documento == "123.456.789-00"
