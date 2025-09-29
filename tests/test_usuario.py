import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.mark.skip(reason="Integração com banco ainda não configurada")
def test_listar_usuarios():
    """Teste de integração chamando GET /usuarios"""
    response = client.get("/usuarios/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.skip(reason="Integração com banco ainda não configurada")
def test_adicionar_usuario():
    """Teste de integração chamando POST /usuarios"""
    novo_usuario = {"nome": "Rafael", "email": "rafael@email.com", "senha": "123456"}
    response = client.post("/usuarios/", json=novo_usuario)
    assert response.status_code == 201
    body = response.json()
    assert body["nome"] == "Rafael"
    assert body["email"] == "rafael@email.com"
