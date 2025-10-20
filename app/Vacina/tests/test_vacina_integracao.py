import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal, Base, engine

client = TestClient(app)


@pytest.fixture(scope="function", autouse=True)
def setup_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


class TestVacinaIntegration:

    def test_listar_vacinas_vazio(self):
        response = client.get("/vacinas/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert len(response.json()) == 0

    def test_adicionar_vacina_sucesso(self):
        nova_vacina = {"nome": "Hepatite B", "doses": 3}
        response = client.post("/vacinas/", json=nova_vacina)
        
        assert response.status_code == 201
        body = response.json()
        assert body["nome"] == "Hepatite B"
        assert body["doses"] == 3
        assert "id" in body
        assert body["id"] > 0

    def test_listar_vacinas_com_dados(self):
        client.post("/vacinas/", json={"nome": "BCG", "doses": 1})
        client.post("/vacinas/", json={"nome": "Hepatite B", "doses": 3})
        client.post("/vacinas/", json={"nome": "COVID-19", "doses": 2})
        
        response = client.get("/vacinas/")
        assert response.status_code == 200
        
        vacinas = response.json()
        assert len(vacinas) == 3
        assert any(v["nome"] == "BCG" for v in vacinas)
        assert any(v["nome"] == "Hepatite B" for v in vacinas)

    def test_buscar_vacina_por_id_sucesso(self):
        response_create = client.post("/vacinas/", json={"nome": "BCG", "doses": 1})
        vacina_id = response_create.json()["id"]
        
        response = client.get(f"/vacinas/{vacina_id}")
        assert response.status_code == 200
        
        vacina = response.json()
        assert vacina["id"] == vacina_id
        assert vacina["nome"] == "BCG"
        assert vacina["doses"] == 1

    def test_buscar_vacina_nao_encontrada(self):
        response = client.get("/vacinas/99999")
        assert response.status_code == 404
        assert "não encontrada" in response.json()["detail"].lower()

    def test_adicionar_vacina_nome_duplicado(self):
        client.post("/vacinas/", json={"nome": "BCG", "doses": 1})
        
        response = client.post("/vacinas/", json={"nome": "BCG", "doses": 2})
        assert response.status_code == 400
        assert "já existe" in response.json()["detail"].lower()

    def test_adicionar_vacina_dados_invalidos(self):
        response = client.post("/vacinas/", json={"nome": "", "doses": 1})
        assert response.status_code == 422
        
        response = client.post("/vacinas/", json={"nome": "Teste", "doses": 0})
        assert response.status_code == 422
        
        response = client.post("/vacinas/", json={"nome": "Teste", "doses": -1})
        assert response.status_code == 422
        
        response = client.post("/vacinas/", json={"nome": "Teste", "doses": 11})
        assert response.status_code == 422
        
        response = client.post("/vacinas/", json={"nome": "Teste"})
        assert response.status_code == 422

    def test_atualizar_vacina_sucesso(self):
        response_create = client.post("/vacinas/", json={"nome": "BCG", "doses": 1})
        vacina_id = response_create.json()["id"]
        
        response = client.put(
            f"/vacinas/{vacina_id}",
            json={"nome": "BCG Atualizada", "doses": 2}
        )
        assert response.status_code == 200
        
        vacina = response.json()
        assert vacina["nome"] == "BCG Atualizada"
        assert vacina["doses"] == 2

    def test_atualizar_vacina_parcial(self):
        response_create = client.post("/vacinas/", json={"nome": "BCG", "doses": 1})
        vacina_id = response_create.json()["id"]
        
        response = client.put(
            f"/vacinas/{vacina_id}",
            json={"nome": "BCG Nova"}
        )
        assert response.status_code == 200
        assert response.json()["nome"] == "BCG Nova"
        assert response.json()["doses"] == 1

    def test_atualizar_vacina_nao_encontrada(self):
        response = client.put(
            "/vacinas/99999",
            json={"nome": "Teste", "doses": 1}
        )
        assert response.status_code == 404

    def test_deletar_vacina_sucesso(self):
        response_create = client.post("/vacinas/", json={"nome": "BCG", "doses": 1})
        vacina_id = response_create.json()["id"]
        
        response = client.delete(f"/vacinas/{vacina_id}")
        assert response.status_code == 204
        
        response_get = client.get(f"/vacinas/{vacina_id}")
        assert response_get.status_code == 404

    def test_deletar_vacina_nao_encontrada(self):
        response = client.delete("/vacinas/99999")
        assert response.status_code == 404

    def test_fluxo_completo_crud(self):
        response = client.get("/vacinas/")
        assert len(response.json()) == 0
        
        response = client.post("/vacinas/", json={"nome": "COVID-19", "doses": 2})
        assert response.status_code == 201
        vacina_id = response.json()["id"]
        
        response = client.get("/vacinas/")
        assert len(response.json()) == 1
        
        response = client.get(f"/vacinas/{vacina_id}")
        assert response.status_code == 200
        assert response.json()["nome"] == "COVID-19"
        
        response = client.put(
            f"/vacinas/{vacina_id}",
            json={"nome": "COVID-19 Pfizer", "doses": 3}
        )
        assert response.status_code == 200
        assert response.json()["doses"] == 3
        
        response = client.delete(f"/vacinas/{vacina_id}")
        assert response.status_code == 204
        
        response = client.get("/vacinas/")
        assert len(response.json()) == 0

    @pytest.mark.parametrize("nome,doses,esperado", [
        ("BCG", 1, 201),
        ("Hepatite B", 3, 201),
        ("Tríplice Viral", 2, 201),
        ("Febre Amarela", 1, 201),
    ])
    def test_adicionar_vacinas_validas(self, nome, doses, esperado):
        response = client.post("/vacinas/", json={"nome": nome, "doses": doses})
        assert response.status_code == esperado
        assert response.json()["nome"] == nome
        assert response.json()["doses"] == doses

    def test_persistencia_entre_requisicoes(self):
        client.post("/vacinas/", json={"nome": "BCG", "doses": 1})
        client.post("/vacinas/", json={"nome": "Hepatite B", "doses": 3})
        client.post("/vacinas/", json={"nome": "COVID-19", "doses": 2})
        
        for _ in range(3):
            response = client.get("/vacinas/")
            assert response.status_code == 200
            assert len(response.json()) == 3

    def test_validacao_nome_espacos(self):
        response = client.post("/vacinas/", json={"nome": "  BCG  ", "doses": 1})
        assert response.status_code == 201
        assert response.json()["nome"].strip() == "BCG"

    def test_atualizar_vacina_nome_duplicado(self):
        client.post("/vacinas/", json={"nome": "BCG", "doses": 1})
        response_create = client.post("/vacinas/", json={"nome": "Hepatite B", "doses": 3})
        vacina_id = response_create.json()["id"]
        
        response = client.put(
            f"/vacinas/{vacina_id}",
            json={"nome": "BCG"}
        )
        assert response.status_code == 400
        assert "já existe" in response.json()["detail"].lower()

    def test_response_structure(self):
        response = client.post("/vacinas/", json={"nome": "BCG", "doses": 1})
        data = response.json()
        
        assert "id" in data
        assert "nome" in data
        assert "doses" in data
        assert isinstance(data["id"], int)
        assert isinstance(data["nome"], str)
        assert isinstance(data["doses"], int)

    def test_multiplas_vacinas_mesma_dose(self):
        client.post("/vacinas/", json={"nome": "BCG", "doses": 1})
        client.post("/vacinas/", json={"nome": "Febre Amarela", "doses": 1})
        
        response = client.get("/vacinas/")
        vacinas = response.json()
        vacinas_dose_1 = [v for v in vacinas if v["doses"] == 1]
        assert len(vacinas_dose_1) == 2

    def test_ordem_listagem(self):
        client.post("/vacinas/", json={"nome": "COVID-19", "doses": 2})
        client.post("/vacinas/", json={"nome": "BCG", "doses": 1})
        client.post("/vacinas/", json={"nome": "Hepatite B", "doses": 3})
        
        response = client.get("/vacinas/")
        vacinas = response.json()
        assert len(vacinas) == 3
        assert all(isinstance(v["id"], int) for v in vacinas)

    def test_atualizar_apenas_nome(self):
        response_create = client.post("/vacinas/", json={"nome": "BCG", "doses": 1})
        vacina_id = response_create.json()["id"]
        
        response = client.put(
            f"/vacinas/{vacina_id}",
            json={"nome": "BCG Atualizada"}
        )
        assert response.status_code == 200
        assert response.json()["nome"] == "BCG Atualizada"
        assert response.json()["doses"] == 1

    def test_atualizar_apenas_doses(self):
        response_create = client.post("/vacinas/", json={"nome": "BCG", "doses": 1})
        vacina_id = response_create.json()["id"]
        
        response = client.put(
            f"/vacinas/{vacina_id}",
            json={"doses": 3}
        )
        assert response.status_code == 200
        assert response.json()["nome"] == "BCG"
        assert response.json()["doses"] == 3

    def test_criar_e_buscar_imediatamente(self):
        response_create = client.post("/vacinas/", json={"nome": "BCG", "doses": 1})
        vacina_id = response_create.json()["id"]
        
        response_get = client.get(f"/vacinas/{vacina_id}")
        assert response_get.status_code == 200
        assert response_get.json()["id"] == vacina_id
        assert response_get.json()["nome"] == "BCG"

    def test_deletar_e_verificar_lista(self):
        response1 = client.post("/vacinas/", json={"nome": "BCG", "doses": 1})
        response2 = client.post("/vacinas/", json={"nome": "Hepatite B", "doses": 3})
        
        vacina_id = response1.json()["id"]
        client.delete(f"/vacinas/{vacina_id}")
        
        response = client.get("/vacinas/")
        vacinas = response.json()
        assert len(vacinas) == 1
        assert vacinas[0]["nome"] == "Hepatite B"

    @pytest.mark.parametrize("doses_invalidas", [0, -1, -5, 11, 20, 100])
    def test_doses_invalidas_parametrizado(self, doses_invalidas):
        response = client.post("/vacinas/", json={"nome": "Teste", "doses": doses_invalidas})
        assert response.status_code == 422

    def test_limites_doses_validas(self):
        response_min = client.post("/vacinas/", json={"nome": "Dose Mínima", "doses": 1})
        assert response_min.status_code == 201
        
        response_max = client.post("/vacinas/", json={"nome": "Dose Máxima", "doses": 10})
        assert response_max.status_code == 201

    def test_nome_muito_longo(self):
        nome_longo = "A" * 101
        response = client.post("/vacinas/", json={"nome": nome_longo, "doses": 1})
        assert response.status_code == 422