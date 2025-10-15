import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from app.main import app
from fastapi import HTTPException
from app.Vacina.model import Vacina
from app.Vacina.routes import router

client = TestClient(app)

class TestVacinaRoutes:
    @patch('app.Vacina.routes.VacinaController.listar_todas')
    @patch('app.Vacina.routes.get_db')
    def test_listar_vacinas_vazio(self, mock_get_db, mock_listar):
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        mock_listar.return_value = []

        response = client.get("/vacinas/")

        assert response.status_code == 200
        assert response.json() == []

    @patch('app.Vacina.routes.VacinaController.listar_todas')
    @patch('app.Vacina.routes.get_db')
    def test_listar_vacinas_com_dados(self, mock_get_db, mock_listar):
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        vacinas_mock = [
            Vacina(id=1, nome="BCG", doses=1),
            Vacina(id=2, nome="COVID-19", doses=2)
        ]
        mock_listar.return_value = vacinas_mock

        response = client.get("/vacinas/")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["nome"] == "BCG"

    @patch('app.Vacina.routes.VacinaController.buscar_por_id')
    @patch('app.Vacina.routes.get_db')
    def test_buscar_vacina_encontrada(self, mock_get_db, mock_buscar):
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        mock_buscar.return_value = Vacina(
            id=1, nome="BCG", doses=1
        )

        response = client.get("/vacinas/1")

        assert response.status_code == 200
        data = response.json()
        assert data["nome"] == "BCG"

    @patch('app.Vacina.routes.VacinaController.buscar_por_id')
    @patch('app.Vacina.routes.get_db')
    def test_buscar_vacina_nao_encontrada(self, mock_get_db, mock_buscar):
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        mock_buscar.return_value = None

        response = client.get("/vacinas/999")

        assert response.status_code == 404
        assert "não encontrada" in response.json()["detail"]

    @patch('app.Vacina.routes.VacinaController.criar')
    @patch('app.Vacina.routes.get_db')
    def test_cadastrar_vacina_sucesso(self, mock_get_db, mock_criar):
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        mock_criar.return_value = Vacina(
            id=1, nome="BCG", doses=1
        )

        payload = {"nome": "BCG", "doses": 1}
        response = client.post("/vacinas/", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["nome"] == "BCG"
        assert data["doses"] == 1

    @patch('app.Vacina.routes.VacinaController.criar')
    @patch('app.Vacina.routes.get_db')
    def test_cadastrar_vacina_nome_duplicado(self, mock_get_db, mock_criar):
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        mock_criar.side_effect = HTTPException(
            status_code=400,
            detail="Vacina com nome 'BCG' já existe"
        )

        payload = {"nome": "BCG", "doses": 1}
        response = client.post("/vacinas/", json=payload)

        assert response.status_code == 400

    def test_cadastrar_vacina_dados_invalidos(self):
        # Nome vazio
        payload = {"nome": "", "doses": 1}
        response = client.post("/vacinas/", json=payload)
        assert response.status_code == 422

        # Doses zero
        payload = {"nome": "BCG", "doses": 0}
        response = client.post("/vacinas/", json=payload)
        assert response.status_code == 422

    @patch('app.Vacina.routes.VacinaController.atualizar')
    @patch('app.Vacina.routes.get_db')
    def test_atualizar_vacina_sucesso(self, mock_get_db, mock_atualizar):
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        mock_atualizar.return_value = Vacina(
            id=1, nome="BCG Atualizada", doses=2
        )

        payload = {"nome": "BCG Atualizada", "doses": 2}
        response = client.put("/vacinas/1", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["nome"] == "BCG Atualizada"

    @patch('app.Vacina.routes.VacinaController.atualizar')
    @patch('app.Vacina.routes.get_db')
    def test_atualizar_vacina_nao_encontrada(self, mock_get_db, mock_atualizar):
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        mock_atualizar.side_effect = HTTPException(
            status_code=404,
            detail="Vacina com ID 999 não encontrada"
        )

        payload = {"nome": "Teste", "doses": 1}
        response = client.put("/vacinas/999", json=payload)

        assert response.status_code == 404

    @patch('app.Vacina.routes.VacinaController.deletar')
    @patch('app.Vacina.routes.get_db')
    def test_deletar_vacina_sucesso(self, mock_get_db, mock_deletar):
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        mock_deletar.return_value = True

        response = client.delete("/vacinas/1")

        assert response.status_code == 204

    @patch('app.Vacina.routes.VacinaController.deletar')
    @patch('app.Vacina.routes.get_db')
    def test_deletar_vacina_nao_encontrada(self, mock_get_db, mock_deletar):
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        mock_deletar.side_effect = HTTPException(
            status_code=404,
            detail="Vacina com ID 999 não encontrada"
        )

        response = client.delete("/vacinas/999")

        assert response.status_code == 404

    @pytest.mark.parametrize("endpoint,method", [
        ("/vacinas/", "get"),
        ("/vacinas/1", "get"),
        ("/vacinas/", "post"),
        ("/vacinas/1", "put"),
        ("/vacinas/1", "delete"),
    ])
    def test_endpoints_existem(self, endpoint, method):
        routes = [route.path for route in app.routes]
        assert endpoint in routes or "/vacinas/{vacina_id}" in routes