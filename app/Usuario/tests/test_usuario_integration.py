import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal, Base, engine
from app.Usuario.model import Usuario

client = TestClient(app)


@pytest.fixture(scope="function", autouse=True)
def setup_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module", autouse=True)
def setup_module_db():
    db = SessionLocal()
    db.query(Usuario).delete()
    db.commit()
    db.close()

class TestUsuarioIntegration:

    def test_listar_usuarios_vazio(self):
        response = client.get("/usuarios/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert len(response.json()) == 0

    def test_senha_limite_72_caracteres(self):
        senha_72 = "a1" * 36  # Exatamente 72 caracteres
        response = client.post("/usuarios/", json={
            "nome": "Teste",
            "email": "teste@teste.com",
            "senha": senha_72
        })
        assert response.status_code == 201

    def test_senha_maior_que_72_recusada(self):
        senha_73 = "a1" * 36 + "x"  # 73 caracteres
        response = client.post("/usuarios/", json={
            "nome": "Teste",
            "email": "teste@teste.com",
            "senha": senha_73
        })
        assert response.status_code == 422

    def test_adicionar_usuario_sucesso(self):
        novo_usuario = {
            "nome": "Alice Silva",
            "email": "alice@teste.com",
            "senha": "senha123"
        }
        print("DEBUG: senha enviada pelo teste:", novo_usuario["senha"])

        response = client.post("/usuarios/", json=novo_usuario)
        print("DEBUG: resposta do endpoint:", response.json())

        assert response.status_code == 201

    def test_listar_usuarios_com_dados(self):
        client.post("/usuarios/", json={"nome": "Alice", "email": "alice@teste.com", "senha": "senha123"})
        client.post("/usuarios/", json={"nome": "Bob", "email": "bob@teste.com", "senha": "senha456"})
        client.post("/usuarios/", json={"nome": "Carlos", "email": "carlos@teste.com", "senha": "senha789"})
        
        response = client.get("/usuarios/")
        assert response.status_code == 200
        
        usuarios = response.json()
        assert len(usuarios) == 3
        assert any(u["nome"] == "Alice" for u in usuarios)
        assert any(u["email"] == "bob@teste.com" for u in usuarios)

    def test_buscar_usuario_por_id_sucesso(self):
        response_create = client.post("/usuarios/", json={
            "nome": "Alice",
            "email": "alice@teste.com",
            "senha": "senha123"
        })
        usuario_id = response_create.json()["id"]
        
        response = client.get(f"/usuarios/{usuario_id}")
        assert response.status_code == 200
        
        usuario = response.json()
        assert usuario["id"] == usuario_id
        assert usuario["nome"] == "Alice"
        assert usuario["email"] == "alice@teste.com"
        assert "senha" not in usuario

    def test_buscar_usuario_nao_encontrado(self):
        response = client.get("/usuarios/99999")
        assert response.status_code == 404
        assert "não encontrado" in response.json()["detail"].lower()

    def test_adicionar_usuario_email_duplicado(self):
        client.post("/usuarios/", json={
            "nome": "Alice",
            "email": "alice@teste.com",
            "senha": "senha123"
        })
        
        response = client.post("/usuarios/", json={
            "nome": "Bob",
            "email": "alice@teste.com",
            "senha": "senha456"
        })
        assert response.status_code == 400
        assert "já existe" in response.json()["detail"].lower()

    def test_adicionar_usuario_dados_invalidos(self):
        response = client.post("/usuarios/", json={
            "nome": "Alice",
            "email": "email_invalido",
            "senha": "senha123"
        })
        assert response.status_code == 422
        
        response = client.post("/usuarios/", json={
            "nome": "Alice",
            "email": "alice@teste.com",
            "senha": "123"
        })
        assert response.status_code == 422
        
        response = client.post("/usuarios/", json={
            "nome": "",
            "email": "alice@teste.com",
            "senha": "senha123"
        })
        assert response.status_code == 422
        
        response = client.post("/usuarios/", json={
            "nome": "Alice",
            "senha": "senha123"
        })
        assert response.status_code == 422

    def test_atualizar_usuario_sucesso(self):
        response_create = client.post("/usuarios/", json={
            "nome": "Alice",
            "email": "alice@teste.com",
            "senha": "senha123"
        })
        usuario_id = response_create.json()["id"]
        
        response = client.put(
            f"/usuarios/{usuario_id}",
            json={"nome": "Alice Silva", "email": "alice.silva@teste.com", "senha": "novasenha123"}
        )
        assert response.status_code == 200
        
        usuario = response.json()
        assert usuario["nome"] == "Alice Silva"
        assert usuario["email"] == "alice.silva@teste.com"
        assert "senha" not in usuario

    def test_atualizar_usuario_parcial(self):
        response_create = client.post("/usuarios/", json={
            "nome": "Alice",
            "email": "alice@teste.com",
            "senha": "senha123"
        })
        usuario_id = response_create.json()["id"]
        
        response = client.put(
            f"/usuarios/{usuario_id}",
            json={"nome": "Alice Silva"}
        )
        assert response.status_code == 200
        assert response.json()["nome"] == "Alice Silva"
        assert response.json()["email"] == "alice@teste.com"

    def test_atualizar_usuario_nao_encontrado(self):
        response = client.put(
            "/usuarios/99999",
            json={"nome": "Teste"}
        )
        assert response.status_code == 404

    def test_deletar_usuario_sucesso(self):
        response_create = client.post("/usuarios/", json={
            "nome": "Alice",
            "email": "alice@teste.com",
            "senha": "senha123"
        })
        usuario_id = response_create.json()["id"]
        
        response = client.delete(f"/usuarios/{usuario_id}")
        assert response.status_code == 204
        
        response_get = client.get(f"/usuarios/{usuario_id}")
        assert response_get.status_code == 404

    def test_deletar_usuario_nao_encontrado(self):
        response = client.delete("/usuarios/99999")
        assert response.status_code == 404

    def test_login_sucesso(self):
        client.post("/usuarios/", json={
            "nome": "Alice",
            "email": "alice@teste.com",
            "senha": "senha123"
        })
        
        response = client.post(
            "/usuarios/login?email=alice@teste.com&senha=senha123"
        )
        assert response.status_code == 200
        
        usuario = response.json()
        assert usuario["email"] == "alice@teste.com"
        assert "senha" not in usuario

    def test_login_credenciais_invalidas(self):
        client.post("/usuarios/", json={
            "nome": "Alice",
            "email": "alice@teste.com",
            "senha": "senha123"
        })
        
        response = client.post(
            "/usuarios/login?email=alice@teste.com&senha=senha_errada"
        )
        assert response.status_code == 401
        assert "incorretos" in response.json()["detail"].lower()

    def test_login_usuario_inexistente(self):
        response = client.post(
            "/usuarios/login?email=naoexiste@teste.com&senha=senha123"
        )
        assert response.status_code == 401

    def test_fluxo_completo_crud(self):
        response = client.get("/usuarios/")
        assert len(response.json()) == 0
        
        response = client.post("/usuarios/", json={
            "nome": "Alice",
            "email": "alice@teste.com",
            "senha": "senha123"
        })
        assert response.status_code == 201
        usuario_id = response.json()["id"]
        
        response = client.get("/usuarios/")
        assert len(response.json()) == 1
        
        response = client.get(f"/usuarios/{usuario_id}")
        assert response.status_code == 200
        assert response.json()["nome"] == "Alice"
        
        response = client.put(
            f"/usuarios/{usuario_id}",
            json={"nome": "Alice Silva", "email": "alice.silva@teste.com"}
        )
        assert response.status_code == 200
        assert response.json()["nome"] == "Alice Silva"
        
        response = client.post(
            f"/usuarios/login?email=alice.silva@teste.com&senha=senha123"
        )
        assert response.status_code == 200
        
        response = client.delete(f"/usuarios/{usuario_id}")
        assert response.status_code == 204
        
        response = client.get("/usuarios/")
        assert len(response.json()) == 0

    @pytest.mark.parametrize("nome,email,senha,esperado", [
        ("Alice", "alice@teste.com", "senha123", 201),
        ("Bob Silva", "bob.silva@empresa.com.br", "senha456", 201),
        ("Carlos", "carlos+tag@domain.co", "senha789", 201),
    ])
    def test_adicionar_usuarios_validos(self, nome, email, senha, esperado):
        response = client.post("/usuarios/", json={
            "nome": nome,
            "email": email,
            "senha": senha
        })
        assert response.status_code == esperado
        assert response.json()["nome"] == nome
        assert response.json()["email"] == email.lower()

    def test_persistencia_entre_requisicoes(self):
        client.post("/usuarios/", json={"nome": "Alice", "email": "alice@teste.com", "senha": "senha123"})
        client.post("/usuarios/", json={"nome": "Bob", "email": "bob@teste.com", "senha": "senha456"})
        client.post("/usuarios/", json={"nome": "Carlos", "email": "carlos@teste.com", "senha": "senha789"})
        
        for _ in range(3):
            response = client.get("/usuarios/")
            assert response.status_code == 200
            assert len(response.json()) == 3

    def test_email_case_insensitive(self):
        client.post("/usuarios/", json={
            "nome": "Alice",
            "email": "Alice@Teste.COM",
            "senha": "senha123"
        })
        
        response = client.post(
            "/usuarios/login?email=alice@teste.com&senha=senha123"
        )
        assert response.status_code == 200

    def test_senha_hasheada(self):
        response = client.post("/usuarios/", json={
            "nome": "Alice",
            "email": "alice@teste.com",
            "senha": "senha123"
        })
        
        usuario = response.json()
        assert "senha" not in usuario
        
        response_login = client.post(
            "/usuarios/login?email=alice@teste.com&senha=senha123"
        )
        assert response_login.status_code == 200

    def test_validacao_nome_espacos(self):
        response = client.post("/usuarios/", json={
            "nome": "  Alice Silva  ",
            "email": "alice@teste.com",
            "senha": "senha123"
        })
        assert response.status_code == 201
        assert response.json()["nome"].strip() == "Alice Silva"

    def test_atualizar_email_duplicado(self):
        client.post("/usuarios/", json={
            "nome": "Alice",
            "email": "alice@teste.com",
            "senha": "senha123"
        })
        
        response_create = client.post("/usuarios/", json={
            "nome": "Bob",
            "email": "bob@teste.com",
            "senha": "senha456"
        })
        bob_id = response_create.json()["id"]
        
        response = client.put(
            f"/usuarios/{bob_id}",
            json={"email": "alice@teste.com"}
        )
        assert response.status_code == 400
        assert "já está em uso" in response.json()["detail"].lower()

    def test_response_structure(self):
        response = client.post("/usuarios/", json={
            "nome": "Alice",
            "email": "alice@teste.com",
            "senha": "senha123"
        })
        data = response.json()
        
        assert "id" in data
        assert "nome" in data
        assert "email" in data
        assert "senha" not in data
        assert isinstance(data["id"], int)
        assert isinstance(data["nome"], str)
        assert isinstance(data["email"], str)

    def test_atualizar_apenas_nome(self):
        response_create = client.post("/usuarios/", json={
            "nome": "Alice",
            "email": "alice@teste.com",
            "senha": "senha123"
        })
        usuario_id = response_create.json()["id"]
        
        response = client.put(
            f"/usuarios/{usuario_id}",
            json={"nome": "Alice Silva"}
        )
        assert response.status_code == 200
        assert response.json()["nome"] == "Alice Silva"
        assert response.json()["email"] == "alice@teste.com"

    def test_atualizar_apenas_email(self):
        response_create = client.post("/usuarios/", json={
            "nome": "Alice",
            "email": "alice@teste.com",
            "senha": "senha123"
        })
        usuario_id = response_create.json()["id"]
        
        response = client.put(
            f"/usuarios/{usuario_id}",
            json={"email": "alice.nova@teste.com"}
        )
        assert response.status_code == 200
        assert response.json()["nome"] == "Alice"
        assert response.json()["email"] == "alice.nova@teste.com"

    def test_atualizar_apenas_senha(self):
        response_create = client.post("/usuarios/", json={
            "nome": "Alice",
            "email": "alice@teste.com",
            "senha": "senha123"
        })
        usuario_id = response_create.json()["id"]
        
        response = client.put(
            f"/usuarios/{usuario_id}",
            json={"senha": "novasenha456"}
        )
        assert response.status_code == 200
        
        response_login = client.post(
            "/usuarios/login?email=alice@teste.com&senha=novasenha456"
        )
        assert response_login.status_code == 200

    def test_criar_e_buscar_imediatamente(self):
        response_create = client.post("/usuarios/", json={
            "nome": "Alice",
            "email": "alice@teste.com",
            "senha": "senha123"
        })
        usuario_id = response_create.json()["id"]
        
        response_get = client.get(f"/usuarios/{usuario_id}")
        assert response_get.status_code == 200
        assert response_get.json()["id"] == usuario_id
        assert response_get.json()["nome"] == "Alice"

    def test_deletar_e_verificar_lista(self):
        response1 = client.post("/usuarios/", json={
            "nome": "Alice",
            "email": "alice@teste.com",
            "senha": "senha123"
        })
        response2 = client.post("/usuarios/", json={
            "nome": "Bob",
            "email": "bob@teste.com",
            "senha": "senha456"
        })
        
        usuario_id = response1.json()["id"]
        client.delete(f"/usuarios/{usuario_id}")
        
        response = client.get("/usuarios/")
        usuarios = response.json()
        assert len(usuarios) == 1
        assert usuarios[0]["nome"] == "Bob"

    @pytest.mark.parametrize("email_invalido", [
        "email_sem_arroba",
        "@semdominio.com",
        "usuario@",
        "usuario @dominio.com",
        "",
    ])
    def test_emails_invalidos_parametrizado(self, email_invalido):
        response = client.post("/usuarios/", json={
            "nome": "Teste",
            "email": email_invalido,
            "senha": "senha123"
        })
        assert response.status_code == 422

    @pytest.mark.parametrize("senha_invalida", ["", "12345", "abc", "a", "12"])
    def test_senhas_invalidas_parametrizado(self, senha_invalida):
        response = client.post("/usuarios/", json={
            "nome": "Teste",
            "email": "teste@teste.com",
            "senha": senha_invalida
        })
        assert response.status_code == 422

    def test_login_apos_atualizar_senha(self):
        response_create = client.post("/usuarios/", json={
            "nome": "Alice",
            "email": "alice@teste.com",
            "senha": "senha123"
        })
        usuario_id = response_create.json()["id"]
        
        response_login_antiga = client.post(
            "/usuarios/login?email=alice@teste.com&senha=senha123"
        )
        assert response_login_antiga.status_code == 200
        
        client.put(
            f"/usuarios/{usuario_id}",
            json={"senha": "novasenha456"}
        )
        
        response_login_antiga2 = client.post(
            "/usuarios/login?email=alice@teste.com&senha=senha123"
        )
        assert response_login_antiga2.status_code == 401
        
        response_login_nova = client.post(
            "/usuarios/login?email=alice@teste.com&senha=novasenha456"
        )
        assert response_login_nova.status_code == 200

    def test_email_lowercase_automatico(self):
        response = client.post("/usuarios/", json={
            "nome": "Alice",
            "email": "ALICE@TESTE.COM",
            "senha": "senha123"
        })
        assert response.status_code == 201
        assert response.json()["email"] == "alice@teste.com"

    def test_multiplos_usuarios_mesmo_nome(self):
        client.post("/usuarios/", json={
            "nome": "Alice",
            "email": "alice1@teste.com",
            "senha": "senha123"
        })
        response = client.post("/usuarios/", json={
            "nome": "Alice",
            "email": "alice2@teste.com",
            "senha": "senha456"
        })
        assert response.status_code == 201

    def test_nome_muito_longo(self):
        nome_longo = "A" * 101
        response = client.post("/usuarios/", json={
            "nome": nome_longo,
            "email": "teste@teste.com",
            "senha": "senha123"
        })
        assert response.status_code == 422

    def test_email_muito_longo(self):
        email_longo = "a" * 250 + "@teste.com"
        response = client.post("/usuarios/", json={
            "nome": "Teste",
            "email": email_longo,
            "senha": "senha123"
        })
        assert response.status_code == 422