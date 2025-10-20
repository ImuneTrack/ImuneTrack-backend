import pytest
from datetime import datetime, date
from fastapi.testclient import TestClient
from app.main import app 
from app.database import get_db
from app.HistoricoVacina.model import StatusDose
from app.Vacina.model import Vacina
from app.Usuario.model import Usuario
from app.HistoricoVacina.model import HistoricoVacinal

# Exemplo de fixtures de usuário e vacina
@pytest.fixture
def criar_usuario(db_session):
    from app.Usuario.model import Usuario
    usuario = Usuario(nome="Test User", email="testuser@example.com", senha="senha_hashed")
    db_session.add(usuario)
    db_session.commit()
    db_session.refresh(usuario)
    return usuario

@pytest.fixture
def db_session():
    from app.database import SessionLocal, Base, engine
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

# Testes de integração para o histórico vacinal
@pytest.fixture
def criar_vacina(db_session):
    from app.Vacina.model import Vacina
    vacina = Vacina(nome="Vacina Teste", doses=3)
    db_session.add(vacina)
    db_session.commit()
    db_session.refresh(vacina)
    return vacina

@pytest.fixture(scope="module")
def client():
    """Fixture para fornecer um TestClient do FastAPI."""
    with TestClient(app) as c:
        yield c

# Teste de criação de histórico vacinal
def test_criar_historico(db_session):
    data_aplicacao = date.fromisoformat("2025-10-17")
    novo_historico = HistoricoVacinal(
        usuario_id=1,
        vacina_id=1,
        numero_dose=1,                   
        status=StatusDose.APLICADA,      
        data_aplicacao=data_aplicacao
    )
    db_session.add(novo_historico)
    db_session.commit()

    resultado = db_session.query(HistoricoVacinal).first()
    assert resultado is not None
    assert resultado.usuario_id == 1

# Teste de listagem de histórico vacinal
def test_listar_historico(client: TestClient, criar_usuario, criar_vacina, db_session):
    app.dependency_overrides[get_db] = lambda: db_session

    historico = HistoricoVacinal(
        usuario_id=criar_usuario.id,
        vacina_id=criar_vacina.id,
        numero_dose=1,
        status=StatusDose.PENDENTE,
        data_prevista=date.today()
    )
    db_session.add(historico)
    db_session.commit()
    db_session.refresh(historico)

    response = client.get(f"/usuarios/{criar_usuario.id}/historico/")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["usuario_id"] == criar_usuario.id
    assert data[0]["vacina_id"] == criar_vacina.id
    assert data[0]["numero_dose"] == 1
    assert data[0]["status"] == StatusDose.PENDENTE.value

# Teste de atualização de histórico vacinal
def test_atualizar_historico(client: TestClient, criar_usuario, criar_vacina, db_session):
    from app.HistoricoVacina.model import HistoricoVacinal
    historico = HistoricoVacinal(
        usuario_id=criar_usuario.id,
        vacina_id=criar_vacina.id,
        numero_dose=1,
        status=StatusDose.PENDENTE
    )
    db_session.add(historico)
    db_session.commit()
    db_session.refresh(historico)

    response = client.put(
        f"/usuarios/{criar_usuario.id}/historico/{historico.id}",
        json={"numero_dose": 2, "status": "aplicada"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["numero_dose"] == 2
    assert data["status"] == "aplicada"

# Teste de marcar dose como aplicada
def test_marcar_como_aplicada(client: TestClient, criar_usuario, criar_vacina, db_session):
    from app.HistoricoVacina.model import HistoricoVacinal
    historico = HistoricoVacinal(
        usuario_id=criar_usuario.id,
        vacina_id=criar_vacina.id,
        numero_dose=1,
        status=StatusDose.PENDENTE
    )
    db_session.add(historico)
    db_session.commit()
    db_session.refresh(historico)

    response = client.patch(
        f"/usuarios/{criar_usuario.id}/historico/{historico.id}/aplicar",
        params={"data_aplicacao": date.today().isoformat()}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "aplicada"
    assert data["data_aplicacao"] == date.today().isoformat()

# Teste de deleção de histórico vacinal
def test_deletar_historico(client: TestClient, criar_usuario, criar_vacina, db_session):
    from app.HistoricoVacina.model import HistoricoVacinal
    historico = HistoricoVacinal(
        usuario_id=criar_usuario.id,
        vacina_id=criar_vacina.id,
        numero_dose=1,
        status=StatusDose.PENDENTE
    )
    db_session.add(historico)
    db_session.commit()
    db_session.refresh(historico)

    response = client.delete(f"/usuarios/{criar_usuario.id}/historico/{historico.id}")
    assert response.status_code == 204

    resp_get = client.get(f"/usuarios/{criar_usuario.id}/historico/{historico.id}")
    assert resp_get.status_code == 404
