import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.mark.skip(reason="Integração com banco ainda não configurada")
def test_listar_vacinas():
    """Teste de integração chamando GET /vacinas"""
    response = client.get("/vacinas/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.skip(reason="Integração com banco ainda não configurada")
def test_adicionar_vacina():
    """Teste de integração chamando POST /vacinas"""
    nova_vacina = {"nome": "Hepatite B", "doses": 3}
    response = client.post("/vacinas/", json=nova_vacina)
    assert response.status_code == 201
    body = response.json()
    assert body["nome"] == "Hepatite B"
    assert body["doses"] == 3
