import pytest
from unittest.mock import Mock, patch
from fastapi import HTTPException, status
from app.Usuario.controller import UsuarioController
from app.Usuario.model import Usuario


class TestUsuarioController:
    """Testes unitários do UsuarioController."""

    def test_listar_todos_vazio(self):
        """Deve retornar lista vazia quando não há usuários."""
        db_mock = Mock()
        db_mock.query.return_value.all.return_value = []

        resultado = UsuarioController.listar_todos(db_mock)

        assert resultado == []
        assert isinstance(resultado, list)

    def test_listar_todos_com_dados(self):
        """Deve retornar todos os usuários cadastrados."""
        db_mock = Mock()
        usuarios_mock = [
            Usuario(id=1, nome="Alice", email="alice@test.com", senha="hash1"),
            Usuario(id=2, nome="Bob", email="bob@test.com", senha="hash2"),
        ]
        db_mock.query.return_value.all.return_value = usuarios_mock

        resultado = UsuarioController.listar_todos(db_mock)

        assert len(resultado) == 2
        assert resultado[0].nome == "Alice"
        assert resultado[1].email == "bob@test.com"

    def test_buscar_por_id_encontrado(self):
        """Deve retornar usuário quando ID existe."""
        db_mock = Mock()
        usuario_mock = Usuario(id=1, nome="Alice", email="alice@test.com", senha="hash")
        db_mock.query.return_value.filter.return_value.first.return_value = usuario_mock

        resultado = UsuarioController.buscar_por_id(db_mock, 1)

        assert resultado is not None
        assert resultado.nome == "Alice"

    def test_buscar_por_id_nao_encontrado(self):
        """Deve retornar None quando ID não existe."""
        db_mock = Mock()
        db_mock.query.return_value.filter.return_value.first.return_value = None

        resultado = UsuarioController.buscar_por_id(db_mock, 999)

        assert resultado is None

    def test_buscar_por_email_encontrado(self):
        """Deve retornar usuário quando email existe."""
        db_mock = Mock()
        usuario_mock = Usuario(id=1, nome="Alice", email="alice@test.com", senha="hash")
        db_mock.query.return_value.filter.return_value.first.return_value = usuario_mock

        resultado = UsuarioController.buscar_por_email(db_mock, "alice@test.com")

        assert resultado is not None
        assert resultado.email == "alice@test.com"

    @patch.object(UsuarioController, '_hash_senha', return_value='hashed_password')
    def test_criar_usuario_sucesso(self, mock_hash):
        """Deve criar usuário com sucesso."""
        db_mock = Mock()
        db_mock.query.return_value.filter.return_value.first.return_value = None

        resultado = UsuarioController.criar(
            db_mock, "Alice", "alice@test.com", "senha123"
        )

        assert resultado.nome == "Alice"
        assert resultado.email == "alice@test.com"
        assert resultado.senha == "hashed_password"
        db_mock.add.assert_called_once()
        db_mock.commit.assert_called_once()

    def test_criar_usuario_email_duplicado(self):
        """Deve lançar exceção ao criar usuário com email duplicado."""
        db_mock = Mock()
        usuario_existente = Usuario(id=1, nome="Alice", email="alice@test.com", senha="hash")
        db_mock.query.return_value.filter.return_value.first.return_value = usuario_existente

        with pytest.raises(HTTPException) as exc_info:
            UsuarioController.criar(db_mock, "Bob", "alice@test.com", "senha123")

        assert exc_info.value.status_code == 400
        assert "já existe" in exc_info.value.detail

    def test_criar_usuario_nome_vazio(self):
        """Deve lançar exceção ao criar usuário com nome vazio."""
        db_mock = Mock()

        with pytest.raises(HTTPException) as exc_info:
            UsuarioController.criar(db_mock, "", "test@test.com", "senha123")

        assert exc_info.value.status_code == 400
        assert "obrigatório" in exc_info.value.detail

    def test_criar_usuario_email_invalido(self):
        """Deve lançar exceção ao criar usuário com email inválido."""
        db_mock = Mock()

        with pytest.raises(HTTPException) as exc_info:
            UsuarioController.criar(db_mock, "Alice", "email_invalido", "senha123")

        assert exc_info.value.status_code == 400
        assert "inválido" in exc_info.value.detail

    def test_criar_usuario_senha_curta(self):
        """Deve lançar exceção ao criar usuário com senha curta."""
        db_mock = Mock()

        with pytest.raises(HTTPException) as exc_info:
            UsuarioController.criar(db_mock, "Alice", "alice@test.com", "123")

        assert exc_info.value.status_code == 400
        assert "mínimo 6" in exc_info.value.detail

    @patch.object(UsuarioController, '_hash_senha', return_value='new_hashed')
    def test_atualizar_usuario_sucesso(self, mock_hash):
        """Deve atualizar usuário com sucesso."""
        db_mock = Mock()
        usuario_mock = Usuario(id=1, nome="Alice", email="alice@test.com", senha="hash")
        db_mock.query.return_value.filter.return_value.first.return_value = usuario_mock

        resultado = UsuarioController.atualizar(
            db_mock, 1, nome="Alice Silva", senha="nova_senha"
        )

        assert resultado.nome == "Alice Silva"
        assert resultado.senha == "new_hashed"
        db_mock.commit.assert_called_once()

    def test_atualizar_usuario_nao_encontrado(self):
        """Deve lançar exceção ao atualizar usuário inexistente."""
        db_mock = Mock()
        db_mock.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            UsuarioController.atualizar(db_mock, 999, nome="Teste")

        assert exc_info.value.status_code == 404

    def test_deletar_usuario_sucesso(self):
        """Deve deletar usuário com sucesso."""
        db_mock = Mock()
        usuario_mock = Usuario(id=1, nome="Alice", email="alice@test.com", senha="hash")
        db_mock.query.return_value.filter.return_value.first.return_value = usuario_mock

        resultado = UsuarioController.deletar(db_mock, 1)

        assert resultado is True
        db_mock.delete.assert_called_once()
        db_mock.commit.assert_called_once()

    def test_deletar_usuario_nao_encontrado(self):
        """Deve lançar exceção ao deletar usuário inexistente."""
        db_mock = Mock()
        db_mock.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            UsuarioController.deletar(db_mock, 999)

        assert exc_info.value.status_code == 404

    @patch.object(UsuarioController, '_verificar_senha', return_value=True)
    def test_autenticar_sucesso(self, mock_verif):
        """Deve autenticar usuário com credenciais corretas."""
        db_mock = Mock()
        usuario_mock = Usuario(id=1, nome="Alice", email="alice@test.com", senha="hash")
        db_mock.query.return_value.filter.return_value.first.return_value = usuario_mock

        resultado = UsuarioController.autenticar(db_mock, "alice@test.com", "senha123")

        assert resultado is not None
        assert resultado.email == "alice@test.com"

    @patch.object(UsuarioController, '_verificar_senha', return_value=False)
    def test_autenticar_senha_incorreta(self, mock_verif):
        """Deve retornar None com senha incorreta."""
        db_mock = Mock()
        usuario_mock = Usuario(id=1, nome="Alice", email="alice@test.com", senha="hash")
        db_mock.query.return_value.filter.return_value.first.return_value = usuario_mock

        resultado = UsuarioController.autenticar(db_mock, "alice@test.com", "senha_errada")

        assert resultado is None

    def test_autenticar_email_nao_encontrado(self):
        """Deve retornar None quando email não existe."""
        db_mock = Mock()
        db_mock.query.return_value.filter.return_value.first.return_value = None

        resultado = UsuarioController.autenticar(db_mock, "naoexiste@test.com", "senha")

        assert resultado is None

    @pytest.mark.parametrize("email,valido", [
        ("alice@test.com", True),
        ("bob.silva@empresa.com.br", True),
        ("user+tag@domain.co", True),
        ("invalid.email", False),
        ("@domain.com", False),
        ("user@", False),
        ("", False),
    ])
    def test_validar_email(self, email, valido):
        """Testa validação de diferentes formatos de email."""
        resultado = UsuarioController._validar_email(email)
        assert resultado == valido

    @pytest.mark.parametrize("senha,valido", [
        ("senha123", True),
        ("123456", True),
        ("senhaforte123", True),
        ("12345", False),
        ("abc", False),
        ("", False),
    ])
    def test_validar_senha(self, senha, valido):
        """Testa validação de diferentes senhas."""
        resultado = UsuarioController._validar_senha(senha)
        assert resultado == valido